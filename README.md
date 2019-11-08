# Getting Started
You'll need the MinIO Client (mc) as well as docker-compose. Clone this repo, then:
```
# Up Everything
docker-compose up

# Go here to see queue - http://localhost:15672/#/queues/%2F/raw-media-bucket

# Create activity in localhost/raw-media-bucket to see events
mc config host add localhost http://localhost:9000 TESTINGTESTING123 TESTINGTESTING123TESTINGTESTING123
mc admin config set localhost < ./init/minio.config
mc admin service restart localhost
watch -n 0.5  mc cp README.md localhost/raw-media-bucket/README.md
```
