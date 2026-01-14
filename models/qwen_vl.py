"""Qwen2-VL model integration."""

from typing import Dict, Any, List, Optional
from PIL import Image
import torch
from .base_model import BaseVLMModel


class Qwen2VLModel(BaseVLMModel):
    """Qwen2-VL model for multimodal understanding."""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__(model_config)
        self.max_length = model_config.get("max_length", 4096)
        self.chat_history: List[Dict[str, str]] = []
        
    def load_model(self) -> None:
        """Load Qwen2-VL model."""
        try:
            from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
            
            print(f"Loading {self.model_name} from {self.model_id}...")
            
            # Load model with specified precision
            precision = self.model_config.get("precision", "fp16")
            torch_dtype = torch.float16 if precision == "fp16" else torch.float32
            
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                self.model_id,
                torch_dtype=torch_dtype,
                device_map=self.model_config.get("device_map", "auto"),
                trust_remote_code=True
            )
            
            self.processor = AutoProcessor.from_pretrained(
                self.model_id,
                trust_remote_code=True
            )
            
            self.model.eval()
            print(f"✓ {self.model_name} loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"✗ Error loading {self.model_name}: {str(e)}")
            raise
    
    def process_image(self, image: Image.Image, **kwargs) -> Dict[str, Any]:
        """Process image with Qwen2-VL."""
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            prompt = kwargs.get('prompt', 'Describe this image in detail.')
            temperature = kwargs.get('temperature', 0.7)
            max_new_tokens = kwargs.get('max_new_tokens', 512)
            
            # Prepare messages for Qwen2-VL
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Process with Qwen2-VL
            text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = self.processor(
                text=[text],
                images=[image],
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True
                )
            
            response = self.processor.batch_decode(
                outputs,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            return {
                'success': True,
                'text': response,
                'model': self.model_name,
                'prompt': prompt
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': self.model_name
            }
    
    def extract_text(self, image: Image.Image) -> str:
        """Extract text from image using OCR prompt."""
        result = self.process_image(
            image,
            prompt="Extract all text from this image. Preserve the layout and structure."
        )
        return result.get('text', '') if result.get('success') else ''
    
    def chat(self, image: Image.Image, message: str, **kwargs) -> str:
        """Chat with the model about the image."""
        result = self.process_image(image, prompt=message, **kwargs)
        
        if result.get('success'):
            response = result['text']
            self.chat_history.append({
                'role': 'user',
                'content': message
            })
            self.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            return response
        else:
            return f"Error: {result.get('error', 'Unknown error')}"
    
    def clear_chat_history(self) -> None:
        """Clear chat history."""
        self.chat_history = []