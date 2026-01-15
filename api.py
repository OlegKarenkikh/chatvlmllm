"""ChatVLMLLM FastAPI REST API.

Provides REST endpoints for OCR and VLM chat.

Usage:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
    
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from PIL import Image
import io
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ChatVLMLLM API",
    description="REST API for Vision-Language Models OCR and Chat",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model cache
model_cache = {}

def get_model(model_name: str):
    """Load and cache model."""
    if model_name not in model_cache:
        try:
            from models import ModelLoader
            logger.info(f"Loading model: {model_name}")
            model_cache[model_name] = ModelLoader.load_model(model_name)
            logger.info(f"Model loaded successfully: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
    return model_cache[model_name]

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ChatVLMLLM API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check with GPU status."""
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if gpu_available else None
    except:
        gpu_available = False
        gpu_name = None
    
    return {
        "status": "healthy",
        "gpu_available": gpu_available,
        "gpu_name": gpu_name,
        "models_loaded": len(model_cache),
        "loaded_models": list(model_cache.keys())
    }

@app.get("/models")
async def list_models():
    """List available models."""
    return {
        "available": [
            {"id": "got_ocr", "name": "GOT-OCR 2.0", "params": "580M"},
            {"id": "qwen_vl_2b", "name": "Qwen2-VL 2B", "params": "2B"},
            {"id": "qwen_vl_7b", "name": "Qwen2-VL 7B", "params": "7B"},
            {"id": "qwen3_vl_2b", "name": "Qwen3-VL 2B", "params": "2B"},
            {"id": "qwen3_vl_4b", "name": "Qwen3-VL 4B", "params": "4B"},
            {"id": "qwen3_vl_8b", "name": "Qwen3-VL 8B", "params": "8B"},
            {"id": "dots_ocr", "name": "dots.ocr", "params": "1.7B"}
        ],
        "loaded": list(model_cache.keys())
    }

@app.post("/ocr")
async def extract_text(
    file: UploadFile = File(...),
    model: str = "qwen3_vl_2b",
    language: Optional[str] = None
):
    """Extract text from image.
    
    Args:
        file: Image file
        model: Model name (default: qwen3_vl_2b)
        language: Language hint (optional)
    
    Returns:
        Extracted text with metadata
    """
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        model_instance = get_model(model)
        start_time = time.time()
        
        # Process based on model type
        if "qwen3" in model:
            text = model_instance.extract_text(image, language=language)
        elif "qwen" in model:
            text = model_instance.chat(image, "Extract all text from this document.")
        elif model == "dots_ocr":
            result = model_instance.parse_document(image, return_json=False)
            text = result.get('raw_text', str(result))
        else:  # GOT-OCR
            text = model_instance.process_image(image)
        
        processing_time = time.time() - start_time
        
        return {
            "text": text,
            "model": model,
            "processing_time": processing_time,
            "image_size": list(image.size),
            "language": language
        }
        
    except Exception as e:
        logger.error(f"OCR error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_image(
    file: UploadFile = File(...),
    prompt: str = "Describe this image",
    model: str = "qwen3_vl_2b",
    temperature: float = 0.7,
    max_tokens: int = 512
):
    """Chat with VLM about an image.
    
    Args:
        file: Image file
        prompt: User prompt
        model: Model name
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Max tokens to generate
    
    Returns:
        Model response
    """
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        model_instance = get_model(model)
        start_time = time.time()
        
        if "qwen" in model:
            response = model_instance.chat(
                image=image,
                prompt=prompt,
                temperature=temperature,
                max_new_tokens=max_tokens
            )
        elif model == "dots_ocr":
            response = str(model_instance.process_image(image, prompt=prompt))
        else:  # GOT-OCR
            response = model_instance.process_image(image)
        
        processing_time = time.time() - start_time
        
        return {
            "response": response,
            "model": model,
            "processing_time": processing_time,
            "prompt": prompt
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch/ocr")
async def batch_ocr(
    files: List[UploadFile] = File(...),
    model: str = "qwen3_vl_2b"
):
    """Batch OCR processing.
    
    Args:
        files: List of image files
        model: Model name
    
    Returns:
        List of results
    """
    results = []
    
    for file in files:
        try:
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
            
            model_instance = get_model(model)
            start_time = time.time()
            
            if "qwen3" in model:
                text = model_instance.extract_text(image)
            elif "qwen" in model:
                text = model_instance.chat(image, "Extract all text.")
            else:
                text = model_instance.process_image(image)
            
            processing_time = time.time() - start_time
            
            results.append({
                "filename": file.filename,
                "text": text,
                "processing_time": processing_time,
                "status": "success"
            })
            
        except Exception as e:
            logger.error(f"Batch OCR error for {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "error": str(e),
                "status": "error"
            })
    
    successful = sum(1 for r in results if r["status"] == "success")
    
    return {
        "results": results,
        "total": len(files),
        "successful": successful,
        "failed": len(files) - successful
    }

@app.delete("/models/{model_name}")
async def unload_model(model_name: str):
    """Unload model from memory."""
    if model_name in model_cache:
        try:
            del model_cache[model_name]
            logger.info(f"Model unloaded: {model_name}")
            return {"status": "success", "message": f"Model {model_name} unloaded"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not loaded")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)