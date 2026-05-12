# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

No authentication required for this demo. In production, implement JWT or OAuth2.

## Response Format

All responses are JSON format with the following structure:

```json
{
  "data": {...},
  "status": "success|error",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

## Error Responses

```json
{
  "detail": "Error message",
  "status": 400
}
```

## Endpoints

### 1. Health Check

#### GET /health

Check if the API server is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

**Status Codes:**
- `200` - API is healthy
- `503` - API is not ready

---

### 2. Root Information

#### GET /

Get basic information about the API.

**Response:**
```json
{
  "message": "Async Image Processing Pipeline",
  "status": "running",
  "version": "1.0.0"
}
```

**Example:**
```bash
curl http://localhost:8000/
```

---

### 3. Upload Image for Processing

#### POST /upload-image

Submit an image metadata for asynchronous processing.

This endpoint immediately returns while RabbitMQ handles the actual processing.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image_id` | integer | Yes | Unique identifier for the image (positive integer) |
| `filename` | string | Yes | Original filename (e.g., "photo.jpg") |
| `image_path` | string | Yes | Path to store the image (e.g., "/uploads/photo.jpg") |
| `image_size` | string | Yes | Size of the image (e.g., "5MB", "2.5MB") |

**Example Request:**
```bash
curl -X POST http://localhost:8000/upload-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 1,
    "filename": "landscape.jpg",
    "image_path": "/uploads/landscape.jpg",
    "image_size": "5MB"
  }'
```

**Successful Response (200):**
```json
{
  "message": "Image processing started",
  "status": "queued",
  "image_id": 1,
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

**Error Responses:**

**400 - Bad Request**
```json
{
  "detail": "image_id must be positive"
}
```

**422 - Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "image_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 - Server Error**
```json
{
  "detail": "Failed to queue image for processing"
}
```

**Processing Flow:**
1. API receives request
2. Validates input (image_id must be positive)
3. Creates uploads directory if needed
4. Publishes messages to RabbitMQ:
   - resize_queue
   - thumbnail_queue
   - ocr_queue
   - ai_tagging_queue
5. Returns immediately (non-blocking)
6. Workers process in background

**Processing Times:**
- Resize: ~5 seconds
- Thumbnail: ~3 seconds
- OCR: ~7 seconds
- AI Tagging: ~6 seconds
- Total (parallel): ~7 seconds

---

### 4. Get Image Processing Status

#### GET /api/status/{image_id}

Get the processing status of a submitted image.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `image_id` | integer | The image ID (from upload-image response) |

**Example Request:**
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
  "timestamp": "2024-01-15T10:30:05.123456"
}
```

**Task Statuses:**
- `pending` - Waiting in queue
- `in_progress` - Currently being processed
- `completed` - Successfully processed
- `failed` - Processing failed
- `retrying` - Retrying after failure

**Note:** In this demo version, the status endpoint returns placeholder data. In production, implement database queries to track actual progress.

---

## Quick Examples

### Example 1: Upload Single Image

```bash
# Upload an image
curl -X POST http://localhost:8000/upload-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 1,
    "filename": "car.jpg",
    "image_path": "/uploads/car.jpg",
    "image_size": "2.5MB"
  }'

# Response (immediate)
# {
#   "message": "Image processing started",
#   "status": "queued",
#   "image_id": 1,
#   "timestamp": "2024-01-15T10:30:00.123456"
# }
```

### Example 2: Upload Multiple Images

```bash
# Upload image 1
curl -X POST http://localhost:8000/upload-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 1,
    "filename": "photo1.jpg",
    "image_path": "/uploads/photo1.jpg",
    "image_size": "3MB"
  }'

# Upload image 2
curl -X POST http://localhost:8000/upload-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 2,
    "filename": "photo2.jpg",
    "image_path": "/uploads/photo2.jpg",
    "image_size": "4MB"
  }'

# Upload image 3
curl -X POST http://localhost:8000/upload-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 3,
    "filename": "photo3.jpg",
    "image_path": "/uploads/photo3.jpg",
    "image_size": "2MB"
  }'
```

### Example 3: Monitor Processing

```bash
# Check status immediately (will likely show pending)
curl http://localhost:8000/api/status/1

# Check status after some time
sleep 10
curl http://localhost:8000/api/status/1
```

### Example 4: Bulk Processing

```bash
# Using shell script to send 10 images
for i in {1..10}; do
  curl -X POST http://localhost:8000/upload-image \
    -H "Content-Type: application/json" \
    -d "{
      \"image_id\": $i,
      \"filename\": \"image_$i.jpg\",
      \"image_path\": \"/uploads/image_$i.jpg\",
      \"image_size\": \"5MB\"
    }"
done
```

---

