#!/usr/bin/env python3
"""Test script for ChatVLMLLM API."""

import requests
import json
import os
from PIL import Image, ImageDraw

def create_test_image():
    """Create a test image if it doesn't exist."""
    if not os.path.exists('test_image.png'):
        print("Creating test_image.png...")
        img = Image.new('RGB', (100, 30), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "Hello World", fill=(255, 255, 0))
        img.save('test_image.png')

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to localhost:8000. Is the server running?")
    print()

def test_models():
    """Test models endpoint."""
    print("Testing models endpoint...")
    try:
        response = requests.get("http://localhost:8000/models")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect.")
    print()

def test_ocr():
    """Test OCR endpoint."""
    print("Testing OCR endpoint...")

    # Test with our created image
    try:
        with open('test_image.png', 'rb') as f:
            files = {'file': f}
            data = {'model': 'qwen3_vl_2b'}

            response = requests.post("http://localhost:8000/ocr", files=files, data=data)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"Extracted text: {result.get('text', 'No text found')}")
                print(f"Model used: {result.get('model', 'Unknown')}")
                print(f"Processing time: {result.get('processing_time_seconds', 'Unknown')}s")
            else:
                print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect.")
    print()

def test_chat():
    """Test chat endpoint."""
    print("Testing chat endpoint...")

    try:
        with open('test_image.png', 'rb') as f:
            files = {'file': f}
            data = {
                'prompt': 'Что написано на этом изображении?',
                'model': 'qwen3_vl_2b'
            }

            response = requests.post("http://localhost:8000/chat", files=files, data=data)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result.get('response', 'No response')}")
                print(f"Model used: {result.get('model', 'Unknown')}")
                print(f"Processing time: {result.get('processing_time_seconds', 'Unknown')}s")
            else:
                print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect.")
    print()

if __name__ == "__main__":
    print("ChatVLMLLM API Test Script")
    print("=" * 50)

    create_test_image()

    test_health()
    test_models()
    test_ocr()
    test_chat()

    print("Testing complete!")
