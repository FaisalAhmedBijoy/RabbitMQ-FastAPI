# Architecture Documentation

## System Overview

This document provides detailed architecture information for the Async Image Processing Pipeline.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                           │
│  (Web Browser, Mobile App, Third-party API)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI)                       │
│  ┌────────────────────────────────────────────────────────┐│
│  │ POST /upload-image    - Submit image for processing    ││
│  │ GET  /health          - Health check                   ││
│  │ GET  /api/status/{id} - Get processing status          ││
│  └────────────────────────────────────────────────────────┘│
└────────────────────────┬────────────────────────────────────┘
                         │ Publishes
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                RabbitMQ Message Broker                      │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Exchanges:                                           │ │
│  │ - Direct: image_processing_direct                    │ │
│  │ - Fanout: image_processing_fanout                    │ │
│  │ - Topic:  image_processing_topic                     │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Queues:                                              │ │
│  │ - resize_queue         (Durable=True)               │ │
│  │ - thumbnail_queue      (Durable=True)               │ │
│  │ - ocr_queue            (Durable=True)               │ │
│  │ - ai_tagging_queue     (Durable=True)               │ │
│  │ - retry_queue          (Durable=True)               │ │
│  │ - dead_letter_queue    (Durable=True)               │ │
│  │ - logging_queue        (Durable=True)               │ │
│  └──────────────────────────────────────────────────────┘ │
└────────┬───────────────┬──────────────┬─────────────┬──────┘
         │               │              │             │
         ▼               ▼              ▼             ▼
    ┌─────────────┐┌──────────────┐┌────────┐┌──────────────┐
    │   Resize    ││  Thumbnail   ││  OCR   ││ AI Tagging   │
    │  Workers    ││  Worker      ││ Worker ││ Worker       │
    │(Competing   ││(Multiple     ││        ││              │
    │ Consumers)  ││ Instances)   ││        ││              │
    └─────────────┘└──────────────┘└────────┘└──────────────┘
         │               │              │             │
         └───────────────┴──────────────┴─────────────┘
                         │
                         ▼
                  ┌────────────────┐
                  │  Results Store │
                  │  (Log Files)   │
                  └────────────────┘
```

## Component Architecture

### 1. API Layer (FastAPI)

**File:** `app/main.py`

**Responsibilities:**
- Accept image metadata via HTTP POST
- Validate input
- Publish messages to RabbitMQ
- Return immediate response
- Non-blocking operation

**Key Functions:**
```python
@app.post("/upload-image")
async def upload_image(request: ImageUploadRequest)
```

**Message Flow:**
```
HTTP Request
    ↓
Validate Input
    ↓
Publish to RabbitMQ (4 messages)
    ↓
Return Response (immediate)
    ↓
[Worker processes in background]
```

### 2. RabbitMQ Connection Manager

**File:** `app/rabbitmq/connection.py`

**Responsibilities:**
- Manage AMQP connection
- Create and reuse channels
- Handle connection failures
- Implement reconnection logic

**Key Pattern:**
```python
class RabbitMQConnection:
    def connect(self) -> BlockingChannel
    def get_channel(self) -> BlockingChannel
    def disconnect(self)
```

### 3. Queue and Exchange Setup

**File:** `app/queues/__init__.py`

**Initialization:**
```python
setup_rabbitmq()
  ├── declare_exchanges()
  │   ├── Direct Exchange: image_processing_direct
  │   ├── Fanout Exchange: image_processing_fanout
  │   └── Topic Exchange: image_processing_topic
  │
  ├── declare_queues()
  │   ├── resize_queue
  │   ├── thumbnail_queue
  │   ├── ocr_queue
  │   ├── ai_tagging_queue
  │   ├── retry_queue
  │   ├── dead_letter_queue
  │   └── logging_queue
  │
  └── bind_queues()
      └── Bind queues to exchanges with routing keys
