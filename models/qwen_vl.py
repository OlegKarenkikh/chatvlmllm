"""Qwen2-VL model integration."""

from typing import Optional, List, Dict
from PIL import Image
import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

from .base_model import BaseVLMModel


class Qwen2VLModel(BaseVLMModel):
    """Qwen2-VL multimodal model for chat and OCR."""
    
    def load_model(self) -> None:
        """Load Qwen2-VL model and processor."""
        print(f"Loading Qwen2-VL model: {self.model_id}")
        
        try:
            # Load processor
            self.processor = AutoProcessor.from_pretrained(
                self.model_id,
                trust_remote_code=True
            )
            
            # Load model
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                self.model_id,
                trust_remote_code=True,
                device_map=self.config.get("device_map", "auto"),
                torch_dtype=torch.float16 if self.config.get("precision") == "fp16" else torch.float32,
                attn_implementation="flash_attention_2" if torch.cuda.is_available() else "eager"
            )
            
            self.model.eval()
            print(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback without flash attention
            try:
                self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                    self.model_id,
                    trust_remote_code=True,
                    device_map=self.config.get("device_map", "auto"),
                    torch_dtype=torch.float16 if self.config.get("precision") == "fp16" else torch.float32
                )
                self.model.eval()
                print("Model loaded without flash attention")
            except Exception as e2:
                print(f"Error loading model (fallback): {e2}")
                raise
    
    def process_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        """
        Process image with Qwen2-VL.
        
        Args:
            image: PIL Image object
            prompt: User prompt or question about the image
            
        Returns:
            Model response
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Default prompt for OCR
            if prompt is None:
                prompt = "Extract all text from this image in the original format and structure."
            
            # Prepare conversation format
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Prepare inputs
            text_prompt = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = self.processor(
                text=[text_prompt],
                images=[image],
                return_tensors="pt",
                padding=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=self.config.get("max_length", 2048),
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
    
    def chat(self, image: Image.Image, message: str, history: List[Dict[str, str]] = None) -> str:
        """
        Interactive chat with image context.
        
        Args:
            image: Context image
            message: User message
            history: Previous conversation history
            
        Returns:
            Model response
        """
        if self.model is None:
            raise RuntimeError("Model not loaded.")
        
        try:
            # Build conversation with history
            messages = []
            
            # Add history if provided
            if history:
                for msg in history:
                    messages.append({
                        "role": msg["role"],
                        "content": [{"type": "text", "text": msg["content"]}]
                    })
            
            # Add current message with image
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": message}
                ]
            })
            
            # Process with model
            text_prompt = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = self.processor(
                text=[text_prompt],
                images=[image],
                return_tensors="pt",
                padding=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=self.config.get("max_length", 2048),
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True
                )
            
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