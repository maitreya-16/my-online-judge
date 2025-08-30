from celery import Celery
from execute_code import run_code as run
from execute_code import submit
import os


REDIS_BROKER_URL = os.getenv('REDIS_BROKER_URL', 'redis://localhost:6379/0')
REDIS_BACKEND_URL = os.getenv('REDIS_BACKEND_URL', 'redis://localhost:6379/0')

app = Celery(    
    'tasks',
    broker=REDIS_BROKER_URL,
    backend=REDIS_BACKEND_URL,
)
app.conf.result_expires = 3600  # seconds me he.. 1 hour

@app.task
def run_code(data):
    # print("Running code...")
    result = run(
        submission_id=data['submission_id'],
        code=data['code'],
        language=data['language'],
        problem_id=data['problem_id'],
        inputData=data['customTestcase']
    )
    return (result)

@app.task
def submit_code(data):
    # print("Submitting code...")
    result = submit(
        submission_id=data['submission_id'],
        problem_id=data['problem_id'],
        code=data['code'],
        language=data['language'],
    )
    return (result)

    