```

**Queue Bindings:**
```
resize_queue         → image_processing_direct (routing_key: 'resize')
thumbnail_queue      → image_processing_direct (routing_key: 'thumbnail')
ocr_queue            → image_processing_direct (routing_key: 'ocr')
ai_tagging_queue     → image_processing_direct (routing_key: 'ai_tagging')
retry_queue          → image_processing_direct (routing_key: 'retry')
dead_letter_queue    → image_processing_direct (routing_key: 'dlq')
logging_queue        → image_processing_fanout (routing_key: '')
```

### 4. Producer (Image Publishing)

**File:** `app/producers/__init__.py`

**Flow:**
```python
publish_image_task(image_id, filename, image_path, image_size)
  │
  ├── Create message object
  │   ├── image_id
  │   ├── filename
  │   ├── image_path
  │   ├── image_size
  │   ├── retry_count: 0
  │   └── timestamp: ISO format
  │
  ├── Publish to resize_queue
  ├── Publish to thumbnail_queue
  ├── Publish to ocr_queue
  └── Publish to ai_tagging_queue
```

**Message Properties:**
```python
pika.BasicProperties(
    delivery_mode=2,          # Persistent (survives restart)
    content_type='application/json'
)
```

### 5. Base Worker Class

**File:** `app/workers/base.py`

**Architecture:**
```python
class BaseWorker(ABC):
    def __init__(queue_name, worker_name)
    def connect()
    def handle_message(ch, method, properties, body)
    def process(message) → dict
    def requeue_message(message)
    def send_to_dlq(message)
    def start_consuming()
```

**Message Handling Flow:**
```
Receive Message from Queue
    ↓
Decode JSON
    ↓
Call process() [to be implemented by subclass]
    ↓
    ├─ Success → ACK ✓
    │
    └─ Failure → Check retry_count
        ├─ < MAX_RETRIES → Requeue to retry_queue
        └─ >= MAX_RETRIES → Send to DLQ
```

**ACK/NACK Strategy:**
```python
try:
    success = self.process(message)
    if success:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        if retry_count < MAX_RETRIES:
            requeue_message(message)
        else:
            send_to_dlq(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)
except Exception:
    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

### 6. Worker Implementations

#### Resize Worker
**File:** `app/workers/resize_worker.py`

**Responsibilities:**
- Simulate image resizing
- Add artificial 5-second delay
- Random failure simulation (1 in 10 chance)
- Return resize metadata

**Process Method:**
```python
def process(message):
    image_id = message['image_id']
    filename = message['filename']
    
    # Simulate failure
    if random.randint(1, 10) == 5:
        raise Exception("Simulated resize failure")
    
    # Simulate processing
    time.sleep(5)
    
    return {
        'task_type': 'resize',
        'status': 'completed',
        'details': {...}
    }
```

#### Thumbnail Worker
**File:** `app/workers/thumbnail_worker.py`
- 3-second processing delay
- 1 in 8 failure chance
- Returns thumbnail path and metadata

#### OCR Worker
**File:** `app/workers/ocr_worker.py`
- 7-second processing delay
- 1 in 6 failure chance
- Returns detected text and confidence scores

#### AI Tagging Worker
**File:** `app/workers/ai_tagging_worker.py`
- 6-second processing delay
- 1 in 7 failure chance
- Returns tags and object detection results

## Message Flow Diagram

### Successful Processing

```
User API Call
    │
    ├─→ POST /upload-image
    │   └─→ Image: {id: 1, file: "car.jpg", ...}
    │
    ├─→ FastAPI Receives
    │
    ├─→ Publish 4 Messages
    │   ├─→ resize_queue
    │   ├─→ thumbnail_queue
    │   ├─→ ocr_queue
    │   └─→ ai_tagging_queue
    │
    ├─→ Immediate Response
    │   └─→ {status: "queued", image_id: 1}
    │
    └─→ [Async Processing]
        │
        ├─→ Resize Worker 1
        │   ├─→ Consume message (prefetch_count=1)
        │   ├─→ Process (5 sec)
        │   ├─→ Generate result
        │   └─→ ACK
        │
        ├─→ Thumbnail Worker
        │   ├─→ Consume message
        │   ├─→ Process (3 sec)
        │   ├─→ Generate thumbnail
        │   └─→ ACK
        │
        ├─→ OCR Worker
        │   ├─→ Consume message
        │   ├─→ Process (7 sec)
        │   ├─→ Extract text
        │   └─→ ACK
        │
        └─→ AI Tagging Worker
            ├─→ Consume message
            ├─→ Process (6 sec)
            ├─→ Tag objects
            └─→ ACK
```

### Failed Processing with Retry

