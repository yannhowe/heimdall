import pika
import os

rabbiitmq_host= os.getenv('RABBITMQ_HOST', 'Token Not found')
rabbiitmq_username = os.getenv('RABBITMQ_USERNAME', 'Token Not found')
rabbiitmq_password = os.getenv('RABBITMQ_PASSWORD', 'Token Not found')
rabbiitmq_exchange_name = os.getenv('RABBITMQ_MINIO_EXCHANGE', 'Token Not found')
rabbiitmq_queue_name = os.getenv('RABBITMQ_MINIO_QUEUE', 'Token Not found')

credentials = pika.credentials.PlainCredentials(rabbiitmq_username, rabbiitmq_password, erase_on_connect=False)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbiitmq_host, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange=rabbiitmq_exchange_name, exchange_type='fanout')

result = channel.queue_declare(rabbiitmq_queue_name, exclusive=False)

#channel.queue_bind(exchange=rabbiitmq_exchange_name, queue=rabbiitmq_queue_name)

#print(' [*] Waiting for logs. To exit press CTRL+C')
#
#def callback(ch, method, properties, body):
#    print(" [x] %r" % body)
#
#channel.basic_consume(rabbiitmq_queue_name, callback, auto_ack=False)
#
#channel.start_consuming()