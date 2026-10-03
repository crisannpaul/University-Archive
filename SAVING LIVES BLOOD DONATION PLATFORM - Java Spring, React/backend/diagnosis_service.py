import os
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# try:
#     import flask
# except ImportError:
#     install('flask')

# try:
#     import openai
# except ImportError:
#     install('openai')

from flask import Flask, request, jsonify
import openai

API_KEY = os.environ["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=API_KEY)

def generate(prompt, text='', model='gpt-3.5-turbo'):

    chat_completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    enhanced_text = chat_completion.choices[0].message.content
    return enhanced_text.strip()


app = Flask(__name__)

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    symptoms = request.json.get('symptoms')
    prompt = (
        "You are built to run as a symptom diagnosis service for my app for a project. "
        "Use a simple diagnosis for the given symptoms, don't overcomplicate, "
        "and then give a recommendation to the patient, what they should do next. "
        "Keep the response short and concise. "
        f"Symptoms: {symptoms}."
    )
    
    diagnosis = generate(prompt, symptoms)
    print(diagnosis)
    
    return jsonify({"diagnosis": diagnosis})

if __name__ == '__main__':
    app.run(debug=True, port=6969)
