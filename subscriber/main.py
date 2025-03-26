import pika
import psycopg
import json
from datetime import datetime
import os
import time

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'postgres')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'pguser')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'pgpassword')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'subscriber_db')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'admin')
RETRY_INTERVAL = int(os.environ.get('RETRY_INTERVAL', 1))

def process_and_store(channel, method, properties, body):
    try:
        message = json.loads(body)
        number = message["value"]
        message_timestamp = message["timestamp"]
        result = number ** 2
        processed_timestamp = datetime.now().isoformat()
        print(f"Received: {message}, Result: {result}, Processed at: {processed_timestamp}", flush=True)

        conn = psycopg.connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO results (number, result, message_timestamp, processed_timestamp) VALUES (%s, %s, %s, %s)",
                (number, result, message_timestamp, processed_timestamp)
            )
        conn.commit()
        conn.close()

    except psycopg.Error as e:
        print(f"Database error: {e}", flush=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True) # Requeue the message
        return

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", flush=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False) # Discard the message
        return

    except Exception as e:
        print(f"General error: {e}", flush=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True) # Requeue the message
        return

    channel.basic_ack(delivery_tag=method.delivery_tag)

def connect_to_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='numbers')
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ: {e}. Retrying in {RETRY_INTERVAL} seconds...", flush=True)
        return None, None

if __name__ == '__main__':
    connection, channel = connect_to_rabbitmq()

    while connection is None or channel is None:
        time.sleep(RETRY_INTERVAL)
        connection, channel = connect_to_rabbitmq()

    try:
        channel.basic_consume(queue='numbers', on_message_callback=process_and_store)
        print('Waiting for messages...', flush=True)
        channel.start_consuming()
    except Exception as e:
        print(f"Error: {e}", flush=True)
    finally:
        if connection and connection.is_open:
            connection.close()