# Connection info
host_ip=$(hostname -I | awk '{print $1}') no_proxy=localhost LLM_ENDPOINT_PORT=8008 LLM_MODEL_ID="llama3.2:1b" docker compose up


## Pull a model
curl http://localhost:8008/api/pull -d '{
  "model": "llama3.2:1b"
}'

## Generate a request
curl http://localhost:8008/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "Why is the sky blue?"
}'