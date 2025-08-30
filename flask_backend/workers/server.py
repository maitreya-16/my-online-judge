from flask import Flask,request,jsonify
from tasks import run_code , submit_code
app = Flask(__name__)

@app.route("/enqueue/run", methods=["POST"])
def enqueue_run():
    data = request.get_json()
    run_code.delay(data)
    return jsonify({"message": "Code execution started"}), 202

@app.route("/enqueue/submit", methods=["POST"])
def enqueue_submit():
    data = request.get_json()
    submit_code.delay(data)
    return jsonify({"message": "Code execution started"}), 202


if __name__ == "__main__":
    #PORT = 5000 
    app.run(host="0.0.0.0", port=5000, debug=True)