#!/bin/bash

echo "Download models and demo data"
dvc pull
echo "Done"

echo "Models:"
find ./source/models/ -name "*.pkl"
echo "Datasource:"
find ./source/data/ -name "*.csv"

echo "Run application"
docker-compose up -d 

echo "Wait"
sleep 10
echo "Run next"

echo "Init database"
docker-compose exec app python ./models/model.py

docker-compose exec app ./demo_init.sh

echo "Demo configuration is done"