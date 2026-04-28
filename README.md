HEAD
Link for docker web:
http://127.0.0.1:8080/

Link for fastkoko web:
http://127.0.0.1:8880/web/

good audio:
am_michael

## Run for the web docker interface
docker run -d --gpus all --network=host -v open-webui:/app/backend/data -e OLLAMA_BASE_URL=http://127.0.0.1:11434 --name open-webui --restart always ghcr.io/open-webui/open-webui:main

## Run for the voice backend
docker run -d --gpus all --network=host -v open-webui:/app/backend/data -e OLLAMA_BASE_URL=http://127.0.0.1:11434 --name kokoro-tts ghcr.io/rushyrush/kokoro-fastapi-gpu:v0.3.0

# voice
