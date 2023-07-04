# Stage 1 - Build the UI
FROM debian:latest AS ui-build

ENV DEBIAN_FRONTEND=noninteractive
ARG API_URI=localhost
ENV API_URI=$API_URI

RUN apt-get update
RUN apt-get install -y curl git wget unzip libgconf-2-4 gdb libstdc++6 libglu1-mesa fonts-droid-fallback lib32stdc++6 python3 sed
RUN apt-get clean

RUN git clone https://github.com/flutter/flutter.git /usr/local/flutter
ENV PATH="${PATH}:/usr/local/flutter/bin:/usr/local/flutter/bin/cache/dart-sdk/bin"
RUN flutter doctor
RUN flutter channel master
RUN flutter upgrade --force
RUN flutter config --enable-web

COPY UI/ /app/
WORKDIR /app
RUN flutter build web --dart-define=API_URI=$API_URI

# Stage 2 - Build the API
FROM python:3.10.12-slim AS api-build

COPY app/ /app/
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade

# Stage 3 - Build the final image
FROM ubuntu:latest

# Install nginx
RUN apt-get update && apt-get install -y nginx

# Install Python and pip
RUN apt-get install -y python3 python3-pip

# Copy the API from the api-build stage
COPY --from=api-build /app /app

# Install API dependencies
RUN pip3 install -r /app/requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg --fix-missing

# Copy the UI from the ui-build stage
COPY --from=ui-build /app/build/web /usr/share/nginx/html

# Set up nginx configuration
COPY nginx.conf /etc/nginx/sites-available/default

# Expose the necessary ports
EXPOSE 80 8081

# Start both nginx and the API
CMD service nginx start && uvicorn main:app --app-dir app/ --host 0.0.0.0 --port 8081
