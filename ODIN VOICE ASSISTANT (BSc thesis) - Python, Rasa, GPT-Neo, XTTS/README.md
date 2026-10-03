# ODIN: voice assistant (bachelor thesis)

My bachelor thesis project (TUCN, 2024). A Rasa assistant with intents for weather, reminders, a shopping list, jokes and small talk, whose answers are then rephrased and spoken:

- `rasa_core/`: NLU data, rules, domain and custom actions, including a natural-language time parser (`actions/nl_time_converter`) and an OpenWeatherMap client. Evaluation reports and confusion matrices are in `rasa_core/results/`.
- `reminder_endpoint/`: Flask + APScheduler reminder service.
- `humanizer/`: three Flask servers. A fine-tuned GPT-Neo 1.3B dialogue model, a GPT-Neo rephrasing model, and Coqui XTTS v2 text-to-speech with voice cloning.
- `chat.py`: console client. `run.py`: starts the processes.
- `diagrams/`: architecture diagrams. `docs/`: the thesis (Romanian).

Not included: the trained Rasa models, the fine-tuned GPT-Neo weights, the reference voice sample and the bundled ffmpeg binaries. The weather action reads its key from `OPENWEATHERMAP_API_KEY`. Host addresses in `chat.py` and `actions.py` point at the machines I ran it on.
