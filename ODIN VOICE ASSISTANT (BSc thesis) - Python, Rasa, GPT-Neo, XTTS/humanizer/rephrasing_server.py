import re

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
from accelerate import Accelerator

app = Flask(__name__)


def process_response(response: str):
    # if type == 'weather_future':
    #     found_degrees = False
    #     found_

    response_split = response.split('###Output:')
    response = response_split[1]
    # print(response)
    if '\\n' in response:
        response_split = response.split('\\n')
        response = response_split[0]
    response = response.strip()
    # print(response)

    sentences = re.findall(r'[^.!?]*[.!?]', response)

    if len(sentences) >= 5:
        response = ''.join(sentences[:5])
    else:
        response = ''.join(sentences)

    # response = response.replace('°C', ' degrees')
    # response = response.replace('km/h', 'kilometers per hour')

    return response


def initialize_rephrasing_model():
    accelerator_rephrasing = Accelerator()
    model = AutoModelForCausalLM.from_pretrained("./odin_rephrase")
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-1.3B", padding_side='left')
    tokenizer.padding_side = 'left'
    tokenizer.pad_token = tokenizer.eos_token
    model, tokenizer = accelerator_rephrasing.prepare(model, tokenizer)
    return model, tokenizer, accelerator_rephrasing


model_rephrasing, tokenizer_rephrasing, accelerator_rephrasing = initialize_rephrasing_model()


def rephrase(prompt_text, type, mood):
    input_format = f"###Input: {prompt_text}\n###Mood: {mood}\n###Type: {type}\n###Output:"
    encoding = tokenizer_rephrasing(input_format, return_tensors="pt", padding=True, truncation=True,
                                    max_length=128)
    input_ids = encoding['input_ids'].to(accelerator_rephrasing.device)
    attention_mask = encoding['attention_mask'].to(accelerator_rephrasing.device)
    with accelerator_rephrasing.autocast():
        generated_ids = model_rephrasing.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=50,
            num_return_sequences=1,
            do_sample=True,
            temperature=1.5,
            top_k=50,
            top_p=0.6,
            repetition_penalty=1.3,
        )
    return tokenizer_rephrasing.decode(generated_ids[0], skip_special_tokens=True)


mood_map = {-1: 'angry', 0: 'neutral', 1: 'happy'}


@app.route('/rephrase', methods=['POST'])
def rephrasing():
    data = request.json
    prompt = data.get("text")
    mood = data.get("mood")

    type = data.get("type")
    response_text = rephrase(prompt, type, mood_map[int(mood)])
    processed_response = process_response(response_text)
    print(type)
    print(processed_response)
    return jsonify({"response": processed_response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5001)
