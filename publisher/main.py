import pika
import random
import time
import json
from datetime import datetime
import os

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
PUBLISH_INTERVAL = int(os.environ.get('PUBLISH_INTERVAL', 1))
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'admin')

def generate_random_number():
    return random.randint(1, 100)

def publish_number(channel, number):
    timestamp = datetime.now().isoformat()
    message = json.dumps({"value": number, "timestamp": timestamp})
    channel.basic_publish(exchange='', routing_key='numbers', body=message)
    print(f"Published: {message}")

if __name__ == '__main__':
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='numbers')

    try:
        while True:
            number = generate_random_number()
            publish_number(channel, number)
            time.sleep(PUBLISH_INTERVAL)
    except KeyboardInterrupt:
        connection.close()