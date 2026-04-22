# Download Qwen2.5-Coder-1.5B-Instruct-GGUF
# Requirements: pip install huggingface-hub

echo "Downloading Qwen2.5-Coder-1.5B-Instruct-GGUF..."
mkdir -p models
huggingface-cli download Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF qwen2.5-coder-1.5b-instruct-q4_k_m.gguf --local-dir models --local-dir-use-symlinks False
