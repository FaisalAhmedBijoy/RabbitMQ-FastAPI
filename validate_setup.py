"""
Test script to validate the project setup
"""

import sys
import time

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import pika
        print("  ✓ pika")
    except ImportError as e:
        print(f"  ✗ pika: {e}")
        return False
    
    try:
        import fastapi
        print("  ✓ fastapi")
    except ImportError as e:
        print(f"  ✗ fastapi: {e}")
        return False
    
    try:
        import uvicorn
        print("  ✓ uvicorn")
    except ImportError as e:
        print(f"  ✗ uvicorn: {e}")
        return False
    
    try:
        import pydantic
        print("  ✓ pydantic")
    except ImportError as e:
        print(f"  ✗ pydantic: {e}")
        return False
    
    return True


def test_rabbitmq_connection():
    """Test RabbitMQ connection"""
    print("\nTesting RabbitMQ connection...")
    try:
        import pika
        
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            virtual_host='/',
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            print("  ✓ Connected to RabbitMQ on localhost:5672")
            connection.close()
            return True
        except Exception as e:
            print(f"  ✗ Cannot connect to RabbitMQ: {e}")
            print("    Make sure RabbitMQ is running on localhost:5672")
            return False
    
    except Exception as e:
        print(f"  ✗ Error testing RabbitMQ: {e}")
        return False


def test_fastapi():
    """Test FastAPI app can be imported"""
    print("\nTesting FastAPI application...")
    try:
        sys.path.insert(0, '/Users/faisal/Documents/RND/RabbitMQ-FastAPI')
        from app.main import app
        print("  ✓ FastAPI app imported successfully")
        return True
    except Exception as e:
        print(f"  ✗ Error importing FastAPI app: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Project Setup Validation")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test RabbitMQ (only if available)
    if not test_rabbitmq_connection():
        print("  Note: This is expected if RabbitMQ is not running yet")
    
    # Test FastAPI
    if not test_fastapi():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ Basic setup validation passed!")
        print("\nNext steps:")
        print("1. Start RabbitMQ: docker-compose up rabbitmq -d")
        print("2. Start FastAPI: docker-compose up api -d")
        print("3. Start workers: docker-compose up -d")
        print("4. Run tests: ./test_api.sh")
    else:
        print("✗ Some tests failed. Check output above.")
    print("=" * 50)


if __name__ == "__main__":
    main()
