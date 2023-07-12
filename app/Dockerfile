FROM python:3.10.12-slim

WORKDIR /app

COPY .env.template .env
COPY __init__.py __init__.py
COPY main.py main.py
COPY src src
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg --fix-missing

EXPOSE 8081

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
