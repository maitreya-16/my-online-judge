from asyncio import log
from codecs import decode
from celery import Celery
import requests
from execute_code import run_code as run, runSystemcode
from execute_code import submit
import os


REDIS_BROKER_URL = os.getenv('REDIS_BROKER_URL', 'redis://localhost:6379/0')
REDIS_BACKEND_URL = os.getenv('REDIS_BACKEND_URL', 'redis://localhost:6379/0')

app = Celery(    
    'tasks',
    broker=REDIS_BROKER_URL,
    backend=REDIS_BACKEND_URL,
)
BACKEND_HOST = "localhost"
BACKEND_PORT = 3000
# specify ur express port

app.conf.result_expires = 3600  # seconds me he.. 1 hour

WEBHOOK_URL_RUN = f'http://{BACKEND_HOST}:{BACKEND_PORT}/webhook/run'
WEBHOOK_URL_SUBMIT = f'http://{BACKEND_HOST}:{BACKEND_PORT}/webhook/submit'
WEBHOOK_URL_SYSTEM = f'http://{BACKEND_HOST}:{BACKEND_PORT}/webhook/system'

def send_webhook_result(url, data):
    """POST result to webhook endpoint."""
    try:
        print(f"[Webhook] Sending to {url}")
        r = requests.post(url, json=data, timeout=5)
        r.raise_for_status()
        print("[Webhook] Sent successfully.")
    except Exception as e:
        print(f"[Webhook] Failed to send: {e}")

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
    # return (result)

    webhook_data = {
        'submission_id': data['submission_id'],
        'status': result.get('status'),
        'message': result.get('message'),
        'expected_output': result.get('expected_output'),
        'user_output':result.get('user_output')
        
    }
    # send_webhook_result(WEBHOOK_URL_RUN, webhook_data)
    return result


@app.task
def submit_code(data):
    # print("Submitting code...")
    result = submit(
        submission_id=data['submission_id'],
        problem_id=data['problem_id'],
        code=data['code'],
        language=data['language'],
    )
    webhook_data = {
        'submission_id':data["submission_id"],
        'status':result.get('status'),
        'message':result.get('message'),
        'failed_test_case':result.get('failed_test_case'),
        'score':result.get('score')
    }
    print("Webhook Data:", webhook_data)
    send_webhook_result(WEBHOOK_URL_SUBMIT, webhook_data)
    return (result)

@app.task
def run_system_code(data):
    # if data.get('customTestcase'):
    #     data['customTestcase'] = decode(data['customTestcase'])
    
    result = runSystemcode(
        submission_id=data['submission_id'],
        problem_id=data['problem_id'],
        inputData=data.get('customTestcase')
    )
    # return (result)
    

    # return (result)
    
    webhook_data = {
        'submission_id': data['submission_id'],
        'status': result.get('status'),
        'message': result.get('message'),
        'expected_output': result.get('expected_output')
    }
    send_webhook_result(WEBHOOK_URL_SYSTEM, webhook_data)