#!/bin/bash

echo "Deploying URL Shortener to Docker Swarm..."

# Инициализация Swarm (если еще не инициализирован)
if [ -z "$(docker info | grep Swarm | grep active)" ]; then
    echo "Initializing Docker Swarm..."
    docker swarm init
fi

# Развертывание стека
echo "Deploying stack..."
docker stack deploy -c docker-compose-swarm.yml url-shortener-stack

echo "Deployment completed!"
echo "Check services: docker service ls"
echo "Check logs: docker service logs url-shortener-stack_nginx"