docker compose build;

az acr login -n trigubtechnologiesprojectsacr;

docker compose push;

# az acr login -n trigubtechnologiesprojectsacr && docker compose build && docker compose push