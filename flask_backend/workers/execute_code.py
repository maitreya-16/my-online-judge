import os
# import shutil
# import time
import subprocess
import logging
import re
import base64
import redis
r = redis.StrictRedis(host='localhost',db=1, port=6379, decode_responses=True)
base_dir = os.getcwd()

LANGUAGE_CONFIG = {
    "python": {
        "extension": ".py",
        "image": "python:3.9-alpine",
        "run_command": "python {filename}",
        "timeout": 5,
        "memory_limit": 256, #MB
    },
    "cpp": {
        "extension": ".cpp",
        "image": "gcc:latest",
        "compile_cmd": "g++ {filename} -o {exec_name}",
        "run_command": "./{exec_name}",
        "timeout": 3,
        "memory_limit": 256,  # MB
    },
    "java": {
        "extension": ".java",
        "image": "openjdk:21-jdk",
        "compile_cmd": "javac {filename}",
        "run_command": "java {classname}",
        "timeout": 5,
        "memory_limit": 256,  # MB
    }
}

def decode(encoded_code):
    return base64.b64decode(encoded_code).decode('utf-8')

def validate_and_configure(language):
    if language not in LANGUAGE_CONFIG:
        return None, {"status": "failed", "message": "Unsupported Programming Language"}
    
    return LANGUAGE_CONFIG[language],None

def find_classname(code):

    match = re.search(r"public\s+class\s+(\w+)", code)
    if match:
        return match.group(1)
    else:
        raise ValueError("No public class found in Java code.") #he check kar error testing veles


def prepare_submission_directory(submission_id):
    work_dir = os.path.join(os.getcwd(),"submissions",f"submission_{submission_id}")
    os.makedirs(work_dir,exist_ok=True)
    os.makedirs(os.path.join(work_dir, "inputs"), exist_ok=True)
    return work_dir

def get_cached_testcases(problem_id):
    count = int(r.get(f"problem_{problem_id}/count"))
    test_input = []
    expected_output = []

    for i in range(count):
        test_input.append(r.get(f"problem_{problem_id}/input_{i}"))
        expected_output.append(r.get(f"problem_{problem_id}/output_{i}"))  
    return test_input, expected_output 

