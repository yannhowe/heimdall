chmod +x ./mc
./mc config host add localhost http://$MINIO_HOST $MINIO_ACCESS_KEY $MINIO_SECRET_KEY
./mc admin config set localhost < minio.config
./mc admin service restart localhost
python ./init.py