```
Worker Receives Message
    │
    ├─→ Try to Process
    │
    ├─→ ERROR! (random failure)
    │
    ├─→ Check retry_count
    │
    ├─→ If retry_count < MAX_RETRIES (3):
    │   ├─→ Create new message
    │   │   └─→ retry_count += 1
    │   │
    │   ├─→ Publish to retry_queue
    │   │
    │   └─→ ACK original message
    │       (so it's removed from original queue)
    │
    └─→ If retry_count >= MAX_RETRIES:
        ├─→ Send message to DLQ
        │
        └─→ ACK original message
            (so it's removed from original queue)
```

## Configuration Architecture

**File:** `app/config.py`

```python
@dataclass
class RabbitMQConfig:
    HOST = "localhost"          # RabbitMQ server host
    PORT = 5672                 # RabbitMQ AMQP port
    USER = "guest"              # RabbitMQ username
    PASSWORD = "guest"          # RabbitMQ password
    
    # Queues
    RESIZE_QUEUE = "resize_queue"
    # ... other queues
    
    # Exchanges
    DIRECT_EXCHANGE = "image_processing_direct"
    # ... other exchanges
    
    # Worker Configuration
    PREFETCH_COUNT = 1          # Messages per worker (fair dispatch)
    MAX_RETRIES = 3             # Retry attempts
    RETRY_DELAY = 10000         # Milliseconds

@dataclass
class AppConfig:
    APP_NAME = "Async Image Processing Pipeline"
    DEBUG = True
    LOG_LEVEL = "INFO"
    UPLOAD_DIR = "uploads"
    MAX_FILE_SIZE = 100 * 1024 * 1024
```

## Docker Architecture

### Services

```
Docker Compose
│
├── rabbitmq (RabbitMQ Container)
│   ├── Port 5672: AMQP Protocol
│   ├── Port 15672: Management UI
│   └── Volume: rabbitmq_data
│
├── api (FastAPI Container)
│   ├── Port 8000: API Server
│   ├── Health Check: /health
│   └── Volume: ./app (code)
│
├── resize_worker_1 (Worker Container)
│   └── Command: python -m app.workers.resize_worker
│
├── resize_worker_2 (Worker Container)
│   └── Command: python -m app.workers.resize_worker
│
├── thumbnail_worker (Worker Container)
│   └── Command: python -m app.workers.thumbnail_worker
│
├── ocr_worker (Worker Container)
│   └── Command: python -m app.workers.ocr_worker
│
└── ai_tagging_worker (Worker Container)
    └── Command: python -m app.workers.ai_tagging_worker
```

### Network Architecture

```
All containers connected via bridge network: image_processing_network

┌─────────────────────────────────────────────┐
│   image_processing_network (Bridge)         │
│                                             │
│  ┌──────────┐  ┌──────┐  ┌─────────────┐  │
│  │ api      │──│      │──│ resize_     │  │
│  │ :8000    │  │      │  │ worker_1    │  │
│  └──────────┘  │      │  └─────────────┘  │
│                │ rmq  │                    │
│  ┌──────────┐  │      │  ┌─────────────┐  │
│  │ clients  │──│:5672 │──│ resize_     │  │
│  │ (ext)    │  │      │  │ worker_2    │  │
│  └──────────┘  │      │  └─────────────┘  │
│                │      │                    │
│  ┌──────────┐  │      │  ┌─────────────┐  │
│  │ Monitoring│──│:15672│──│ thumbnail_  │  │
│  │ (ext)    │  │      │  │ worker      │  │
│  └──────────┘  │      │  └─────────────┘  │
│                │      │                    │
│                │      │  ┌─────────────┐  │
│                │      │  │ ocr_worker  │  │
│                │      │  └─────────────┘  │
│                │      │                    │
│                └──────┘  ┌─────────────┐  │
│                          │ ai_tagging_ │  │
│                          │ worker      │  │
│                          └─────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

## Scaling Architecture

### Horizontal Scaling

```
Scale Out (Add More Workers):

Single Worker Setup:
┌───────────────────┐
│  resize_worker_1  │
└─────────┬─────────┘
          │
      [Queue]
          │
    5 messages/min capacity


Multi-Worker Setup:
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│  resize_worker_1  │  │  resize_worker_2  │  │  resize_worker_3  │
└─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
          │                      │                      │
          └──────────┬───────────┴───────────┬──────────┘
                     │                       │
                  [Queue]
                 (Fair dispatch with prefetch_count=1)
                 
              15 messages/min capacity (3x throughput)
```

### Load Distribution

```
Without Fair Dispatch (prefetch_count=∞):
Worker1: Receives all messages at once
Worker2: Idle
Worker3: Idle
Result: Unbalanced load