## Interactive API Documentation

### Swagger UI

Open in browser: http://localhost:8000/docs

Features:
- Try out endpoints directly
- See request/response schemas
- View all parameters and types

### ReDoc

Open in browser: http://localhost:8000/redoc

Features:
- Detailed API documentation
- Better for reading/understanding

---

## Request/Response Examples

### Using Python

```python
import requests
import json

# Upload image
response = requests.post(
    'http://localhost:8000/upload-image',
    json={
        'image_id': 1,
        'filename': 'photo.jpg',
        'image_path': '/uploads/photo.jpg',
        'image_size': '5MB'
    }
)

print(response.status_code)  # 200
print(json.dumps(response.json(), indent=2))

# Get status
response = requests.get('http://localhost:8000/api/status/1')
print(response.json())
```

### Using JavaScript/Fetch

```javascript
// Upload image
const response = await fetch('http://localhost:8000/upload-image', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    image_id: 1,
    filename: 'photo.jpg',
    image_path: '/uploads/photo.jpg',
    image_size: '5MB'
  })
});

const data = await response.json();
console.log(data);
// {
//   message: "Image processing started",
//   status: "queued",
//   image_id: 1,
//   timestamp: "..."
// }
```

### Using Postman

1. Open Postman
2. Create new Request
3. Set method to POST
4. URL: `http://localhost:8000/upload-image`
5. Headers: `Content-Type: application/json`
6. Body (raw JSON):
```json
{
  "image_id": 1,
  "filename": "photo.jpg",
  "image_path": "/uploads/photo.jpg",
  "image_size": "5MB"
}
```
7. Click Send

---

## Rate Limiting

Currently, there is no rate limiting. In production, implement:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

@app.post("/upload-image")
@limiter.limit("100/minute")
async def upload_image(request: ImageUploadRequest):
    ...
```

---

## Pagination

Current endpoints don't use pagination. For future implementations:

```python
@app.get("/api/images/")
async def list_images(skip: int = 0, limit: int = 10):
    # skip: number of items to skip
    # limit: maximum number of items to return
    ...
```

---

## Filtering and Search

For future implementations:

```python
@app.get("/api/images/")
async def search_images(
    filename: str = Query(None),
    status: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None)
):
    # Filter by filename
    # Filter by status
    # Filter by date range
    ...
```

---

## Webhooks (Future)

For real-time status updates:

```python
@app.post("/api/webhook/register")
async def register_webhook(url: str):
    # Register webhook URL
    # Receive POST requests when processing completes
    ...
```

---

## Versioning

Current version: 1.0.0

Future versions might use URL versioning:
- `/api/v1/upload-image`
- `/api/v2/upload-image`

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 422 | Unprocessable Entity (schema validation) |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Monitoring API Health

```bash
# Check health regularly
watch -n 5 'curl -s http://localhost:8000/health | jq .'

# Combined with RabbitMQ check
curl http://localhost:8000/health && \
curl -u guest:guest http://localhost:15672/api/overview > /dev/null && \
echo "All systems operational"
```

---

## Troubleshooting API Issues

### API Not Responding

```bash
# Check if API container is running
docker-compose ps api

# Check API logs
docker-compose logs api

# Restart API
docker-compose restart api
```

### RabbitMQ Connection Error

```bash
# Verify RabbitMQ is running
docker-compose ps rabbitmq

# Check RabbitMQ health
docker-compose logs rabbitmq | grep ERROR
```

### Message Not Processing

```bash
# Check queue lengths
curl -u guest:guest http://localhost:15672/api/queues/%2F/resize_queue

# Check if workers are running
docker-compose ps | grep worker

# View worker logs
docker-compose logs resize_worker_1
```

---

## Best Practices

### 1. Always Provide Image ID
```bash
# Good
curl -X POST http://localhost:8000/upload-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 123,
    ...
  }'

# Bad (missing image_id)
curl -X POST http://localhost:8000/upload-image \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "photo.jpg",
    ...
  }'
```

### 2. Use Consistent Image IDs
```bash
# Keep IDs unique and sequential
# Good: 1, 2, 3, 4, 5
# Bad: 1, 1, 1, 2, 5
```

### 3. Implement Polling
```bash
# Poll status every 5 seconds
while true; do
  curl http://localhost:8000/api/status/1
  sleep 5
done
```

### 4. Handle Failures Gracefully
```bash
# In your client code
try {
  response = requests.post(url, json=data, timeout=5)
except requests.exceptions.Timeout:
  # Retry logic
  pass
except requests.exceptions.ConnectionError:
  # Fallback logic
  pass
```

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review README.md
3. Check ARCHITECTURE.md for design details
4. Review worker logs for processing errors

---

**Happy API Testing!** 🚀
