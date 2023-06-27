FROM python:3.10.12-slim

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg --fix-missing

# Necessary for SSH to Azure
EXPOSE 2222 80

EXPOSE 5555

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5555"]

HEALTHCHECK --interval=5m --timeout=3s CMD curl -f http://localhost:80/ || exit 1
