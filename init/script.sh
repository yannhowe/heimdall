if [ "$(uname)" == "Darwin" ]; then
    chmod +x ./mc_macos
    ./mc_macos config host add localhost http://$MINIO_HOST $MINIO_ACCESS_KEY $MINIO_SECRET_KEY
    ./mc_macos admin config set localhost < minio.config
    ./mc_macos admin service restart localhost
    python ./init.py
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    chmod +x ./mc_linux
    ./mc_linux config host add localhost http://$MINIO_HOST $MINIO_ACCESS_KEY $MINIO_SECRET_KEY
    ./mc_linux admin config set localhost < minio.config
    ./mc_linux admin service restart localhost
    python ./init.py
fi