With Fair Dispatch (prefetch_count=1):
Worker1: Processes 1 message
Worker2: Processes 1 message (waiting for Worker1)
Worker3: Processes 1 message (waiting for Worker1 & 2)
Result: Balanced load, faster overall processing
```

## Data Flow Diagrams

### Complete Image Processing Pipeline

```
┌─────────────┐
│   Client    │ Sends image metadata
└──────┬──────┘
       │
       ▼
┌────────────────────────────┐
│ FastAPI POST /upload-image │
├────────────────────────────┤
│ 1. Receive request          │
│ 2. Validate input           │
│ 3. Publish 4 messages       │
│ 4. Return immediately       │
└────────────┬────────────────┘
             │
             │ Publishes (non-blocking)
             │
             ▼
    ┌────────────────────┐
    │  RabbitMQ Broker   │
    └────────────────────┘
       │  │  │  │
       │  │  │  └────────────────────────────────────┐
       │  │  │                                        │
       │  │  └────────────────────────────┐           │
       │  │                               │           │
       │  └────────────────────┐           │           │
       │                       │           │           │
       ▼                       ▼           ▼           ▼
    ┌──────────┐          ┌──────────┐ ┌──────┐  ┌─────────────┐
    │  Resize  │          │Thumbnail │ │ OCR  │  │ AI Tagging  │
    │  Worker  │          │  Worker  │ │Worker│  │  Worker     │
    └────┬─────┘          └────┬─────┘ └──┬───┘  └──────┬──────┘
         │                     │           │             │
         ▼                     ▼           ▼             ▼
    ┌──────────┐          ┌──────────┐ ┌──────┐  ┌─────────────┐
    │  Results │          │ Results  │ │Result│  │  Results    │
    │  Logged  │          │  Logged  │ │Logged│  │  Logged     │
    └──────────┘          └──────────┘ └──────┘  └─────────────┘
         │                     │           │             │
         └─────────────────────┴───────────┴─────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Log Files/Store    │
                    │  Processing Results │
                    └─────────────────────┘
```

## Performance Characteristics

### Message Processing Timeline

```
For a single image (image_id: 1):

Timeline:
├─ T=0ms:   API receives request
├─ T=10ms:  Messages published to RabbitMQ
├─ T=15ms:  API returns response (status: queued)
│
├─ T=100ms: Resize worker starts processing
├─ T=5100ms: Resize worker completes, sends ACK
│
├─ T=100ms: Thumbnail worker starts processing
├─ T=3100ms: Thumbnail worker completes, sends ACK
│
├─ T=100ms: OCR worker starts processing
├─ T=7100ms: OCR worker completes, sends ACK
│
├─ T=100ms: AI Tagging worker starts processing
└─ T=6100ms: AI Tagging worker completes, sends ACK

Maximum completion time: 7.1 seconds
(Parallel processing means workers run simultaneously)
```

### Throughput Analysis

```
Single Worker:
- Processing time per image: 7.1 seconds
- Throughput: 1 image / 7.1 seconds ≈ 8 images/minute

With 2 Resize + 1 Thumbnail + 1 OCR + 1 AI Worker:
- Resize bottleneck: 5 sec × 2 workers = 2.5 sec per image
- All workers process in parallel
- Throughput: ~24 images/minute

With 3 Resize + 2 Thumbnail + 1 OCR + 1 AI Worker:
- Resize: 5 sec / 3 = 1.67 sec per image
- Thumbnail: 3 sec / 2 = 1.5 sec per image
- Throughput: ~36 images/minute
```

## Error Handling Architecture

```
Error Recovery Strategy:

Level 1: Immediate Retry
├─ Error occurs in process()
├─ Increment retry_count
├─ Requeue to retry_queue
├─ Workers consume from retry_queue
└─ Up to MAX_RETRIES (3) attempts

Level 2: Dead Letter Queue
├─ Error persists after MAX_RETRIES
├─ Message sent to DLQ
├─ Manual inspection needed
├─ No automatic reprocessing
└─ Alert or log for investigation

Level 3: Monitoring
├─ Track DLQ size
├─ Alert if DLQ > threshold
├─ Monitor ACK/NACK ratios
└─ Track worker error rates
```

---

This architecture is designed for scalability, reliability, and educational value. Each component can be independently scaled and replaced with more sophisticated implementations as needed.
