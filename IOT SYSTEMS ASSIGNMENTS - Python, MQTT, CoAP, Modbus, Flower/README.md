# IoT systems assignments (Python)

Four assignments from the master's Internet of Things course.

1. **Device simulation, HTTP vs MQTT.** Threaded simulated sensors replay the Intel Berkeley Lab dataset over HTTP or MQTT (Mosquitto); a consumer ingests the messages and exposes Prometheus metrics. Plots in `out/` compare the two at 4 and 40 devices.
2. **Industrial protocols gateway.** MQTT, CoAP and Modbus devices with fault injection (latency, packet loss, device failure) feeding one gateway through RabbitMQ. Has its own README.
3. **MQTT intrusion detection.** Notebook: leakage-aware time-delta features and a multiclass XGBoost IDS on the MQTTEEB-D dataset.
4. **Federated vs centralized RUL.** LSTM remaining-useful-life regression on NASA C-MAPSS, trained centrally and with Flower federated learning across 10 clients. Report: `documentation.pdf`.

Not included: the datasets, trained models and raw run logs.
