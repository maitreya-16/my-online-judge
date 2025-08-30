import redis 
import os

r = redis.Redis(host='localhost',db=1, port=6379, decode_responses=True)

def load_data(pid , path):
    # print("Problem id ",pid)
    # print(path)
    i = 0
    while True:
        input_path = os.path.join(path,f"input_{i}.txt")
        output_path = os.path.join(path,f"output_{i}.txt")
        # print(input_path)
        # print(output_path)
        if not os.path.exists(input_path) or not os.path.exists(output_path):
            print("Input output finished")
            break
        with open (input_path,'r') as f:
            input = (f.read().strip())
            r.set(f"{pid}/input_{i}",input)
        with open(output_path,"r") as f:
            output = (f.read().strip())
            r.set(f"{pid}/output_{i}",output)
        i=i+1
    r.set(f"{pid}/count",i)

# print(os.listdir("problems"))
for pid in (os.listdir("problems")):
    path = os.path.join("problems", pid)
    load_data(pid,path)
        