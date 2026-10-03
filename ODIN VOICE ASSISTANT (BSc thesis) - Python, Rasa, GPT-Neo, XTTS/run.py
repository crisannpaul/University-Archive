import subprocess
import threading
import sys


def process_output(process, process_name):
    for line in iter(process.stdout.readline, ''):
        sys.stdout.write(f"[{process_name}] {line}")


def start_process(command, process_name, cwd=None):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True, cwd=cwd)
    threading.Thread(target=process_output, args=(process, process_name), daemon=True).start()
    return process


if __name__ == "__main__":
    python_path = "C:\\Users\\Paul\\AppData\\Local\\Programs\\Python\\Python310\\python.exe"
    rasa_dir = "rasa_core"

    rasa_cmd = "rasa run -m rasa_core/models"
    rasa_actions_cmd = "rasa run actions"
    reminder_endpoint_cmd = f"{python_path} reminder_endpoint/endpoint.py"
    chat_cmd = f"{python_path} chat.py"

    rasa_process = start_process(rasa_cmd, "Rasa", cwd=rasa_dir)
    rasa_actions_process = start_process(rasa_actions_cmd, "Rasa Actions", cwd=rasa_dir)
    reminder_endpoint_process = start_process(reminder_endpoint_cmd, "Reminder Endpoint")
    # chat_process = start_process(chat_cmd, "Chat")

    rasa_process.wait()
    rasa_actions_process.wait()
    reminder_endpoint_process.wait()
    # chat_process.wait()

