import os
# import shutil
# import time
import sys
import shutil
import subprocess
import logging
import re
import base64
import redis
r = redis.StrictRedis(host='localhost',db=1, port=6379, decode_responses=True)
base_dir = os.getcwd()


logging.basicConfig(
    level=logging.INFO,  # show INFO and above
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # send logs to terminal
    ]
)


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
        
def runSystemcode(submission_id, problem_id, inputData=None):
   try:
        if not isinstance(problem_id, str):
            problem_id = str(problem_id)

        work_dir = prepare_submission_directory(submission_id)

        input_file = os.path.join(work_dir, "inputs", "custom_input.txt")

        if inputData is None:
            sample_input_path = os.path.join(
                "problems", problem_id, "sample.txt")
            if not os.path.exists(sample_input_path):
                return {"status": "failed", "user_output": "Sample input file not found."}

            logging.info(f"Reading sample input from {sample_input_path}")
            with open(sample_input_path, "r") as sample_file:
                inputData = sample_file.read()


        logging.info("Saving custom input data")
        with open(input_file, "w") as f:
            f.write(inputData)

        
        expected_output = execute_reference_solution(
            problem_id, submission_id, work_dir, input_file)
        
        logging.info("expected output: ",expected_output)
        return {"status": "executed_successfully", "expected_output": expected_output}

   except Exception as e:
          logging.error(f"An error occurred during execution: {e}")
          return {"status": "failed", "expected_output": str(e)}

   finally:
     logging.info("Cleaning up submission directory")
     work_dir = os.path.join(os.getcwd(), "submissions", f"submission_{submission_id}")
     if os.path.exists(work_dir):
        shutil.rmtree(work_dir)   

def execute_reference_solution(problem_id, submission_id, work_dir, input_file):
    """Fetch solution.cpp from Redis (by problem_id), compile, and run inside Docker."""
    try:
        if not isinstance(problem_id, str):
            problem_id = str(problem_id)
            
        # Fetch solution code from Redis
        solution_code = r.get(f"problem_{problem_id}/solution")
        if not solution_code:
            logging.error(f"Solution code not found in Redis for problem {problem_id}")
            return "[Error] Solution code not found"
        
        work_dir = f"/tmp/submissions/submission_{submission_id}"
        os.makedirs(work_dir, exist_ok=True)
        
        if os.path.isabs(input_file):
            
            input_file_relative = input_file
        else:
            input_file_relative = os.path.relpath(input_file, work_dir)
        
        solution_file = os.path.join(work_dir, "solution.cpp")
        
        if isinstance(solution_code, bytes):
            solution_code = solution_code.decode("utf-8")
            
        with open(solution_file, "w") as f:
            f.write(solution_code)
    
        compile_cmd = "g++ -o solution_exec solution.cpp"
        logging.info(f"Compiling solution with command: {compile_cmd}")
        compile_result = subprocess.run(
            compile_cmd,
            shell=True,
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        if compile_result.returncode != 0:
            logging.error(f"Compilation failed. Error: {compile_result.stderr.decode()}")
            return f"[Compilation Error] {compile_result.stderr.decode().strip()}"
            
        logging.info("Compilation successful.")
        
        docker_input_file = "input.txt"
        if not os.path.exists(os.path.join(work_dir, docker_input_file)):
            if os.path.exists(input_file):
                import shutil
                shutil.copy2(input_file, os.path.join(work_dir, docker_input_file))
            else:
      
                with open(os.path.join(work_dir, docker_input_file), "w") as f:
                    f.write("")
        
        # Run inside Docker with corrected paths
        docker_cmd = [
            "docker", "run", "--rm", 
            "-v", f"{work_dir}:/workspace",  
            "-w", "/workspace",             
            "gcc:latest",
            "sh", "-c",
            f"./solution_exec < {docker_input_file}", 
        ]
        
        logging.info(f"Executing solution with Docker: {' '.join(docker_cmd)}")
        result = subprocess.run(
            docker_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=30  
        )
        
        if result.returncode != 0:
            logging.error(f"Execution failed. Error: {result.stderr.decode()}")
            return f"[Runtime Error] {result.stderr.decode().strip()}"
        
        # Return program output
        output = result.stdout.decode().strip()
        logging.info(f"Solution executed successfully. Output: {output}")
        return output
        
    except subprocess.TimeoutExpired:
        logging.error("Solution execution timed out")
        return "[Runtime Error] Execution timed out"
    except Exception as e:
        logging.error(f"Unexpected error in execute_reference_solution: {str(e)}")
        return f"[Unexpected Error] {str(e)}"
    finally:
        # Optional: Clean up work directory
        try:
            if 'work_dir' in locals() and os.path.exists(work_dir):
                import shutil
                shutil.rmtree(work_dir)
        except:
            pass  # Ignore cleanup errors