#!/bin/bash

# Set the port
PORT=5000

# Stop any program currently running on the set port
echo 'preparing port' $PORT '...'
fuser -k 5000/tcp

# switch directories
cd build/web/

# Start the server
echo 'Starting app'
flutter run -d chrome
