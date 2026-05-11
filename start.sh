#!/bin/bash

# Async Image Processing Pipeline - Quick Start Script

echo "================================"
echo "Async Image Processing Pipeline"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose found"
echo ""

# Offer menu
echo "Choose an option:"
echo "1. Start all services (build + run)"
echo "2. Start services (no rebuild)"
echo "3. Stop all services"
echo "4. View logs"
echo "5. Scale workers"
echo "6. Stop and remove everything"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting services (building images)..."
        docker-compose up --build
        ;;
    2)
        echo ""
        echo "🚀 Starting services..."
        docker-compose up
        ;;
    3)
        echo ""
        echo "⏹️  Stopping services..."
        docker-compose stop
        echo "✓ Services stopped"
        ;;
    4)
        echo ""
        echo "📋 Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    5)
        read -p "How many resize workers? (default: 2): " workers
        workers=${workers:-2}
        echo ""
        echo "📊 Scaling resize workers to $workers instances..."
        docker-compose up -d --scale resize_worker=3
        docker-compose ps
        ;;
    6)
        echo ""
        echo "🗑️  Removing all services and volumes..."
        read -p "Are you sure? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            docker-compose down -v
            echo "✓ Everything removed"
        fi
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "📚 For more information, see README.md"
echo ""
echo "Access points:"
echo "• FastAPI API: http://localhost:8000"
echo "• API Docs: http://localhost:8000/docs"
echo "• RabbitMQ UI: http://localhost:15672 (guest/guest)"
