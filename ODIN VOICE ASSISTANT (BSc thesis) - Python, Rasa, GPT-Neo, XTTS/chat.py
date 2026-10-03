import logging
import time
from tempfile import mkdtemp
import simpleaudio
import pydub
import requests
import threading
from pydub import AudioSegment
from pydub.playback import play
import queue
import io
from flask import Flask, request, jsonify

app = Flask(__name__)
message_queue = queue.Queue()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.logger.setLevel(logging.ERROR)

wake_up_cues = [['wake', 'up'], ['turn', 'on'], ['power', 'up'], ['come', 'online']]
shut_down_cues = [['turn', 'yourself', 'off'], ['go', 'idle'], ['shut', 'down'], ['back', 'to', 'sleep']]
TTS_ENABLED = True


def get_tts(text):
    payload = {'text': text}
    headers = {'Content-Type': 'application/json'}

    response = requests.post("http://192.168.0.107:5003/synthesize", json=payload)

    if response.status_code == 200:
        return response.content
    else:
        print("Failed to get audio from server:", response.status_code)
        return None


def play_audio(audio_bytes):
    if audio_bytes:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
        play(audio)
    else:
        print("No audio to play.")


def check_wake_up(input: str):
    input = input.lower().split(' ')
    is_wake_up = True
    for cues in wake_up_cues:
        is_wake_up = True
        for cue in cues:
            if cue not in input:
                is_wake_up = False
                break
        if is_wake_up:
            break

    return is_wake_up


def check_shut_down(input: str):
    input = input.lower().split(' ')
    is_shut_down = True
    for cues in shut_down_cues:
        is_shut_down = True
        for cue in cues:
            if cue not in input:
                is_shut_down = False
                break
        if is_shut_down:
            break

    return is_shut_down


@app.route('/api/reminder', methods=['POST'])
def receive():
    data = request.json
    message = f"{data.get('message', 'The reminder got lost on the way, sorry Paul.')}"
    # print(message)

    if TTS_ENABLED:
        if audio := get_tts(message):
            play_audio(audio)
    print(f'Bot: {message}')

    return jsonify({"status": "Message received"}), 200


@app.route('/api/toggle-tts', methods=['POST'])
def toggle_tts():
    global TTS_ENABLED
    TTS_ENABLED = not TTS_ENABLED

    return jsonify({"tts": f"{TTS_ENABLED}"}), 200


def run_flask():
    app.run(port=5001, use_reloader=False, threaded=True)


def listen_for_user_input():
    idle = True
    time.sleep(1)
    user_input = input("\nYou: ")
    while True:

        if idle and check_wake_up(user_input):
            idle = False

        if not idle:
            response = requests.post('http://localhost:5005/webhooks/rest/webhook',
                                     json={"sender": "user_1", "message": user_input})
            responses = response.json()
            for r in responses:
                text = r.get('text')
                if TTS_ENABLED:
                    if audio := get_tts(text):
                        play_audio(audio)
                print(f'Bot: {text}')
                # message_queue.put(f"\nBot: {text}\n")

        if not idle and check_shut_down(user_input):
            idle = True

        user_input = input("\nYou: ")


def display_messages():
    while True:
        message = message_queue.get()
        if audio := get_tts(message):
            play_audio(audio)
        else:
            print(message, end='')


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    # threading.Thread(target=listen_for_user_input, daemon=True).start()
    listen_for_user_input()
    # display_messages()
