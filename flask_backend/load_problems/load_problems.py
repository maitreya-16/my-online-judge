import redis 
import os
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
r = redis.Redis(host=REDIS_HOST, db=1, port=REDIS_PORT, decode_responses=True)

def load_data(pid, path):
    i = 0
    while True:
        input_path = os.path.join(path, f"input_{i}.txt")
        output_path = os.path.join(path, f"output_{i}.txt")

        if not os.path.exists(input_path) or not os.path.exists(output_path):
            print(f"Input/output finished for {pid}")
            break

        with open(input_path, 'r') as f:
            input_data = f.read().strip()
            r.set(f"{pid}/input_{i}", input_data)

        with open(output_path, "r") as f:
            output_data = f.read().strip()
            r.set(f"{pid}/output_{i}", output_data)

        i += 1

    r.set(f"{pid}/count", i)

    # ✅ Add solution.cpp if it exists
    solution_path = os.path.join(path, "solution.cpp")
    if os.path.exists(solution_path):
        with open(solution_path, "r") as f:
            solution_code = f.read().strip()
            r.set(f"{pid}/solution", solution_code)
        print(f"Loaded solution.cpp for problem {pid}")
    else:
        print(f"No solution.cpp found for problem {pid}")

for pid in os.listdir("problems"):
    path = os.path.join("problems", pid)
    load_data(pid, path)
