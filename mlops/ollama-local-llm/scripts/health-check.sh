#!/bin/bash
# Ollama Health Check Script
# Run this to verify Ollama installation and functionality

set -e

echo "==================================="
echo "    Ollama Health Check"
echo "==================================="
echo ""

# 1. Version check
echo "1. Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "   ✓ Ollama version: $(ollama --version)"
else
    echo "   ✗ Ollama not found in PATH"
    echo "   Install with: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi
echo ""

# 2. Service status
echo "2. Checking Ollama service..."
if ps aux | grep -v grep | grep ollama > /dev/null; then
    echo "   ✓ Ollama service is running"
else
    echo "   ✗ Ollama service is NOT running"
    echo "   Start with: systemctl start ollama"
    exit 1
fi
echo ""

# 3. GPU detection (Linux only)
echo "3. Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi &> /dev/null; then
        echo "   ✓ NVIDIA GPU detected"
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader | sed 's/^/     /'
    else
        echo "   ⚠ nvidia-smi exists but failed to run"
    fi
else
    echo "   ⚠ nvidia-smi not found (CPU-only or Apple Silicon)"
fi
echo ""

# 4. Model list
echo "4. Checking installed models..."
MODEL_COUNT=$(ollama list 2>/dev/null | tail -n +2 | wc -l)
if [ "$MODEL_COUNT" -gt 0 ]; then
    echo "   ✓ Found $MODEL_COUNT model(s):"
    ollama list | tail -n +2 | head -n 5 | sed 's/^/     /'
    if [ "$MODEL_COUNT" -gt 5 ]; then
        echo "     ... and $((MODEL_COUNT - 5)) more"
    fi
else
    echo "   ⚠ No models installed"
    echo "   Pull one with: ollama pull qwen2.5:3b"
fi
echo ""

# 5. Port availability
echo "5. Checking API endpoint (port 11434)..."
if command -v curl &> /dev/null; then
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "   ✓ API is responding on http://localhost:11434"
    else
        echo "   ✗ API is not responding"
    fi
else
    echo "   ⚠ curl not found, skipping API check"
fi
echo ""

# 6. Inference test (if models available)
if [ "$MODEL_COUNT" -gt 0 ]; then
    echo "6. Testing inference..."
    # Get first model name
    FIRST_MODEL=$(ollama list | tail -n +2 | head -n 1 | awk '{print $1}')
    echo "   Testing with model: $FIRST_MODEL"
    
    RESPONSE=$(echo "Say 'OK' in one word." | ollama run "$FIRST_MODEL" 2>/dev/null | tr -d '\n' | head -c 100)
    
    if [ -n "$RESPONSE" ]; then
        echo "   ✓ Inference working"
        echo "     Response: $RESPONSE"
    else
        echo "   ✗ Inference failed or returned empty"
    fi
else
    echo "6. Skipping inference test (no models)"
fi
echo ""

# 7. Disk space
echo "7. Checking disk space..."
MODELS_DIR="$HOME/.ollama/models"
if [ -d "$MODELS_DIR" ]; then
    SIZE=$(du -sh "$MODELS_DIR" 2>/dev/null | cut -f1)
    echo "   Models directory: $MODELS_DIR"
    echo "   Total size: $SIZE"
else
    echo "   ⚠ Models directory not found yet"
fi
echo ""

echo "==================================="
echo "Health check complete!"
echo "==================================="
