import pika
import random
import time
import json
from datetime import datetime
import os

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
PUBLISH_INTERVAL = float(os.environ.get('PUBLISH_INTERVAL', 1))
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'admin')
RETRY_INTERVAL = int(os.environ.get('RETRY_INTERVAL', 1))

def generate_random_number():
    return random.randint(1, 100)

def publish_number(channel, number):
    timestamp = datetime.now().isoformat()
    message = json.dumps({"value": number, "timestamp": timestamp})
    channel.basic_publish(exchange='', routing_key='numbers', body=message)
    print(f"Published: {message}", flush=True)

def connect_to_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='numbers')
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ: {e}. Retrying in {RETRY_INTERVAL} seconds...")
        return None, None

if __name__ == '__main__':
    connection, channel = connect_to_rabbitmq()

    while connection is None or channel is None:
        time.sleep(RETRY_INTERVAL)
        connection, channel = connect_to_rabbitmq()

    try:
        while True:
            number = generate_random_number()
            publish_number(channel, number)
            time.sleep(PUBLISH_INTERVAL)
    except KeyboardInterrupt:
        if connection and connection.is_open:
            connection.close()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if connection and connection.is_open:
            connection.close()