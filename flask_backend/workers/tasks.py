from asyncio import log
from codecs import decode
from celery import Celery
import requests
from workers.execute_code import run_code as run, runSystemcode
from workers.execute_code import submit
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
BACKEND_HOST = os.getenv('BACKEND_HOST', 'backend')
BACKEND_PORT = int(os.getenv('BACKEND_PORT', 3000))

REDIS_BROKER_URL = os.getenv('REDIS_BROKER_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')
REDIS_BACKEND_URL = os.getenv('REDIS_BACKEND_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')

app = Celery(    
    'tasks',
    broker=REDIS_BROKER_URL,
    backend=REDIS_BACKEND_URL,
)
app.conf.update(
    broker_heartbeat=10,
    broker_connection_timeout=30,
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)
# specify ur express port


app.conf.result_expires = 3600  # seconds me he.. 1 hour

# WEBHOOK_URL_RUN = f'https://abhitime.credenz.co.in/webhook/run'
# WEBHOOK_URL_SUBMIT = f'https://abhitime.credenz.co.in/webhook/submit'
# WEBHOOK_URL_SYSTEM = f'https://abhitime.credenz.co.in/webhook/system'

WEBHOOK_URL_RUN = f'http://{BACKEND_HOST}:{BACKEND_PORT}/webhook/run'
WEBHOOK_URL_SUBMIT = f'http://{BACKEND_HOST}:{BACKEND_PORT}/webhook/submit'
WEBHOOK_URL_SYSTEM = f'http://{BACKEND_HOST}:{BACKEND_PORT}/webhook/system'


def send_webhook_result(url, data):
    """POST result to webhook endpoint."""
    try:
        print(f"[Webhook] Sending to {url}")
        r = requests.post(url, json=data, timeout=10)
        r.raise_for_status()
        print("[Webhook] Sent successfully.")
    except Exception as e:
        print(f"[Webhook] Failed to send: {e}")


# ─── Task: Run System Code ──────────────────────────────────────────────

@app.task(name="tasks.run_code", queue="runQueue")
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
    send_webhook_result(WEBHOOK_URL_RUN, webhook_data)
    return result


# ─── Task: Code Submission ──────────────────────────────────────────────

@app.task(name="tasks.submit_code", queue="submitQueue")
def submit_code(data):
    print("Submitting code...")
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
        'total_test_case':result.get('total_test_case'),
        'score':result.get('score'),
    }
    print("Webhook Data:", webhook_data)
    send_webhook_result(WEBHOOK_URL_SUBMIT, webhook_data)
    return (result)

# ─── Task: Run System Code ──────────────────────────────────────────────

@app.task(name="tasks.run_system_code", queue="runSystemQueue")
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
        'user_output':result.get('user_output')
    }
    send_webhook_result(WEBHOOK_URL_SYSTEM, webhook_data)
    return result
