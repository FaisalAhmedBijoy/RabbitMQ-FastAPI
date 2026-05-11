#!/bin/bash

# Test the API endpoints

BASE_URL="http://localhost:8000"

echo "================================"
echo "Testing Image Processing API"
echo "================================"
echo ""

# Health check
echo "1️⃣  Testing health endpoint..."
curl -s "$BASE_URL/health" | python -m json.tool
echo ""
echo ""

# Upload image 1
echo "2️⃣  Uploading image 1..."
curl -s -X POST "$BASE_URL/upload-image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 1,
    "filename": "landscape.jpg",
    "image_path": "/uploads/landscape.jpg",
    "image_size": "5MB"
  }' | python -m json.tool
echo ""
echo ""

# Upload image 2
echo "3️⃣  Uploading image 2..."
curl -s -X POST "$BASE_URL/upload-image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 2,
    "filename": "portrait.png",
    "image_path": "/uploads/portrait.png",
    "image_size": "3MB"
  }' | python -m json.tool
echo ""
echo ""

# Upload image 3
echo "4️⃣  Uploading image 3..."
curl -s -X POST "$BASE_URL/upload-image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": 3,
    "filename": "document.pdf",
    "image_path": "/uploads/document.pdf",
    "image_size": "2MB"
  }' | python -m json.tool
echo ""
echo ""

# Get status
echo "5️⃣  Checking status of image 1..."
curl -s "$BASE_URL/api/status/1" | python -m json.tool
echo ""
echo ""

echo "✓ Test complete!"
echo ""
echo "📊 Monitor progress in RabbitMQ UI:"
echo "   http://localhost:15672 (guest/guest)"
echo ""
echo "📋 View worker logs:"
echo "   docker-compose logs -f resize_worker_1"
echo "   docker-compose logs -f thumbnail_worker"
echo "   docker-compose logs -f ocr_worker"
echo "   docker-compose logs -f ai_tagging_worker"
