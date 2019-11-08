import pika
import os
from minio import Minio
from minio.error import ResponseError

# Initialise Rabbit MQ
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'Token Not found')
rabbitmq_username = os.getenv('RABBITMQ_USERNAME', 'Token Not found')
rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'Token Not found')
rabbitmq_exchange_name = os.getenv('RABBITMQ_MINIO_EXCHANGE', 'Token Not found')
rabbitmq_queue_name = os.getenv('RABBITMQ_MINIO_QUEUE', 'Token Not found')

credentials = pika.credentials.PlainCredentials(rabbitmq_username, rabbitmq_password, erase_on_connect = False)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials = credentials))
channel = connection.channel()

channel.exchange_declare(exchange = rabbitmq_exchange_name, exchange_type = 'fanout')

result = channel.queue_declare(rabbitmq_queue_name, exclusive = False)

channel.queue_bind(exchange = rabbitmq_exchange_name, queue = rabbitmq_queue_name)


# Initialise MinIO
minioClient = Minio(os.getenv('MINIO_HOST', 'Token Not found'),
    access_key = os.getenv('MINIO_ACCESS_KEY', 'Token Not found'),
    secret_key = os.getenv('MINIO_SECRET_KEY', 'Token Not found'),
    secure=False
)

notification = {
    'QueueConfigurations': [{
        'Id': "1",
        'Arn': 'arn:minio:sqs::1:amqp',
        'Events': ['s3:ObjectCreated:*', 's3:ObjectRemoved:*', 's3:ObjectAccessed:*']
    }]
}

if minioClient.bucket_exists(os.getenv('RAW_MEDIA_BUCKET', 'Token Not found')):
    print("bucket %s exists" % os.getenv('RAW_MEDIA_BUCKET', 'Token Not found'))
else:
    try:
        minioClient.make_bucket(os.getenv('RAW_MEDIA_BUCKET', 'Token Not found'))
    except ResponseError as err:
        print(err)

try:
    minioClient.set_bucket_notification(os.getenv('RAW_MEDIA_BUCKET', 'Token Not found'), notification)
    print(minioClient.get_bucket_notification(os.getenv('RAW_MEDIA_BUCKET', 'Token Not found')))
except ResponseError as err:
    # handle error response from service.
    print(err)