# ChatVLMLLM API Guide

Complete REST API documentation for ChatVLMLLM.

## Quick Start

### Start API Server

```bash
# Development
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

# Docker
docker-compose up -d api
```

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### GET `/`

API information.

**Response:**
```json
{
  "message": "ChatVLMLLM API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

### GET `/health`

Health check with GPU status.

**Response:**
```json
{
  "status": "healthy",
  "gpu_available": true,
  "gpu_name": "NVIDIA GeForce RTX 5070",
  "models_loaded": 2,
  "loaded_models": ["qwen3_vl_2b", "got_ocr"]
}
```

### GET `/models`

List available models.

**Response:**
```json
{
  "available": [
    {"id": "got_ocr", "name": "GOT-OCR 2.0", "params": "580M"},
    {"id": "qwen3_vl_2b", "name": "Qwen3-VL 2B", "params": "2B"},
    ...
  ],
  "loaded": ["qwen3_vl_2b"]
}
```

### POST `/ocr`

Extract text from image.

**Parameters:**
- `file` (required): Image file
- `model` (optional): Model name (default: `qwen3_vl_2b`)
- `language` (optional): Language hint

**Example:**
```bash
curl -X POST "http://localhost:8000/ocr?model=qwen3_vl_2b" \
  -F "file=@document.jpg"
```

**Response:**
```json
{
  "text": "Extracted text content...",
  "model": "qwen3_vl_2b",
  "processing_time": 1.23,
  "image_size": [1920, 1080],
  "language": null
}
```

### POST `/chat`

Chat with VLM about an image.

**Parameters:**
- `file` (required): Image file
- `prompt` (required): User prompt
- `model` (optional): Model name (default: `qwen3_vl_2b`)
- `temperature` (optional): 0.0-1.0 (default: 0.7)
- `max_tokens` (optional): Max tokens (default: 512)

**Example:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -F "file=@image.jpg" \
  -F "prompt=What's in this image?" \
  -F "model=qwen3_vl_4b" \
  -F "temperature=0.7"
```

**Response:**
```json
{
  "response": "This image shows...",
  "model": "qwen3_vl_4b",
  "processing_time": 2.45,
  "prompt": "What's in this image?"
}
```

### POST `/batch/ocr`

Batch OCR processing.

**Parameters:**
- `files` (required): List of image files
- `model` (optional): Model name

**Example:**
```bash
curl -X POST "http://localhost:8000/batch/ocr?model=qwen3_vl_2b" \
  -F "files=@doc1.jpg" \
  -F "files=@doc2.jpg" \
  -F "files=@doc3.jpg"
```

**Response:**
```json
{
  "results": [
    {
      "filename": "doc1.jpg",
      "text": "...",
      "processing_time": 1.2,
      "status": "success"
    },
    ...
  ],
  "total": 3,
  "successful": 3,
  "failed": 0
}
```

### DELETE `/models/{model_name}`

Unload model from memory.

**Example:**
```bash
curl -X DELETE "http://localhost:8000/models/qwen3_vl_8b"
```

**Response:**
```json
{
  "status": "success",
  "message": "Model qwen3_vl_8b unloaded"
}
```

## Python Client

### Installation

```bash
pip install requests
```

### Basic Usage

```python
import requests

# OCR
with open('document.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/ocr',
        files={'file': f},
        params={'model': 'qwen3_vl_2b'}
    )
    print(response.json()['text'])

# Chat
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/chat',
        files={'file': f},
        data={
            'prompt': 'Describe this image',
            'model': 'qwen3_vl_4b',
            'temperature': 0.7
        }
    )
    print(response.json()['response'])

# Batch
files = [
    ('files', open('doc1.jpg', 'rb')),
    ('files', open('doc2.jpg', 'rb'))
]
response = requests.post(
    'http://localhost:8000/batch/ocr',
    files=files,
    params={'model': 'qwen3_vl_2b'}
)
print(f"Processed {response.json()['successful']} files")
```

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message"
}
```

### Status Codes

- `200`: Success
- `400`: Bad request
- `404`: Not found
- `500`: Server error

### Example Error Handling

```python
try:
    response = requests.post('http://localhost:8000/ocr', ...)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Detail: {e.response.json()['detail']}")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Tips

### Model Selection

| VRAM | Recommended Model | Speed | Quality |
|------|------------------|-------|----------|
| 8 GB | qwen3_vl_2b | Fast | Good |
| 12 GB | qwen3_vl_4b | Medium | Better |
| 16 GB+ | qwen3_vl_8b | Slower | Best |

### Batch Processing

```python
# Process multiple files efficiently
import glob
from pathlib import Path

files = []
for path in glob.glob('documents/*.jpg'):
    files.append(('files', open(path, 'rb')))

response = requests.post(
    'http://localhost:8000/batch/ocr',
    files=files
)

for result in response.json()['results']:
    if result['status'] == 'success':
        print(f"{result['filename']}: {result['text'][:100]}...")
```

### Concurrent Requests

```python
import concurrent.futures
import requests

def process_image(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/ocr',
            files={'file': f}
        )
        return response.json()

image_paths = ['img1.jpg', 'img2.jpg', 'img3.jpg']

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_image, image_paths))
```

## Docker Deployment

### docker-compose.yml

```yaml
version: '3.8'
services:
  api:
    build: .
    command: uvicorn api:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Start Services

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop
docker-compose down
```

## Security

### Future Features

- API key authentication
- Rate limiting
- Request validation
- HTTPS support

### Current Setup

⚠️ **Warning**: Current API has no authentication. Use behind firewall or add nginx proxy with auth.

## Monitoring

### Health Check

```bash
# Simple check
curl http://localhost:8000/health

# Monitor GPU
watch -n 1 'curl -s http://localhost:8000/health | jq'
```

### Logging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Troubleshooting

### Out of Memory

```bash
# Use smaller model
curl -X DELETE http://localhost:8000/models/qwen3_vl_8b

# Load smaller model
curl -X POST http://localhost:8000/ocr?model=qwen3_vl_2b -F "file=@test.jpg"
```

### Slow Response

- Use smaller model
- Enable Flash Attention in config.yaml
- Use INT8/INT4 quantization
- Check GPU utilization: `nvidia-smi`

### Model Not Found

```bash
# Check available models
curl http://localhost:8000/models

# Download model first
python -c "from models import ModelLoader; ModelLoader.load_model('qwen3_vl_2b')"
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Swagger UI](http://localhost:8000/docs)
- [GPU Requirements](gpu_requirements.md)
- [Qwen3-VL Guide](qwen3_vl_guide.md)