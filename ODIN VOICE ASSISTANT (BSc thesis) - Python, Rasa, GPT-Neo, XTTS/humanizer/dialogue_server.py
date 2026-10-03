import re

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
from accelerate import Accelerator

app = Flask(__name__)


class ContextWindow:
    def __init__(self):
        self.window = []

    def add_input(self, input: str):
        # print(f'Input {input}')
        if not input.endswith(('.', '!', '?')):
            input += '.'
        self.window.append(input)
        # print(f'Added {input}')

    def add_response(self, response: str):
        # print(f'Raw response {response}')
        corresponding_input = self.window[-1]
        split_response = response.split(corresponding_input)
        if len(split_response) > 1:
            response = split_response[1]
        else:
            response = split_response[0]
        response = response.lstrip('\n')
        # print(f'Response after strip {response}')

        if '\n' in response:
            response = response.split('\n')[0]
        response = response.strip()

        # print(f'Response after split {response}')

        sentences = re.findall(r'[^.!?]*[.!?]', response)

        if len(sentences) >= 5:
            response = ''.join(sentences[:5])
        else:
            response = ''.join(sentences)

        self.window.append(response)
        if len(self.window) > 5:
            self.window.pop(0)

    def get_last(self):
        return self.window[-1]

    def format(self):
        formatted_context = ''
        for dialogue in self.window:
            formatted_context += dialogue + '\n'
        return formatted_context.rstrip('\n')


def process_response(previous, response):
    split_response = response.split(previous)
    if len(split_response) > 1:
        response = split_response[1]
    else:
        response = split_response[0]
    response = response.lstrip('\n')
    # print(f'Response after strip {response}')

    if '\n' in response:
        response = response.split('\n')[0]
    response = response.strip()

    # print(f'Response after split {response}')

    sentences = re.findall(r'[^.!?]*[.!?]', response)

    if len(sentences) >= 4:
        response = ''.join(sentences[:4])
    else:
        response = ''.join(sentences)

    return response


def initialize_dialogue_model():
    accelerator_dialogue = Accelerator()
    model = AutoModelForCausalLM.from_pretrained("./odin_dialogue").to("cuda:0")
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-1.3B", padding_side='left')
    tokenizer.padding_side = 'left'
    tokenizer.pad_token = tokenizer.eos_token
    model, tokenizer = accelerator_dialogue.prepare(model, tokenizer)
    return model, tokenizer, accelerator_dialogue


model_dialogue, tokenizer_dialogue, accelerator_dialogue = initialize_dialogue_model()
context = ContextWindow()


def generate_dialogue(prompt_text):
    encoding = tokenizer_dialogue(prompt_text + '<|endoftext|>', return_tensors="pt", padding=True, truncation=True, max_length=128)
    input_ids = encoding['input_ids'].to(accelerator_dialogue.device)
    attention_mask = encoding['attention_mask'].to(accelerator_dialogue.device)
    with accelerator_dialogue.autocast():
        generated_ids = model_dialogue.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=50,
            num_return_sequences=1,
            do_sample=True,
            temperature=1,
            top_k=50,
            top_p=0.6,
            repetition_penalty=1.2,
        )
    return tokenizer_dialogue.decode(generated_ids[0], skip_special_tokens=True)


@app.route('/dialogue', methods=['POST'])
def conversation():
    input_text = request.json.get("text")
    print(input_text, end='\n')
    response_text = generate_dialogue(input_text)
    print(response_text, end='\n')
    response = process_response(input_text, response_text)
    print(response, end='\n')
    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5002)
