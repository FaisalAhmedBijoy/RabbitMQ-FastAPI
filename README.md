# Async Image Processing Pipeline with RabbitMQ

A complete beginner-to-intermediate level backend project demonstrating asynchronous processing, distributed workers, and message queue architecture using RabbitMQ and FastAPI.

## Table of Contents

- [Overview](#overview)
- [Learning Objectives](#learning-objectives)
- [System Architecture](#system-architecture)
- [RabbitMQ Concepts](#rabbitmq-concepts)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Advanced Features](#advanced-features)

## Overview

This project simulates a real-world image processing backend similar to systems used in social media platforms, AI services, cloud storage, and OCR solutions.

### Key Features

- **Non-blocking APIs**: FastAPI returns immediately while RabbitMQ handles processing
- **Multiple Workers**: Parallel processing with competing consumers pattern
- **Fault Tolerance**: ACK/NACK, retry logic, and Dead Letter Queues
- **Scalability**: Easily scale workers by running multiple instances
- **Production-Ready**: Durable queues and persistent messages
- **Docker Integration**: Complete containerization for all services

## Learning Objectives

After completing this project, you'll understand:

### RabbitMQ Concepts

1. **Producer** - FastAPI publishes messages to queues
2. **Consumer** - Workers consume messages from queues
3. **Queue** - Message storage with FIFO behavior
4. **Durable Queue** - Persists through RabbitMQ restarts
5. **Persistent Messages** - Messages survive broker restarts (delivery_mode=2)
6. **ACK/NACK** - Acknowledging successful processing or rejecting failed tasks
7. **Retry Queue** - Automatic retry mechanism for failed jobs
8. **Dead Letter Queue (DLQ)** - Storage for permanently failed messages
9. **Competing Consumers** - Multiple workers consuming same queue
10. **Fair Dispatch** - Prefetch count ensures fair task distribution
11. **Exchanges** - Message routing (direct, fanout, topic)

### Architecture Patterns

- Asynchronous task processing
- Distributed worker scaling
- Error handling and recovery
- Message-driven architecture

## System Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /upload-image
       ▼
┌──────────────────────┐
│   FastAPI Server     │
│  (Producer)          │
└──────┬───────────────┘
       │ Publish message
       ▼
┌──────────────────────────────────────────────────────┐
│           RabbitMQ Message Broker                    │
│  ┌────────────────┬───────────────┬────────────────┐ │
│  │ resize_queue   │thumbnail_queue│   ocr_queue    │ │
│  ├────────────────┼───────────────┼────────────────┤ │
│  │ Direct Exchange (routing keys) │                │ │
│  └────────────────┬───────────────┬────────────────┘ │
│                   │               │                  │
│            ┌──────┴──────┐   ┌───┴──────┐          │
│            │ retry_queue  │   │ dlq_queue│          │
│            └──────────────┘   └──────────┘          │
└────────────────────────────────────────────────────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌──────────┐ ┌──────────────┐
│ Resize      │ │ Thumbnail   │ │   OCR    │ │  AI Tagging  │
│ Worker(s)   │ │ Worker      │ │ Worker   │ │ Worker       │
└─────────────┘ └─────────────┘ └──────────┘ └──────────────┘
```

## RabbitMQ Concepts

### Producer-Consumer Pattern

```python
# Producer (FastAPI)
channel.basic_publish(
    exchange='image_processing_direct',
    routing_key='resize',
    body=message_body,
    properties=pika.BasicProperties(delivery_mode=2)  # Persistent
)

# Consumer (Worker)
channel.basic_consume(
    queue='resize_queue',
    on_message_callback=handle_message
)
```

### ACK/NACK Mechanism

```
Worker receives message
       ↓
Process task
       ↓
    ↙   ↘
Success  Failure
   ↓        ↓
  ACK    Check retry count
           ↓
        ↙    ↘
    < MAX   >= MAX
      ↓        ↓
   RETRY    → DLQ
```

### Fair Dispatch (Prefetch Count)

```python
# Ensures each worker gets one task at a time
channel.basic_qos(prefetch_count=1)

# Without this: RabbitMQ would send all messages to first available worker
# With this: RabbitMQ sends next message only when worker acknowledges current one
```

### Retry and DLQ Architecture

```
Initial Queue
    ↓
[Process]
    ↓
  ↙   ↘
 ✓     ✗ (retry_count < MAX_RETRIES)
 ↓     ↓
ACK  Retry Queue (with incremented count)
     ↓
  [Process again]
     ↓
   ↙   ↘
  ✓     ✗ (retry_count >= MAX_RETRIES)
  ↓     ↓
 ACK   Dead Letter Queue (DLQ)
```

## Project Structure

```
RabbitMQ-FastAPI/
│
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application entry point
│   ├── worker_launcher.py               # Launch all workers
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                    # Configuration management (DATABASE, RABBITMQ, SECURITY, APP)
│   │   ├── constants.py                 # Application constants
│   │   ├── database.py                  # Database connection setup
│   │   ├── rabbitmq.py                  # RabbitMQ connection management
│   │   └── security.py                  # Security utilities
│   │
│   ├── api/
│   │   └── __init__.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── image_upload_routes.py       # Image upload endpoints
│   │   └── monitoring_routes.py         # Health check and monitoring
│   │
│   ├── rabbitmq/
│   │   ├── __init__.py                  # Re-exports from core.rabbitmq (for backwards compatibility)
│   │   └── connection.py                # Deprecated: use core.rabbitmq instead
│   │
│   ├── modules/                         # Feature modules
│   │   ├── resize/
│   │   │   ├── __init__.py
│   │   │   ├── consumer.py              # RabbitMQ consumer setup
│   │   │   ├── producer.py              # Message publishing
│   │   │   ├── exchange.py              # Exchange declarations
│   │   │   ├── queue.py                 # Queue declarations
│   │   │   ├── worker.py                # Resize worker implementation
│   │   │   ├── service.py               # Business logic
│   │   │   ├── schemas.py               # Pydantic models
│   │   │   └── utils.py                 # Utilities
│   │   │
│   │   ├── thumbnail/
│   │   │   ├── __init__.py
│   │   │   └── worker.py                # Thumbnail worker
│   │   │
│   │   ├── ocr/
│   │   │   ├── __init__.py
│   │   │   └── worker.py                # OCR worker
│   │   │
│   │   ├── ai_tagging/
│   │   │   ├── __init__.py
│   │   │   └── worker.py                # AI tagging worker
│   │   │
│   │   ├── retry/
│   │   │   ├── __init__.py
│   │   │   └── worker.py                # Retry handler
│   │   │
│   │   ├── dead_letter/
│   │   │   ├── __init__.py
│   │   │   └── worker.py                # Dead letter queue handler
│   │   │
│   │   ├── logging_system/
│   │   │   ├── __init__.py
│   │   │   └── worker.py                # Centralized logging
│   │   │
│   │   └── image_upload/
│   │       ├── __init__.py
│   │       ├── schemas.py               # Upload request/response models
│   │       ├── service.py               # Upload service logic
│   │       └── __init__.py
│   │
│   ├── shared/                          # Shared utilities and base classes
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   └── worker.py                # Base worker class
│   │   ├── dependencies/
│   │   │   └── __init__.py              # FastAPI dependencies
│   │   ├── enums/
│   │   │   └── __init__.py              # Enumerations
│   │   ├── exceptions/
│   │   │   ├── __init__.py
│   │   │   └── custom.py                # Custom exceptions
│   │   ├── helpers/
│   │   │   ├── __init__.py
│   │   │   └── logger.py                # Logging setup
│   │   ├── middleware/
│   │   │   └── __init__.py              # FastAPI middlewares
│   │   └── validators/
│   │       └── __init__.py              # Data validators
│   │
│   ├── producers/
│   │   ├── __init__.py
│   │   └── producer.py                  # Message producer utilities
│   │
│   ├── queues/
│   │   └── __init__.py                  # Queue declarations
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── image.py                     # Pydantic models for images
│   │
│   ├── models/
│   │   └── __init__.py                  # Database models
│   │
│   ├── services/
│   │   └── __init__.py                  # Business logic services
│   │
│   ├── workers/                         # Legacy worker modules (for backwards compatibility)
│   │   ├── __init__.py
│   │   ├── base.py                      # Base worker class (moved to shared/base/worker.py)
│   │   ├── resize_worker.py
│   │   ├── thumbnail_worker.py
│   │   ├── ocr_worker.py
│   │   └── ai_tagging_worker.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py                    # Logging configuration
│
├── docker/
│   ├── Dockerfile                       # FastAPI server image
│   ├── Dockerfile.worker                # Worker base image
│   └── fastapi/
│       └── Dockerfile
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest configuration and fixtures
│   ├── test_config.py                   # Configuration tests
│   └── test_workers.py                  # Worker tests
│
├── docs/
│   ├── 00_START_HERE.md
│   ├── API.md                           # API documentation
│   ├── ARCHITECTURE.md                  # Detailed architecture docs
│   ├── DEVELOPMENT.md                   # Development guide
│   ├── PROJECT_CORRECTIONS.md           # Corrections applied
│   └── [other documentation files]
│
├── docker-compose.yml                   # Docker Compose configuration
├── docker-compose.override.yml          # Local development overrides
├── requirements.txt                     # Python dependencies
├── .env.example                         # Environment variables template
├── Makefile                             # Build automation
├── QUICKSTART.sh                        # Quick start script
├── start.sh                             # Startup script
├── test_api.sh                          # API testing script
├── validate_setup.py                    # Setup validation
└── README.md                            # This file
```

### Key Files Explained

**Core Configuration & Setup:**
- `app/core/config.py` - Centralized configuration management for all services
- `app/core/rabbitmq.py` - RabbitMQ connection and channel management
- `docker-compose.yml` - Container orchestration

**API Layer:**
- `app/main.py` - FastAPI application setup and middleware
- `app/routes/image_upload_routes.py` - Image upload and status endpoints
- `app/routes/monitoring_routes.py` - Health checks and monitoring

**Message Processing:**
- `app/modules/**/worker.py` - Individual worker implementations
- `app/shared/base/worker.py` - Base worker class with ACK/NACK logic
- `app/worker_launcher.py` - Launch all workers in separate processes

**Data Models & Validation:**
- `app/schemas/image.py` - Request/response schemas
- `app/modules/image_upload/schemas.py` - Image upload specific models

**Utilities & Helpers:**
- `app/shared/helpers/logger.py` - Centralized logging setup
- `app/shared/exceptions/custom.py` - Custom exception classes

## Prerequisites

- **Docker** (version 20.10+)
- **Docker Compose** (version 1.29+)
- OR **Python 3.11+** and **RabbitMQ** (for local development)

### System Requirements

- 4GB RAM minimum
- 2GB disk space
- Port 5672 (RabbitMQ AMQP)
- Port 15672 (RabbitMQ Management UI)
- Port 8000 (FastAPI)

## Installation & Setup

### Option 1: Docker Compose (Recommended)

1. Clone or download the project:
```bash
cd /path/to/RabbitMQ-FastAPI
```

2. Build and start all services:
```bash
docker-compose up --build
```

This will:
- Start RabbitMQ broker
- Start FastAPI API server
- Start multiple worker instances
- Set up all queues and exchanges

3. Verify services are running:
```bash
docker-compose ps
```

### Option 2: Local Development Setup

1. Create a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start RabbitMQ (make sure it's running):
```bash
# On macOS with Homebrew
brew install rabbitmq
brew services start rabbitmq

# On Linux with Docker
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3.12-management-alpine
```

4. Start FastAPI server:
```bash
uvicorn app.main:app --reload
```

5. In separate terminals, start workers:
```bash
# Terminal 1: Resize Worker
python -m app.workers.resize_worker

# Terminal 2: Thumbnail Worker
python -m app.workers.thumbnail_worker

# Terminal 3: OCR Worker
python -m app.workers.ocr_worker

# Terminal 4: AI Tagging Worker
python -m app.workers.ai_tagging_worker
```

## Running the Project

### Using Docker Compose

```bash
# Start all services
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f resize_worker_1

# Stop all services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v
```

### Scaling Workers

To run multiple instances of a worker:

```bash
# Scale resize workers to 3 instances
docker-compose up -d --scale resize_worker=3
```

## API Documentation

### 1. Health Check

**Endpoint:** `GET /health`

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### 2. Upload Image

**Endpoint:** `POST /upload-image`

**Request Body:**
```json
{
  "image_id": 1,
  "filename": "car.jpg",
  "image_path": "/uploads/car.jpg",
  "image_size": "5MB"
}
```

**Response:**
```json
{
  "message": "Image processing started",
  "status": "queued",
  "image_id": 1,
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/upload-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 1,
    "filename": "car.jpg",
    "image_path": "/uploads/car.jpg",
    "image_size": "5MB"
  }'
```

### 3. Get Image Status

**Endpoint:** `GET /api/status/{image_id}`

```bash
curl http://localhost:8000/api/status/1
```

**Response:**
```json
{
  "image_id": 1,
  "status": "processing",
  "tasks": {
    "resize": "completed",
    "thumbnail": "in_progress",
    "ocr": "pending",
    "ai_tagging": "pending"
  },
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

## Monitoring

### RabbitMQ Management UI

Access the RabbitMQ management dashboard:
- **URL:** http://localhost:15672
- **Username:** guest
- **Password:** guest

**Dashboard Features:**
- View queue sizes and message counts
- Monitor consumer connections
- Track message rates
- Inspect individual messages
- Manage exchanges and bindings
- Check node status

### Key Metrics to Monitor

1. **Queue Length** - Number of messages waiting
2. **Consumer Count** - Number of active workers
3. **Message Rate** - Messages per second
4. **Acked/Nacked** - Successfully/failed processed messages
5. **Unacked** - Messages being processed

### Logs

View application logs:
```bash
# All logs
docker-compose logs

# Specific service
docker-compose logs api
docker-compose logs resize_worker_1

# Follow logs in real-time
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

## Configuration

### Environment Variables

Edit `docker-compose.yml` or create `.env` file:

```env
# RabbitMQ Configuration
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

# FastAPI Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
DEBUG=True
LOG_LEVEL=INFO
ENVIRONMENT=development

# Security
SECRET_KEY=your-secret-key-here  # Set in production!

# Database
DATABASE_URL=sqlite:///./image_processing.db
DB_ECHO=False
```

### RabbitMQ Configuration

Modify in `app/core/config.py`:

```python
@dataclass
class RabbitMQConfig:
    PREFETCH_COUNT = 1           # Messages per worker
    MAX_RETRIES = 3              # Retry attempts
    RETRY_DELAY = 10000          # Milliseconds (10 seconds)
    
    # Queue names
    RESIZE_QUEUE = "resize_queue"
    THUMBNAIL_QUEUE = "thumbnail_queue"
    OCR_QUEUE = "ocr_queue"
    AI_TAGGING_QUEUE = "ai_tagging_queue"
    RETRY_QUEUE = "retry_queue"
    DEAD_LETTER_QUEUE = "dead_letter_queue"
```

### Application Configuration

Key settings in `app/core/config.py`:

```python
@dataclass
class AppConfig:
    APP_NAME: str = "Async Image Processing Pipeline"
    UPLOAD_DIR: str = "app/uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Processing timeouts (seconds)
    RESIZE_TIMEOUT: int = 30
    THUMBNAIL_TIMEOUT: int = 20
    OCR_TIMEOUT: int = 60
    AI_TAGGING_TIMEOUT: int = 45
```

### Security Configuration

Important! Set a proper SECRET_KEY in production:

```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set environment variable
export SECRET_KEY="<generated-key>"
```

## Troubleshooting

### Issue: Connection Refused

**Problem:** `Connection refused` error when connecting to RabbitMQ

**Solution:**
```bash
# Check if RabbitMQ is running
docker-compose ps

# Check RabbitMQ logs
docker-compose logs rabbitmq

# Restart RabbitMQ
docker-compose restart rabbitmq
```

### Issue: Workers Not Processing Messages

**Problem:** Messages queue up but workers don't process them

**Solutions:**
1. Check worker logs: `docker-compose logs resize_worker_1`
2. Verify RabbitMQ connectivity
3. Check queue bindings in RabbitMQ UI
4. Ensure workers are running: `docker-compose ps`

### Issue: Messages in Dead Letter Queue

**Problem:** Too many messages in DLQ indicates processing failures

**Solutions:**
1. Check worker logs for error messages
2. Verify input data format
3. Increase MAX_RETRIES in config
4. Check RabbitMQ UI for error patterns

### Issue: High Memory Usage

**Problem:** RabbitMQ or workers consuming excessive memory

**Solutions:**
1. Reduce prefetch_count: `basic_qos(prefetch_count=1)`
2. Process messages more efficiently
3. Increase resource limits in docker-compose.yml
4. Monitor message queue size

### Issue: Port Already in Use

**Problem:** Ports 5672, 15672, or 8000 already in use

**Solutions:**
```bash
# Find process using port
lsof -i :8000
lsof -i :5672

# Kill process
kill -9 <PID>

# Or use different ports in docker-compose.yml
```

## Demonstration Scenarios

### Scenario 1: Basic Image Processing

1. Upload an image:
```bash
curl -X POST http://localhost:8000/upload-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 1,
    "filename": "photo.jpg",
    "image_path": "/uploads/photo.jpg",
    "image_size": "5MB"
  }'
```

2. Watch worker logs:
```bash
docker-compose logs -f resize_worker_1
docker-compose logs -f thumbnail_worker
docker-compose logs -f ocr_worker
docker-compose logs -f ai_tagging_worker
```

3. Monitor in RabbitMQ UI:
   - View queue lengths
   - Check consumer activity
   - Track processed messages

### Scenario 2: Failure and Retry

1. Upload multiple images rapidly
2. Observe some workers fail (simulated with random.randint)
3. Watch retry_queue receive failed messages
4. Monitor retry attempts in logs
5. After MAX_RETRIES, see messages move to DLQ

### Scenario 3: Competing Consumers

1. Verify two resize_worker instances running
2. Upload multiple images
3. Watch logs from both resize_worker_1 and resize_worker_2
4. Observe fair distribution of work

## Advanced Features

### Future Enhancements

1. **Database Integration**
   - Store processing results in PostgreSQL
   - Track image processing status
   - Query historical data

2. **Real Image Processing**
   - Use Pillow for actual image resizing
   - Implement real OCR with EasyOCR
   - Use YOLO for object detection

3. **WebSocket Updates**
   - Real-time processing status
   - Live progress notifications
   - Browser UI dashboard

4. **Message Batching**
   - Process multiple images together
   - Reduce RabbitMQ overhead
   - Improve throughput

5. **Priority Queues**
   - Urgent vs. normal processing
   - Weighted distribution
   - SLA-based routing

6. **Celery Integration**
   - Production-grade task queue
   - Better scheduling
   - Advanced monitoring

7. **Kubernetes Deployment**
   - Container orchestration
   - Auto-scaling workers
   - Multi-node clusters

## Best Practices Demonstrated

### 1. Message Durability
```python
# Durable queue survives broker restart
channel.queue_declare(queue='resize_queue', durable=True)

# Persistent message survives broker crash
properties=pika.BasicProperties(delivery_mode=2)
```

### 2. Graceful Error Handling
```python
try:
    result = self.process(message)
    ch.basic_ack(delivery_tag=method.delivery_tag)
except Exception as e:
    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

### 3. Fair Dispatch
```python
# Prevent overwhelming slow workers
channel.basic_qos(prefetch_count=1)
```

### 4. Retry Logic
```python
if retry_count < MAX_RETRIES:
    self.requeue_message(message)
else:
    self.send_to_dlq(message)
```

### 5. Logging
```python
logger.info(f"Processing image {image_id}")
logger.error(f"Failed to process image {image_id}: {error}")
```

## Testing

### Unit Tests (Coming Soon)

```bash
pytest tests/
```

### Integration Tests

```bash
# Upload and verify full pipeline
python tests/integration_test.py
```

### Load Testing

```bash
# Send multiple images simultaneously
python tests/load_test.py --images=100 --workers=5
```

## Performance Metrics

### Typical Performance

- **Image Processing Time:** 15-20 seconds per image
- **Throughput:** 10-15 images/min with 4 workers
- **Latency:** <100ms API response
- **Memory:** ~200MB per worker

### Optimization Tips

1. **Increase Workers:** `docker-compose up -d --scale resize_worker=5`
2. **Increase Prefetch:** Change `PREFETCH_COUNT` (careful with memory)
3. **Batch Processing:** Process multiple images together
4. **Hardware:** Use SSD for better I/O

## Contributing

Contributions welcome! Areas to improve:

- Real image processing implementations
- Database integration
- UI dashboard
- Advanced monitoring
- Performance optimizations

## References

- [RabbitMQ Documentation](https://www.rabbitmq.com/docs)
- [RabbitMQ Python Tutorials](https://www.rabbitmq.com/tutorials/tutorial-one-python.html)
- [Pika Documentation](https://pika.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)

## License

MIT License - Feel free to use for learning and commercial projects.

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review RabbitMQ Management UI
3. Check application logs
4. Consult official documentation

---

**Happy Learning! 🚀**

This project is designed to teach practical RabbitMQ concepts through a real-world scenario. Experiment, break things, and understand how distributed systems work!
