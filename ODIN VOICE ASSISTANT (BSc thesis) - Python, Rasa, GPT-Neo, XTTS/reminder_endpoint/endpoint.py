from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import datetime

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

RASA_API = "http://localhost:5005/webhooks/rest/webhook"


def send_reminder(task):
    print(f"Sending reminder for: {task}")
    response = requests.post(RASA_API, json={"sender": "reminder_scheduler", "message": f"reminder_notification: {task}"})
    print(response)
    response_text = response.json()[0]['text']

    # chat_response = requests.post('http://localhost:5001/api/reminder', json={"message": response_text})


@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.json
    task = data['task']
    delay = data['delay']

    run_date = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    scheduler.add_job(send_reminder, 'date', run_date=run_date, args=[task])
    print(scheduler.print_jobs())

    return jsonify({"message": "Reminder scheduled"}), 200


if __name__ == '__main__':
    app.run(port=5000)
