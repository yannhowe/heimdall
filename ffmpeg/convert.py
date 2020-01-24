import os
import pika
import json
import ffmpeg
from minio import Minio
from minio.error import ResponseError

# Connect to Rabbit MQ
rabbitmq_host           = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_username       = os.getenv('RABBITMQ_USERNAME', 'Token Not found')
rabbitmq_password       = os.getenv('RABBITMQ_PASSWORD', 'Token Not found')
rabbitmq_exchange_name  = os.getenv('RABBITMQ_MINIO_EXCHANGE', 'Token Not found')
rabbitmq_queue_name     = os.getenv('RABBITMQ_MINIO_QUEUE', 'Token Not found')

credentials     = pika.credentials.PlainCredentials(rabbitmq_username, rabbitmq_password, erase_on_connect = False)
connection      = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials = credentials))
channel         = connection.channel()

rabbitmq_queue_name = os.getenv('RABBITMQ_MINIO_QUEUE', 'Token Not found')

channel.queue_declare(queue=rabbitmq_queue_name)

# Connect to MinIO
minioClient = Minio(os.getenv('MINIO_HOST', 'Token Not found'),
    access_key = os.getenv('MINIO_ACCESS_KEY', 'Token Not found'),
    secret_key = os.getenv('MINIO_SECRET_KEY', 'Token Not found'),
    secure=False
)


if minioClient.bucket_exists(os.getenv('CONVERTED_MEDIA_BUCKET', 'Token Not found')):
    print("bucket %s exists" % os.getenv('CONVERTED_MEDIA_BUCKET', 'Token Not found'))
else:
    try:
        minioClient.make_bucket(os.getenv('CONVERTED_MEDIA_BUCKET', 'Token Not found'))
    except ResponseError as err:
        print(err)


def callback(ch, method, properties, body):
    event = json.loads(body)
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    object_name = event["Records"][0]["s3"]["object"]["key"]
    file_to_convert_name = bucket_name+"-"+object_name
    file_converted_name = bucket_name+"-"+object_name+".converted.wav"

    print(event)
    if minioClient.bucket_exists(os.getenv('RAW_MEDIA_BUCKET', 'Token Not found')):

        try:
            data = minioClient.get_object(os.getenv('RAW_MEDIA_BUCKET', 'Token Not found'), object_name)
            with open("/tmp/"+file_to_convert_name, 'wb') as file_data:
                for d in data.stream(32*1024):
                    file_data.write(d)
            ffmpeg.input("/tmp/"+file_to_convert_name).output("/tmp/"+file_converted_name, acodec='pcm_s16le', ac=1, ar='8000').run()
            os.remove("/tmp/"+file_to_convert_name)
        except ResponseError as err:
            os.remove("/tmp/"+file_to_convert_name)
            print(err)
    
    if minioClient.bucket_exists(os.getenv('CONVERTED_MEDIA_BUCKET', 'Token Not found')):        
        try:
            with open("/tmp/"+file_converted_name, 'rb') as file_data:
                file_stat = os.stat("/tmp/"+file_converted_name)
                print(minioClient.put_object(os.getenv('CONVERTED_MEDIA_BUCKET', 'Token Not found'), file_converted_name,
                                    file_data, file_stat.st_size))
            os.remove("/tmp/"+file_converted_name)
        except ResponseError as err:
            os.remove("/tmp/"+file_converted_name)
            print(err)


channel.basic_consume(queue=rabbitmq_queue_name,
                      auto_ack=True,
                      on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()