def compile_code(work_dir,filename,exec_name,language):
    if language not in ["cpp","java"]:
        return {"status":"success"}

    config = LANGUAGE_CONFIG[language]
    #java
    if language=='java':
        compile_cmd =  config["compile_cmd"].format(filename=filename)
    else:
        compile_cmd = config["compile_cmd"].format(filename=filename,exec_name=exec_name)

    try:
        subprocess.run(compile_cmd,shell=True,check=True,cwd=work_dir,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        return {"status":"success"}
    
    except subprocess.CalledProcessError as e:

        logging.error(f"Compilation failed for {language}: {e.stderr.decode().strip()}")
        return {"status": "compilation_error", "message": e.stderr.decode().strip()}


def execute_code_in_docker(submission_id, work_dir,run_cmd, input_file, image, timeout, memory_limit):

    work_dir = os.path.join(base_dir, "submissions", f"submission_{submission_id}")
    input_file_rel = os.path.relpath(input_file, work_dir)
    container_name = f"submission_{submission_id}_runner"

    docker_cmd = [
        "docker", "run", "--rm",
        "--name", container_name,
        "-v", f"{work_dir}:/app",
        "-w", "/app",
        image, "sh", "-c",
        f"{run_cmd} < {input_file_rel}"
    ]

    try:

        # Run the docker command
        result = subprocess.run(
            docker_cmd,
            stdout=subprocess.PIPE,  # capture standard output
            stderr=subprocess.PIPE,  # capture errors
            text=True,               # stringify the output
            check=True               # error raise karega
        )

        # logging.info("result in docker : ",result)

        return {"status": "success", "user_output": result.stdout.strip()}

    except subprocess.CalledProcessError as e:

        return {"status": "runtime_error", "message": e.stderr.strip()}
    


def run_code(submission_id , problem_id , code , language ,inputData=None):
    
    try:
        code = decode(code)
        inputData=decode(inputData)
        
        if not isinstance(problem_id,str):
            problem_id=str(problem_id)

        
        work_dir = prepare_submission_directory(submission_id)

        
        input_file_path = os.path.join(work_dir,"inputs","custom_input.txt")

        with open(input_file_path,"w") as f:
            f.write(inputData)


        config,error= validate_and_configure(language)

        if error:
            return {"status":error["status"],"message":error["message"]}
        

        if language== 'java':
            classname = find_classname(code)
            filename = f"{classname}{config['extension']}"
            exec_name=classname
        else:
            filename = f"{submission_id}{config['extension']}"
            exec_name = f"{submission_id}_exec"

        #writing code the file 
        code_file_path = os.path.join(work_dir,filename)
        with open (code_file_path,"w") as f :
            f.write(code)

        #compiling ^_^
        compile_result  = compile_code(work_dir,filename,exec_name,language)


        if compile_result["status"] != "success":
        
            return {"status": compile_result["status"], "message": compile_result["message"]}

        logging.info("Compilation Successfull")

        run_cmd = config["run_command"]
        if language == 'java':
            run_cmd = config["run_command"].format(classname=exec_name)
        elif language == 'cpp':
            run_cmd = config["run_command"].format(exec_name=exec_name)
        else:
            run_cmd = config["run_command"].format(filename=exec_name)
        

        exec_result = execute_code_in_docker(
            submission_id,
            work_dir,
            run_cmd,
            input_file_path,
            config["image"],
            config["timeout"],
            config["memory_limit"]
        )

        logging.info("We are after execute_code_in_docker %s",
                     exec_result["status"])
        

        if exec_result["status"] != "success":
            logging.warning(f"User code execution failed with status")
            return {"status": exec_result["status"],
                    "user_output": exec_result["message"]
                    }
                    

        return {"status": "sucess", "user_output": exec_result["user_output"]}

        
    except Exception as e:
        logging.error(f"An error occurred during execution: {e}")
        return {"status": "failed", "message": str(e)}



def submit (submission_id , problem_id , code , language ):
        try :
            
            result = {
                "status":"accepted",
                "message":None,
                "failed_test_case":None
            }

            code = decode(code)

            if not isinstance(problem_id,str):
                problem_id=str(problem_id)

            config,error = validate_and_configure(language)

            if error:
                result.update({
                    "status":error["status"],
                    "message":error["message"]
                })
                return result
            
            
            work_dir = prepare_submission_directory(submission_id)

            

            if language== 'java':
                classname = find_classname(code)
                filename = f"{classname}{config['extension']}"
                exec_name=classname
            else:
                filename = f"{submission_id}{config['extension']}"
                exec_name = f"{submission_id}_exec"


            code_file_path = os.path.join(work_dir,filename)
            with open (code_file_path,"w") as f :
                f.write(code)

            #compiling ^_^
            logging.info("Before Compiling")
            compile_result  = compile_code(work_dir,filename,exec_name,language)


            if compile_result["status"] != "success":
                return {"status": compile_result["status"], "message": compile_result["message"]}
            

            logging.info("Compilation Successfull")

            test_inputs,expected_outputs = get_cached_testcases(problem_id)

            logging.info("Catching Successfull")


            for i,(test_input,expected_output) in enumerate(zip(test_inputs,expected_outputs)):

                input_path = os.path.join(work_dir,"inputs",f"input_{i}.txt")

                with open (input_path,"w") as f :
                    f.write(test_input)
                
                if language == 'java':
                    run_cmd = config["run_command"].format(classname=classname)
                elif language =="cpp":
                    run_cmd = config["run_command"].format(exec_name=exec_name,filename=filename)
                else:
                    run_cmd = config["run_command"].format(filename=filename)
                
                exec_result = execute_code_in_docker(
                    submission_id,
                    work_dir,
                    run_cmd,
                    input_path,
                    config["image"],
                    config["timeout"],
                    config["memory_limit"],
                )

                logging.info("redis output %s",expected_output)
                if exec_result["status"]!="success":
                    result.update({
                        "status":exec_result["status"],
                        "message":exec_result["message"],
                        "failed_test_case":f"Test Case {i}"
                    })
                    return result

                # print("Redis expected_output : ",expected_output)
                # print("docker_output : ",exec_result)
                exec_result["user_output"]=exec_result["user_output"].replace('\n','').strip()
                # print('dokcer output after replacing \\n',exec_result["user_output"])

                if exec_result["user_output"]!=expected_output.strip():
                    result.update({
                        "status":"wrong",
                        "message":"Failed Testcase",
                        "failed_test_case":f"Test Case {i}"
                    })

                logging.info("We are after execute_code_in_docker %s",exec_result["status"])
                logging.info("user_output : %s",exec_result.get("user_output"))
            return result
        
        except Exception as e:
            logging.error(f"An error occurred during submission: {e}")
            result.update({"status": "failedd", "message": str(e)})
            
            return result
        

        

