import os
import subprocess
import json
import yaml
import re


def read_nlu_file(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        for index, intent in enumerate(data['nlu']):
            examples = intent['examples']
            examples = re.findall(r"- (.*?)\n", examples)
            data['nlu'][index]['examples'] = examples
        # print(data)
        return data


def write_nlu_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write('version: "{}"\n'.format(data['version']))
        file.write('nlu:\n')
        for intent_data in data['nlu']:
            file.write('  - intent: {}\n'.format(intent_data['intent']))
            file.write('    examples: |\n')
            for example in intent_data['examples']:
                file.write('      - {}\n'.format(example))


def run_chatito(chatito_file):
    command = f'chatito {chatito_file} --format=rasa'
    subprocess.run(command, shell=True)


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def main():
    nlu_data = read_nlu_file('data/chatito/nlu.yml')
    output_dir = 'D:\\Stuff\\My Shit\\facultate\\an4\\Licenta\\rasa'

    # print(nlu_data)
    chatito_dir = 'data/chatito'

    for file in os.listdir(chatito_dir):
        if file.endswith('.chatito'):
            run_chatito(os.path.join(chatito_dir, file))

            training_file = os.path.join(output_dir, 'rasa_dataset_training.json')
            training_data = read_json_file(training_file)

            intent_yaml_format = {'intent': training_data['rasa_nlu_data']['common_examples'][0]['intent'],
                                  'examples': [data['text'] for data in
                                               training_data['rasa_nlu_data']['common_examples']]
                                  }

            # print(intent_yaml_format)
            if intent_yaml_format not in nlu_data['nlu']:
                nlu_data['nlu'].append(intent_yaml_format)

                # print(nlu_data)
    write_nlu_file('data/nlu.yml', nlu_data)


if __name__ == '__main__':
    main()
