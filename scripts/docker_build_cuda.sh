#!/bin/bash
# Docker Build Script for ChatVLMLLM with CUDA support
# Optimized for WSL2 with NVIDIA GPU
#
# Usage:
#   ./scripts/docker_build_cuda.sh [options]
#
# Options:
#   --no-cache    Build without using cache
#   --push        Push to registry after build
#   --test        Run test after build
#   --help        Show this help

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="chatvlmllm"
IMAGE_TAG="cuda"
DOCKERFILE="Dockerfile.cuda"
COMPOSE_FILE="docker-compose.cuda.yml"

# Parse arguments
NO_CACHE=""
DO_PUSH=false
DO_TEST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --push)
            DO_PUSH=true
            shift
            ;;
        --test)
            DO_TEST=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --no-cache    Build without using cache"
            echo "  --push        Push to registry after build"
            echo "  --test        Run test after build"
            echo "  --help        Show this help"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     ChatVLMLLM Docker Build (CUDA)                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# Check if we're in the right directory
if [ ! -f "$DOCKERFILE" ]; then
    echo -e "${RED}Error: $DOCKERFILE not found!${NC}"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

# Check NVIDIA driver
if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n1)
    echo -e "${GREEN}✓ NVIDIA GPU detected: ${GPU_NAME}${NC}"
else
    echo -e "${YELLOW}⚠ nvidia-smi not found. GPU may not be available.${NC}"
fi

# Check Docker GPU access
echo -e "\n${YELLOW}Testing Docker GPU access...${NC}"
if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ Docker can access GPU${NC}"
else
    echo -e "${RED}✗ Docker cannot access GPU${NC}"
    echo -e "${YELLOW}Please install NVIDIA Container Toolkit and restart Docker.${NC}"
    echo "See: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build
echo -e "\n${YELLOW}Building Docker image...${NC}"
echo -e "Image: ${BLUE}${IMAGE_NAME}:${IMAGE_TAG}${NC}"
echo -e "Dockerfile: ${BLUE}${DOCKERFILE}${NC}"

BUILD_START=$(date +%s)

if [ -n "$NO_CACHE" ]; then
    echo -e "${YELLOW}Building without cache...${NC}"
fi

# Use docker compose for building (better caching)
docker compose -f "$COMPOSE_FILE" build $NO_CACHE chatvlmllm

BUILD_END=$(date +%s)
BUILD_TIME=$((BUILD_END - BUILD_START))

echo -e "\n${GREEN}✓ Build completed in ${BUILD_TIME} seconds${NC}"

# Show image info
echo -e "\n${YELLOW}Image information:${NC}"
docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# Test if requested
if [ "$DO_TEST" = true ]; then
    echo -e "\n${YELLOW}Running tests...${NC}"
    
    # Start container
    docker compose -f "$COMPOSE_FILE" up -d
    
    # Wait for container to be healthy
    echo "Waiting for container to be ready..."
    for i in {1..30}; do
        if docker compose -f "$COMPOSE_FILE" ps | grep -q "healthy"; then
            echo -e "${GREEN}✓ Container is healthy${NC}"
            break
        fi
        sleep 5
    done
    
    # Test GPU access in container
    echo -e "\n${YELLOW}Testing GPU in container...${NC}"
    docker compose -f "$COMPOSE_FILE" exec chatvlmllm python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
    
    # Stop container
    docker compose -f "$COMPOSE_FILE" down
fi

# Push if requested
if [ "$DO_PUSH" = true ]; then
    echo -e "\n${YELLOW}Pushing image to registry...${NC}"
    docker push "${IMAGE_NAME}:${IMAGE_TAG}"
    echo -e "${GREEN}✓ Image pushed${NC}"
fi

# Final message
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Build Complete!                                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}To start the container:${NC}"
echo "  docker compose -f docker-compose.cuda.yml up -d"

echo -e "\n${BLUE}To view logs:${NC}"
echo "  docker compose -f docker-compose.cuda.yml logs -f"

echo -e "\n${BLUE}To stop:${NC}"
echo "  docker compose -f docker-compose.cuda.yml down"

echo -e "\n${BLUE}Access the UI at:${NC}"
echo "  http://localhost:8501"
