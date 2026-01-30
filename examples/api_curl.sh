#!/bin/bash
# ChatVLMLLM API cURL examples

API_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}ChatVLMLLM API Examples${NC}\n"

# 1. Health check
echo -e "${GREEN}1. Health Check${NC}"
curl -s "${API_URL}/health" | jq
echo -e "\n"

# 2. List models
echo -e "${GREEN}2. List Models${NC}"
curl -s "${API_URL}/models" | jq
echo -e "\n"

# 3. OCR - Extract text
echo -e "${GREEN}3. OCR - Extract Text${NC}"
curl -X POST "${API_URL}/ocr?model=qwen3_vl_2b" \
  -F "file=@test_image.jpg" \
  -s | jq
echo -e "\n"

# 4. OCR with language hint
echo -e "${GREEN}4. OCR with Language Hint${NC}"
curl -X POST "${API_URL}/ocr?model=qwen3_vl_2b&language=Russian" \
  -F "file=@test_image.jpg" \
  -s | jq
echo -e "\n"

# 5. Chat
echo -e "${GREEN}5. Chat with Image${NC}"
curl -X POST "${API_URL}/chat" \
  -F "file=@test_image.jpg" \
  -F "prompt=What's in this image?" \
  -F "model=qwen3_vl_4b" \
  -F "temperature=0.7" \
  -F "max_tokens=512" \
  -s | jq
echo -e "\n"

# 6. Batch OCR
echo -e "${GREEN}6. Batch OCR${NC}"
curl -X POST "${API_URL}/batch/ocr?model=qwen3_vl_2b" \
  -F "files=@doc1.jpg" \
  -F "files=@doc2.jpg" \
  -F "files=@doc3.jpg" \
  -s | jq
echo -e "\n"

# 7. Unload model
echo -e "${GREEN}7. Unload Model${NC}"
curl -X DELETE "${API_URL}/models/qwen3_vl_8b" -s | jq
echo -e "\n"

echo -e "${BLUE}Examples completed!${NC}"
echo -e "\nFor interactive documentation, visit: ${API_URL}/docs"