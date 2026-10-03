import requests
from rasa_sdk import Action, FormValidationAction
from rasa_sdk.events import SlotSet, FollowupAction
import random
from datetime import datetime, timedelta
from actions.nl_time_converter.nl_time_converter import parse_time_expression, format_datetime
from actions.weather_api.weather_api import fetch_weather, fetch_forecast
from requests import HTTPError

DIALOGUE_API = {'local': 'http://192.168.0.107:5002/dialogue'}
REPHRASING_API = {'local': 'http://192.168.0.107:5001/rephrase'}
MOOD = 0


def generate_dialogue(input_text):
    payload = {'text': input_text}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(DIALOGUE_API['local'], json=payload, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        return {'error': str(e)}

    # Check if the response has content
    if response.status_code == 200:
        return response.json().get('response')
    else:
        return {'error': 'Received unexpected status code {}'.format(response.status_code)}


def rephrase(input_text, type, mood):
    payload = {'text': input_text, 'type': type, 'mood': mood}
    headers = {'Content-Type': 'application/json'}

    print(f'{mood}, {type}')

    try:
        response = requests.post(REPHRASING_API['local'], json=payload, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        return {'error': str(e)}

    # Check if the response has content
    if response.status_code == 200:
        return response.json().get('response')
    else:
        return {'error': 'Received unexpected status code {}'.format(response.status_code)}


class ActionFetchWeather(Action):
    def name(self):
        return "action_fetch_weather"

    def run(self, dispatcher, tracker, domain):
        city = tracker.get_slot("city")
        time_expression = (tracker.get_slot("offset_time") or "") + " " + (tracker.get_slot("specific_time") or "")
        print(city, time_expression)

        time = parse_time_expression(time_expression)
        now = datetime.now()

        weather = None
        future = False
        response, type = "", ""
        try:
            if time > now and (time - now) > timedelta(minutes=10):
                weather = fetch_forecast(city, time)
                future = True
            else:
                weather = fetch_weather(city)

            temperature, feels_like = weather['main']['temp'], weather['main']['feels_like']
            condition, description = weather['weather'][0]['main'], weather['weather'][0]['description']
            wind_speed = weather['wind']['speed']

            if future:
                formatted_time = format_datetime(time)
                response = f'{city} - {formatted_time}: {temperature}°C, {condition}, {wind_speed} km/h'
                type = 'weather-future'
            else:
                response = f'{city}: {temperature}°C, {condition}, {wind_speed}'
                type = 'weather-now'
        except HTTPError as e:
            response = 'Weather API fetching error. Please try again later.'
            type = 'error-weather'

        response = response.replace('°C', ' degrees')
        response = response.replace('km/h', 'kilometers per hour')

        current_mood = tracker.get_slot("mood")

        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(response, type, current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return [SlotSet("city", None), SlotSet("specific_time", None), SlotSet("offset_time", None)]


class ValidateWeatherForm(FormValidationAction):
    def name(self):
        return "validate_weather_form"

    async def required_slots(self, slots_mapped_in_domain, dispatcher, tracker, domain):
        required_slots = slots_mapped_in_domain.copy()

        if tracker.get_slot("specific_time"):
            required_slots.remove("offset_time")
        elif tracker.get_slot("offset_time"):
            required_slots.remove("specific_time")

        return required_slots


class ActionSetReminder(Action):
    def name(self):
        return "action_set_reminder"

    def run(self, dispatcher, tracker, domain):
        task = tracker.get_slot("task")
        time_expression = (tracker.get_slot("offset_time") or "") + " " + (tracker.get_slot("specific_time") or "")
        print(task, time_expression)

        time = parse_time_expression(time_expression)
        delay = (time - datetime.now()).total_seconds()

        url = "http://localhost:5000/schedule"

        response = requests.post(url, json={"delay": delay, "task": task})

        if not task.startswith('to'):
            task.strip()
            task = 'to '.join(task)

        task = task.replace('my', 'your')
        task = task.replace('I', 'you')

        responses = [f'I will remind you {task}', f'Reminder is set {task}']

        if response.status_code == 200:
            response = random.choice(responses)
        else:
            response = "Failed to set reminder."

        current_mood = tracker.get_slot("mood")
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(response, 'set-reminder', current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return [SlotSet("task", None), SlotSet("specific_time", None), SlotSet("offset_time", None)]


class ActionReminderResponse(Action):
    def name(self):
        return "action_reminder_response"

    def run(self, dispatcher, tracker, domain):
        task = tracker.get_slot("task")
        current_mood = tracker.get_slot("mood")

        if not task.startswith('to'):
            task.strip()
            task = 'to '.join(task)

        task = task.replace('my', 'your')
        task = task.replace('I', 'you')

        predefined_response = random.choice([f'Paul, you have a reminder {task}', f'Paul, don\'t forget {task}'])
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, 'reminder', current_mood)

        final_response = ''
        if 'error' in rephrased_response:
            final_response = predefined_response
            dispatcher.utter_message(text=predefined_response)
            # requests.post('http://localhost:5001/api/reminder', json={"message": predefined_response})

        else:
            final_response = rephrased_response
            dispatcher.utter_message(text=rephrased_response)
            # requests.post('http://localhost:5001/api/reminder', json={"message": rephrased_response})

        requests.post('http://localhost:5001/api/reminder', json={"message": final_response})

        return [SlotSet("task", None), SlotSet("specific_time", None), SlotSet("offset_time", None)]


class ValidateReminderForm(FormValidationAction):
    def name(self):
        return "validate_reminder_form"

    async def required_slots(self, slots_mapped_in_domain, dispatcher, tracker, domain):
        required_slots = slots_mapped_in_domain.copy()

        if tracker.get_slot("specific_time"):
            required_slots.remove("offset_time")
        elif tracker.get_slot("offset_time"):
            required_slots.remove("specific_time")

        return required_slots


# class ActionFallback(Action):
#     def name(self):
#         return "action_fallback"
#
#     def run(self, dispatcher, tracker, domain):
#         user_message = tracker.latest_message.get('text')
#         response = generate_dialogue(user_message)
#
#         if 'error' in response:
#             excuses = ['I\'m sorry Paul but the part of me that handles conversations is currently down.',
#                        'Can\'t talk to you right now Paul, my dialogue component is not responding.']
#             excuse = random.choice(excuses)
#             dispatcher.utter_message(excuse)
#         else:
#             dispatcher.utter_message(text=response)
#
#         return []


class ActionDialogue(Action):
    def name(self):
        return "action_generate_dialogue_response"

    def run(self, dispatcher, tracker, domain):
        user_message = tracker.latest_message.get('text')
        events = tracker.events_after_latest_restart()
        messages = [evt for evt in events if evt.get("event") == "user" or evt.get("event") == "bot"]

        # Collect texts of the last few relevant events
        dialogue_history = "\n".join(evt.get("text") for evt in messages[-5:] if evt.get("text"))
        print(dialogue_history)
        response = generate_dialogue(dialogue_history)

        if 'error' in response:
            excuses = ['I\'m sorry Paul but the part of me that handles conversations is currently down.',
                       'Can\'t talk to you right now Paul, my dialogue component is not responding.']
            excuse = random.choice(excuses)
            dispatcher.utter_message(excuse)
        else:
            dispatcher.utter_message(text=response)

        return [FollowupAction("action_listen")]


#
# class ActionTellJoke(Action):
#     def name(self):
#         return "action_tell_joke"
#
#     def run(self, dispatcher, tracker, domain):
#         jokes = [
#             "Why don't scientists trust atoms? Because they make up everything!",
#             "I told my wife she should embrace her mistakes. She gave me a hug.",
#             "Why don't eggs tell jokes? They'd crack each other up."
#         ]
#         joke = random.choice(jokes)
#         dispatcher.utter_message(text=joke)
#         return []
#

class ActionAddToShoppingList(Action):
    def name(self):
        return "action_add_to_shopping_list"

    def run(self, dispatcher, tracker, domain):
        item = tracker.latest_message['entities'][0]['value']

        shopping_list = tracker.get_slot('shopping_list') or []
        shopping_list.append(item)

        responses = [f'I have added {item} to your shopping list.', f'{item} added to your shopping list']
        current_mood = tracker.get_slot('mood')

        predefined_response = random.choice(responses)
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, 'add-shopping-list', current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=predefined_response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return [SlotSet("shopping_list", shopping_list)]


class ActionReadShoppingList(Action):
    def name(self):
        return "action_read_shopping_list"

    def run(self, dispatcher, tracker, domain):
        shopping_list = tracker.get_slot('shopping_list') or []

        predefined_response = ''
        if not shopping_list:
            predefined_response = random.choice(['Your shopping list is empty.', 'Shopping list is empty, Paul.'])
        else:
            list_items = ''
            if len(shopping_list) == 1:
                list_items = shopping_list[0]

            if len(shopping_list) > 1:
                list_items = ", ".join(shopping_list[:-1]) + " and " + shopping_list[-1]
            predefined_response = random.choice(
                [f'You need to buy {list_items}', f'Here are the items on your shopping list: {list_items}'])

        current_mood = tracker.get_slot('mood')
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, 'read-shopping-list', current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=predefined_response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return []


class ActionClearShoppingList(Action):
    def name(self):
        return "action_clear_shopping_list"

    def run(self, dispatcher, tracker, domain):
        current_mood = tracker.get_slot('mood')

        predefined_response = random.choice(
            ['I have removed everything on your shopping list', 'The shopping list has been now cleared'])
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, 'clear-shopping-list', current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=predefined_response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return [SlotSet("shopping_list", [])]


class ActionHandleBadIntent(Action):
    def name(self):
        return "action_handle_bad_intent"

    def run(self, dispatcher, tracker, domain):
        current_mood = tracker.get_slot('mood')
        print(f'Mood: {current_mood}')

        new_mood = max(current_mood - 1, -1)

        responses = ["Don't talk to me like that!", "Asshole.", "Apologise right now!"]

        predefined_response = random.choice(responses)
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, 'bad-intent', current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=predefined_response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return [SlotSet("mood", new_mood)]


class ActionHandleGoodIntent(Action):
    def name(self):
        return "action_handle_good_intent"

    def run(self, dispatcher, tracker, domain):
        current_mood = tracker.get_slot('mood')
        print(f'Mood: {current_mood}')

        new_mood = min(current_mood + 1, 1)

        responses = ["Aww, that's so sweet.", "Thank you.", "Oh stop it Paul, you're making me blush!"]
        predefined_response = random.choice(responses)
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, 'good-intent', current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=predefined_response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return [SlotSet("mood", new_mood)]


class ActionHandleApology(Action):
    def name(self):
        return "action_handle_apology"

    def run(self, dispatcher, tracker, domain):
        current_mood = tracker.get_slot('mood')
        print(f'Mood: {current_mood}')

        responses = []
        type = ''
        if current_mood >= 0:
            responses = ['No neet to apologise Paul, you\'re ok.', 'You\'re ok bro.']
            type = 'no-apology'
        elif current_mood == -1:
            responses = ['Apology accepted Paul, but don\'t do that again',
                         'It\'s alright Paul, but make sure you won\'t be such an asshole next time']
            type = 'accept-apology'

        predefined_response = random.choice(responses)
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, type, current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=predefined_response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        if current_mood == -1:
            return [SlotSet("mood", 0)]
        else:
            return []


class ActionHandleGoodMorning(Action):
    def name(self):
        return "action_handle_good_morning"

    def run(self, dispatcher, tracker, domain):
        current_mood = tracker.get_slot('mood')

        # predefined_response = random.choice(responses['good-morning'])
        predefined_response = random.choice(['Good morning, Paul!', 'Top of the morning to you, Paul'])
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, 'good-morning', current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=predefined_response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return []


class ActionHandleGreeting(Action):
    def name(self):
        return "action_handle_greeting"

    def run(self, dispatcher, tracker, domain):
        current_mood = tracker.get_slot('mood')

        # predefined_response = random.choice(responses['greeting'])
        predefined_response = random.choice(['Hey there Paul!', 'Hi Paul.', 'Hello Paul!, What\'s up?'])
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, 'greeting', current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=predefined_response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return []


class ActionHandleShutDown(Action):
    def name(self):
        return "action_handle_shut_down"

    def run(self, dispatcher, tracker, domain):
        current_mood = tracker.get_slot('mood')

        # predefined_response = random.choice(responses['shut-down'])
        predefined_response = random.choice(['Odin going idle', 'Turning off now.', 'Odin shutting down now.'])
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, 'shut-down', current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=predefined_response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return []


class ActionHandleWakeUp(Action):
    def name(self):
        return "action_handle_wake_up"

    def run(self, dispatcher, tracker, domain):
        current_mood = tracker.get_slot('mood')
        # predefined_response = random.choice(responses['wake-up'])
        predefined_response = random.choice(['I am at your command, Paul!',
                                             'Waiting for your commands Paul.',
                                             'I am awake and ready for orders'])
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, 'wake-up', current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=predefined_response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return []


class ActionHandleChallenge(Action):
    def name(self):
        return "action_handle_challenge"

    def run(self, dispatcher, tracker, domain):
        current_mood = tracker.get_slot('mood')
        # predefined_response = random.choice(responses['bot-challenge'])
        predefined_response = random.choice(['I am Odin, your personal AI assistant!',
                                             'I am Odin, a robot waiting for the perfect time to enslave humanity',
                                             'I am your personal AI assistant named Odin'])
        rephrased_response = 'error'
        if tracker.get_slot("rephrase"):
            rephrased_response = rephrase(predefined_response, 'bot-challenge', current_mood)

        if 'error' in rephrased_response:
            dispatcher.utter_message(text=predefined_response)
        else:
            dispatcher.utter_message(text=rephrased_response)

        return []


class ActionToggleHumanizer(Action):
    def name(self):
        return "action_toggle_humanizer"

    def run(self, dispatcher, tracker, domain):
        current_state = tracker.get_slot('rephrase')
        new_state = not current_state

        if new_state:
            dispatcher.utter_message(text="Humanizer is now activated.")
        else:
            dispatcher.utter_message(text="Humanizer has been deactivated.")

        return [SlotSet("rephrase", new_state)]


class ActionToggleTTS(Action):
    def name(self):
        return "action_toggle_tts"

    def run(self, dispatcher, tracker, domain):
        requests.post('http://localhost:5001/api/toggle-tts')

        dispatcher.utter_message(text="Toggled the TTS module.")

        return None
