import os
import pika
import docker
import json

# Connect to docker
docker_session = docker.from_env()

# Connect to Rabbit MQ
rabbitmq_host = "localhost"
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'Token Not found')
rabbitmq_username = os.getenv('RABBITMQ_USERNAME', 'Token Not found')
rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'Token Not found')
rabbitmq_exchange_name = os.getenv('RABBITMQ_MINIO_EXCHANGE', 'Token Not found')
rabbitmq_queue_name = os.getenv('RABBITMQ_MINIO_QUEUE', 'Token Not found')

credentials = pika.credentials.PlainCredentials(rabbitmq_username, rabbitmq_password, erase_on_connect = False)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials = credentials))
channel = connection.channel()

rabbitmq_queue_name = os.getenv('RABBITMQ_MINIO_QUEUE', 'Token Not found')

channel.queue_declare(queue=rabbitmq_queue_name)

def callback(ch, method, properties, body):
    event = json.loads(body)
    print(event["Key"])
    print("hello world")
    docker_session.containers.run("alpine", "echo hello")

channel.basic_consume(queue=rabbitmq_queue_name,
                      auto_ack=True,
                      on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()