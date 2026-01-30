#!/usr/bin/env python3
"""Test script for ChatVLMLLM API."""

import requests
import json

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get("http://localhost:8001/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_models():
    """Test models endpoint."""
    print("Testing models endpoint...")
    response = requests.get("http://localhost:8001/models")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_ocr():
    """Test OCR endpoint."""
    print("Testing OCR endpoint...")
    
    # Test with our created image
    with open('test_image.png', 'rb') as f:
        files = {'file': f}
        data = {'model': 'qwen3_vl_2b'}
        
        response = requests.post("http://localhost:8001/ocr", files=files, data=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Extracted text: {result.get('text', 'No text found')}")
            print(f"Model used: {result.get('model', 'Unknown')}")
            print(f"Processing time: {result.get('processing_time_seconds', 'Unknown')}s")
        else:
            print(f"Error: {response.text}")
    print()

def test_chat():
    """Test chat endpoint."""
    print("Testing chat endpoint...")
    
    with open('test_image.png', 'rb') as f:
        files = {'file': f}
        data = {
            'prompt': 'Что написано на этом изображении?',
            'model': 'qwen3_vl_2b'
        }
        
        response = requests.post("http://localhost:8001/chat", files=files, data=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', 'No response')}")
            print(f"Model used: {result.get('model', 'Unknown')}")
            print(f"Processing time: {result.get('processing_time_seconds', 'Unknown')}s")
        else:
            print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    print("ChatVLMLLM API Test Script")
    print("=" * 50)
    
    test_health()
    test_models()
    test_ocr()
    test_chat()
    
    print("Testing complete!")