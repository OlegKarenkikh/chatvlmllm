"""Prompt processing service for ChatVLMLLM.

Centralized prompt processing that eliminates duplication across:
- Official prompts
- Example prompts  
- User input prompts
"""

import time
import torch
import gc
import re
from typing import Dict, Any, Optional
from PIL import Image

from core.error_handler import ErrorHandler


class PromptService:
    """Unified prompt processing service."""
    
    @staticmethod
    def process_prompt(
        image: Image.Image,
        prompt: str,
        selected_model: str,
        execution_mode: str,
        max_tokens: int,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Process a prompt with the selected model.
        
        This is the central function that handles all prompt processing,
        eliminating duplication between official prompts, examples, and user input.
        
        Args:
            image: PIL Image to process
            prompt: Text prompt
            selected_model: Model identifier
            execution_mode: "vLLM" or "Transformers"
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Returns:
            Dictionary with:
                - success: bool
                - text: str (response or error message)
                - processing_time: float
                - model_used: str
                - execution_mode: str
        """
        # Clean GPU memory before processing
        PromptService._clean_gpu_memory()
        
        start_time = time.time()
        
        try:
            if "vLLM" in execution_mode:
                result = PromptService._process_vllm(
                    image, prompt, selected_model, max_tokens, temperature
                )
            else:
                result = PromptService._process_transformers(
                    image, prompt, selected_model, max_tokens, temperature
                )
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "text": result,
                "processing_time": processing_time,
                "model_used": selected_model,
                "execution_mode": execution_mode
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_response = ErrorHandler.create_error_response(e, "обработка промпта")
            
            return {
                "success": False,
                "text": error_response,
                "processing_time": processing_time,
                "model_used": selected_model,
                "execution_mode": execution_mode,
                "error": str(e)
            }
    
    @staticmethod
    def _process_vllm(
        image: Image.Image,
        prompt: str,
        selected_model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Process prompt via vLLM.
        
        Args:
            image: PIL Image
            prompt: Text prompt
            selected_model: Model name
            max_tokens: Max tokens
            temperature: Temperature
            
        Returns:
            Response text
            
        Raises:
            Exception: If processing fails
        """
        try:
            from vllm_streamlit_adapter import VLLMStreamlitAdapter
            import streamlit as st
            
            # Get or create adapter
            if "vllm_adapter" not in st.session_state:
                st.session_state.vllm_adapter = VLLMStreamlitAdapter()
            
            adapter = st.session_state.vllm_adapter
            
            # Check if model is dots.ocr for special handling
            is_dots_ocr = "dots" in selected_model.lower()
            
            if is_dots_ocr:
                # Use safe token limit for dots.ocr
                vllm_model = "rednote-hilab/dots.ocr"
                model_max_tokens = adapter.get_model_max_tokens(vllm_model)
                safe_max_tokens = min(max_tokens, model_max_tokens - 500)
                
                if safe_max_tokens < 100:
                    safe_max_tokens = model_max_tokens // 2
                
                result = adapter.process_image(image, prompt, vllm_model, safe_max_tokens)
                
                if result and result["success"]:
                    response = result["text"]
                    processing_time = result["processing_time"]
                    
                    # Adapt response based on prompt type
                    response = PromptService._adapt_dots_ocr_response(
                        response, prompt, processing_time
                    )
                else:
                    raise Exception("vLLM processing failed")
            else:
                # Regular model processing with safe token limit
                model_max_tokens = adapter.get_model_max_tokens(selected_model)
                safe_max_tokens = min(max_tokens, model_max_tokens - 500)
                
                if safe_max_tokens < 100:
                    safe_max_tokens = model_max_tokens // 2
                
                result = adapter.process_image(image, prompt, selected_model, safe_max_tokens)
                
                if result and result["success"]:
                    response = result["text"]
                    processing_time = result["processing_time"]
                    response += f"\n\n*🚀 Обработано через vLLM за {processing_time:.2f}с*"
                else:
                    raise Exception("vLLM processing failed")
            
            return response
            
        except Exception as e:
            # Try fallback to Transformers if not a critical error
            if not ErrorHandler.is_cuda_error(e):
                return PromptService._process_transformers(
                    image, prompt, selected_model, max_tokens, temperature
                )
            raise
    
    @staticmethod
    def _process_transformers(
        image: Image.Image,
        prompt: str,
        selected_model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Process prompt via Transformers.
        
        Args:
            image: PIL Image
            prompt: Text prompt
            selected_model: Model name
            max_tokens: Max tokens
            temperature: Temperature
            
        Returns:
            Response text
            
        Raises:
            Exception: If processing fails
        """
        from models.model_loader import ModelLoader
        
        model = ModelLoader.load_model(selected_model)
        
        # Get response based on model capabilities
        if hasattr(model, 'chat'):
            response = model.chat(
                image=image,
                prompt=prompt,
                temperature=temperature,
                max_new_tokens=max_tokens
            )
        elif hasattr(model, 'process_image'):
            # For OCR models, adapt based on prompt
            if any(word in prompt.lower() for word in ['текст', 'прочитай', 'извлеки']):
                response = model.process_image(image)
            else:
                ocr_text = model.process_image(image)
                response = f"Это OCR модель. Извлеченный текст:\n\n{ocr_text}"
        else:
            response = "Модель не поддерживает чат. Попробуйте режим OCR."
        
        processing_time = time.time() - time.time()  # Will be calculated in main function
        response += f"\n\n*🔧 Обработано локально с помощью {selected_model}*"
        
        return response
    
    @staticmethod
    def _adapt_dots_ocr_response(response: str, prompt: str, processing_time: float) -> str:
        """Adapt dots.ocr response based on prompt type.
        
        Args:
            response: Model response
            prompt: Original prompt
            processing_time: Processing time
            
        Returns:
            Adapted response
        """
        # Check prompt type
        if any(word in prompt.lower() for word in ['текст', 'прочитай', 'извлеки', 'text', 'extract', 'read']):
            # OCR question - return as is
            pass
        elif any(word in prompt.lower() for word in ['число', 'number']):
            # Number question - extract numbers
            numbers = re.findall(r'\d+', response)
            if numbers:
                response = f"В изображении найдены числа: {', '.join(numbers)}"
            else:
                response = "В изображении не найдено чисел."
        elif any(word in prompt.lower() for word in ['сколько', 'how many']):
            # Count question
            words = len(response.split())
            response = f"В тексте примерно {words} слов."
        elif any(word in prompt.lower() for word in ['есть ли', 'is there']):
            # Existence question
            if 'текст' in prompt.lower() or 'text' in prompt.lower():
                response = f"Да, в изображении есть текст:\n\n{response}"
            else:
                response = f"dots.ocr может определить только наличие текста. Найденный текст:\n\n{response}"
        else:
            # General analytical question
            response = f"dots.ocr специализирована на OCR. Вот распознанный текст, который может помочь ответить на ваш вопрос:\n\n{response}\n\n💡 Для детального анализа изображений используйте Qwen3-VL в настройках модели."
        
        # Add timing info
        response += f"\n\n*🚀 Обработано через vLLM за {processing_time:.2f}с*"
        
        return response
    
    @staticmethod
    def _clean_gpu_memory():
        """Clean GPU memory before processing."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        gc.collect()
