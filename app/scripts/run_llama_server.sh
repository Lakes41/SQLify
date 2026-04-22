# Start llama.cpp server
# Assumes llama-server is in your PATH or current directory

MODEL_PATH="models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"

if [ ! -f "$MODEL_PATH" ]; then
    echo "Model not found at $MODEL_PATH. Please run download_model.sh first."
    exit 1
fi

echo "Starting llama-server on port 8080..."
llama-server -m "$MODEL_PATH" --port 8080 --ctx-size 4096 --n-gpu-layers 0
