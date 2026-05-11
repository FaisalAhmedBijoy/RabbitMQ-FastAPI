# Development Guide

## Local Development Setup

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Git
- Visual Studio Code (optional but recommended)

### Option 1: Full Docker Setup (Recommended)

This is the easiest way to get started.

```bash
# 1. Clone/navigate to project
cd /Users/faisal/Documents/RND/RabbitMQ-FastAPI

# 2. Start all services
docker-compose up --build

# 3. In another terminal, test the API
bash test_api.sh
```

**Advantages:**
- No local dependencies needed
- Exactly matches production environment
- Easy to scale services
- Simple container management

### Option 2: Local Python Development

For development with live code reloading:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start RabbitMQ (with Docker)
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3.12-management-alpine

# 4. Start FastAPI (Terminal 1)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Start workers (in separate terminals)
python -m app.workers.resize_worker
python -m app.workers.thumbnail_worker
python -m app.workers.ocr_worker
python -m app.workers.ai_tagging_worker
```

**Advantages:**
- Faster iteration with code reload
- Better debugging capabilities
- Easier to modify code
- Direct worker process access

### Option 3: Hybrid Setup

RabbitMQ in Docker, Python services locally:

```bash
# Start only RabbitMQ
docker-compose up rabbitmq -d

# Then run Python services locally as in Option 2
```

## Development Workflow

### 1. Code Changes and Reload

**With Docker:**
```bash
# Code changes are automatically reflected with volume mounts
docker-compose up api

# Check logs for changes
docker-compose logs -f api
```

**Locally:**
```bash
# FastAPI automatically reloads with --reload flag
uvicorn app.main:app --reload

# Workers need manual restart
# Stop (Ctrl+C) and restart each worker
```

### 2. Testing Changes

```bash
# Test your changes
bash test_api.sh

# Monitor specific worker
docker-compose logs -f resize_worker_1

# Check RabbitMQ UI
# http://localhost:15672
```

### 3. Debugging

**View Logs:**
```bash
# All logs
docker-compose logs

# Specific service
docker-compose logs api
docker-compose logs resize_worker_1

# Follow in real-time
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail 100

# Grep specific error
docker-compose logs | grep ERROR
```

**Inspect Containers:**
```bash
# Connect to container shell
docker-compose exec api /bin/bash

# Run Python commands
docker-compose exec api python -c "import pika; print(pika.__version__)"

# Check environment variables
docker-compose exec api env
```

**Monitor RabbitMQ:**
```bash
# Access management UI
curl http://localhost:15672/api/overview

# List queues
curl -u guest:guest http://localhost:15672/api/queues

# Monitor message rates
watch -n 1 'curl -s -u guest:guest http://localhost:15672/api/overview | python -m json.tool'
```

### 4. Modifying Code

**Add a New Endpoint:**
```python
# In app/main.py

@app.get("/custom-endpoint")
async def custom_endpoint():
    return {"message": "Custom endpoint"}
```

**Add a New Worker:**
```python
# Create app/workers/custom_worker.py

from app.workers.base import BaseWorker
from app.config import RABBITMQ_CONFIG

class CustomWorker(BaseWorker):
    def __init__(self):
        super().__init__("custom_queue", "CustomWorker")
    
    def process(self, message):
        # Your custom processing logic
        return {"status": "completed"}

if __name__ == "__main__":
    worker = CustomWorker()
    worker.start_consuming()
```

**Update Configuration:**
```python
# In app/config.py

CUSTOM_QUEUE = "custom_queue"
# Then set up the queue in app/queues/__init__.py
```

## Testing

### Unit Testing

```python
# Create tests/test_schemas.py

import pytest
from app.schemas.image import ImageUploadRequest

def test_image_upload_request():
    request = ImageUploadRequest(
        image_id=1,
        filename="test.jpg",
        image_path="/path/to/test.jpg",
        image_size="5MB"
    )
    assert request.image_id == 1
    assert request.filename == "test.jpg"
```

**Run tests:**
```bash
pytest tests/
pytest tests/test_schemas.py -v
```

### Integration Testing

```bash
# Test with live RabbitMQ
bash test_api.sh

# Monitor results
docker-compose logs -f
```

### Load Testing

```python
# Create tests/load_test.py

import concurrent.futures
import requests
import time

def send_image(image_id):
    response = requests.post(
        "http://localhost:8000/upload-image",
        json={
            "image_id": image_id,
            "filename": f"image_{image_id}.jpg",
            "image_path": f"/uploads/image_{image_id}.jpg",
            "image_size": "5MB"
        }
    )
    return response.status_code

if __name__ == "__main__":
    # Send 100 images in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_image, i) for i in range(100)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    print(f"Sent 100 images. Success: {results.count(200)}")
```

**Run load test:**
```bash
python tests/load_test.py
```

## Project Structure Notes

### Core Modules

- **app/main.py** - FastAPI application entry point
- **app/config.py** - All configuration settings
- **app/rabbitmq/** - RabbitMQ connection management
- **app/producers/** - Message publishing logic
- **app/workers/** - Consumer workers
- **app/queues/** - Queue setup and initialization
- **app/schemas/** - Pydantic models for validation
- **app/utils/** - Helper functions and logging

### Key Files to Understand

1. **Start here:** `app/main.py` - Understand the API layer
2. **Then:** `app/rabbitmq/connection.py` - How we connect to RabbitMQ
3. **Then:** `app/producers/__init__.py` - How we publish messages
4. **Then:** `app/workers/base.py` - The worker pattern
5. **Finally:** `app/workers/resize_worker.py` - Example worker implementation

## Common Development Tasks

### Task 1: Add Logging to a Worker

```python
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class MyWorker(BaseWorker):
    def process(self, message):
        logger.info(f"Processing image {message['image_id']}")
        
        try:
            # Do work
            logger.info("Work completed successfully")
            return {"status": "completed"}
        except Exception as e:
            logger.error(f"Work failed: {str(e)}")
            raise
```

### Task 2: Add Configuration Option

```python
# In app/config.py

@dataclass
class RabbitMQConfig:
    MY_NEW_SETTING: str = os.getenv("MY_NEW_SETTING", "default_value")

# Use it
from app.config import RABBITMQ_CONFIG
value = RABBITMQ_CONFIG.MY_NEW_SETTING
```

### Task 3: Add New Queue

```python
# In app/queues/__init__.py

def declare_queues():
    channel = get_rabbitmq_channel()
    channel.queue_declare(
        queue='my_new_queue',
        durable=True,
        auto_delete=False
    )
```

### Task 4: Monitor Queue Depth

```bash
# Check specific queue
curl -u guest:guest http://localhost:15672/api/queues/%2F/resize_queue

# Parse with Python
curl -s -u guest:guest http://localhost:15672/api/queues/%2F/resize_queue | \
  python -c "import sys, json; data=json.load(sys.stdin); print(f'Messages: {data[\"messages\"]}')"
```

## Troubleshooting During Development

### Issue: "Connection refused" to RabbitMQ

```bash
# Check if RabbitMQ is running
docker-compose ps rabbitmq

# If not running, start it
docker-compose up -d rabbitmq

# Check RabbitMQ logs
docker-compose logs rabbitmq
```

### Issue: Code changes not reflecting

**With Docker:**
```bash
# Rebuild images if requirements.txt changed
docker-compose up --build

# Restart services
docker-compose restart
```

**Locally:**
```bash
# Reinstall packages if requirements changed
pip install -r requirements.txt

# Restart the service (Ctrl+C and rerun)
```

### Issue: Worker not processing messages

```bash
# Check if worker is running
docker-compose ps resize_worker_1

# Check worker logs
docker-compose logs resize_worker_1

# Verify connection to RabbitMQ
docker-compose exec resize_worker_1 python -c "
import pika
creds = pika.PlainCredentials('guest', 'guest')
params = pika.ConnectionParameters('rabbitmq', credentials=creds)
conn = pika.BlockingConnection(params)
print('Connected!')
conn.close()
"
```

### Issue: Too much memory usage

```bash
# Check container stats
docker stats

# Reduce prefetch_count in app/config.py
PREFETCH_COUNT = 1  # Don't increase this

# Limit Docker container memory
# In docker-compose.yml:
# services:
#   api:
#     deploy:
#       resources:
#         limits:
#           memory: 512M
```

## Performance Profiling

```bash
# Profile Python code
pip install py-spy

# Run worker with profiling
py-spy record -o profile.svg -- python -m app.workers.resize_worker

# Analyze with Flamegraph
# Open profile.svg in browser
```

## Docker Best Practices

### 1. Use specific versions

```dockerfile
FROM python:3.11-slim
RUN pip install fastapi==0.109.0
```

### 2. Multi-stage builds (optional)

```dockerfile
FROM python:3.11 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
```

### 3. Health checks

```yaml
rabbitmq:
  healthcheck:
    test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
    interval: 30s
    timeout: 10s
    retries: 5
```

## IDE Setup

### VS Code Extensions

1. **Python** - ms-python.python
2. **Docker** - ms-vscode.docker
3. **Rest Client** - humao.rest-client
4. **Better Comments** - aaron-bond.better-comments

### Run Configurations

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true,
      "console": "integratedTerminal"
    },
    {
      "name": "Resize Worker",
      "type": "python",
      "request": "launch",
      "module": "app.workers.resize_worker",
      "console": "integratedTerminal"
    }
  ]
}
```

## Next Steps

1. **Understand the flow:** Run the project and monitor logs
2. **Modify a worker:** Change delay times or failure rates
3. **Add a queue:** Create a new processing queue
4. **Write tests:** Add unit and integration tests
5. **Optimize:** Profile and improve performance

Happy developing! 🚀
