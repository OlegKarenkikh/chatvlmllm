"""Qwen2-VL model integration."""

from typing import List, Dict, Optional
from PIL import Image
import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

from .base_model import BaseVLMModel


class Qwen2VLModel(BaseVLMModel):
    """Qwen2-VL multimodal model."""
    
    def __init__(self, model_id: str = "Qwen/Qwen2-VL-2B-Instruct", **kwargs):
        super().__init__(model_id, **kwargs)
        self.conversation_history = []
        
    def load_model(self) -> None:
        """Load Qwen2-VL model and processor."""
        try:
            print(f"Loading Qwen2-VL model from {self.model_id}...")
            
            # Load processor
            self.processor = AutoProcessor.from_pretrained(
                self.model_id,
                trust_remote_code=True
            )
            
            # Load model with appropriate settings
            load_kwargs = {
                "trust_remote_code": True,
            }
            
            if self.device == "cuda":
                load_kwargs["device_map"] = "auto"
                if self.precision == "fp16":
                    load_kwargs["torch_dtype"] = torch.float16
                elif self.precision == "int8":
                    load_kwargs["load_in_8bit"] = True
            
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                self.model_id,
                **load_kwargs
            )
            
            print(f"Qwen2-VL model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"Error loading Qwen2-VL model: {e}")
            raise
    
    def process_image(self, image: Image.Image, prompt: str = "") -> str:
        """
        Process image with Qwen2-VL.
        
        Args:
            image: PIL Image to process
            prompt: Instruction for the model
            
        Returns:
            Model response
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Default OCR prompt if none provided
            if not prompt:
                prompt = "Extract all text from this image in a structured format."
            
            # Prepare input
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Process with model
            text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = self.processor(
                text=[text],
                images=[image],
                padding=True,
                return_tensors="pt"
            )
            
            if self.device == "cuda":
                inputs = inputs.to("cuda")
            
            # Generate response
            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=2048,
                    do_sample=False
                )
            
            # Decode output
            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids in zip(inputs.input_ids, output_ids)
            ]
            
            response = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            return response
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return f"Error: {str(e)}"
    
    def chat(self, image: Image.Image, message: str, history: List[Dict] = None) -> str:
        """
        Interactive chat with Qwen2-VL.
        
        Args:
            image: PIL Image for context
            message: User message
            history: Previous conversation
            
        Returns:
            Model response
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Build conversation
            messages = []
            
            # Add history if provided
            if history:
                for h in history:
                    messages.append(h)
            
            # Add current message with image
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": message}
                ]
            })
            
            # Process
            text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = self.processor(
                text=[text],
                images=[image],
                padding=True,
                return_tensors="pt"
            )
            
            if self.device == "cuda":
                inputs = inputs.to("cuda")
            
            # Generate
            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=2048,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True
                )
            
            # Decode
            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids in zip(inputs.input_ids, output_ids)
            ]
            
            response = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            return response
            
        except Exception as e:
            print(f"Error in chat: {e}")
            return f"Error: {str(e)}"
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []