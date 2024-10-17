#!/bin/bash

# Model service on port 6006
echo "Starting model service on port 6006..."
cd /root/autodl-tmp/AUG/
python api.py &
sleep 2

# Backend service on port 5000
echo "Starting backend service on port 5000..."
cd /root/autodl-tmp/bushu/AUG/web_demo/server/
python app.py &
sleep 2

# Frontend service on port 8080
echo "Starting frontend service on port 8080..."
cd /root/autodl-tmp/bushu/AUG/web_demo/client/
npm run serve &
sleep 2

# PlantUML service on port 8888
echo "Starting PlantUML service on port 8888..."
cd /root/autodl-tmp/bushu/AUG/puml_serve/
java -jar plantuml.jar -picoweb:8888 &
sleep 2

echo "All services started."
