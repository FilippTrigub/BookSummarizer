docker compose build;

az acr login -n audiosummarizerAcr;

docker compose push;
