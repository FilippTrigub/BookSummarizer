FROM python:3.10.12-slim

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg --fix-missing

# Necessary for SSH to Azure
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
