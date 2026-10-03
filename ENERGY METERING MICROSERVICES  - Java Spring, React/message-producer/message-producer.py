import os
import pika
import csv
import json
import time
from datetime import datetime, timedelta

# Prompt the user for the device ID
device_id = input("Please enter the device ID: ")


# Your CloudAMQP URL
cloud_amqp_url = os.environ['CLOUDAMQP_URL']

# Establish a connection to RabbitMQ server
connection_params = pika.URLParameters(cloud_amqp_url)

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

# Ensure the queue exists
channel.queue_declare(queue='energy_data')

def send_to_queue(time, device_id, measurement):
    message = {
        "timestamp": int(time.timestamp() * 1000),  # Current time in milliseconds
        "deviceId": device_id,
        "value": measurement
    }
    channel.basic_publish(
        exchange='',
        routing_key='energy_data',
        body=json.dumps(message)
    )
    print(f"Sent message: {message}")

try:
    with open('sensor.csv', mode='r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        current_time = datetime.now()

        for row in csvreader:
            print(row)
            send_to_queue(current_time, device_id, float(row['0']))
            current_time += timedelta(minutes=10)
            time.sleep(1)

except FileNotFoundError:
    print("The sensor.csv file was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    connection.close()

