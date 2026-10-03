from flask import Flask, request, send_file
from TTS.api import TTS
import torch
import os

app = Flask(__name__)


# Initialize the TTS model
def initialize_tts_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    return tts, device


tts, device = initialize_tts_model()


@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.json
    text = data.get("text")
    language = data.get("language", "en")  # Default to English if not specified

    file_path = "output.wav"
    path_to_speaker = 'speaker_paul.wav'
    tts.tts_to_file(text=text, speaker_wav=path_to_speaker, language=language, file_path=file_path)

    # Return the generated WAV file
    return send_file(file_path, mimetype="audio/wav")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)
