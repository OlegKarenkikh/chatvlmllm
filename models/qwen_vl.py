"""Qwen2-VL model implementation."""

from typing import Dict, List, Optional
from PIL import Image
import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

from .base_model import BaseVLMModel


class Qwen2VLModel(BaseVLMModel):
    """Qwen2-VL multimodal chat model."""
    
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
            
            # Load model with appropriate precision
            if self.precision == "fp16":
                self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                    self.model_id,
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    device_map=self.device
                )
            elif self.precision == "int8":
                self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                    self.model_id,
                    trust_remote_code=True,
                    load_in_8bit=True,
                    device_map=self.device
                )
            else:
                self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                    self.model_id,
                    trust_remote_code=True,
                    device_map=self.device
                )
            
            self.model.eval()
            print("Qwen2-VL model loaded successfully!")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load Qwen2-VL model: {str(e)}")
    
    def process_image(self, image: Image.Image, prompt: str = "") -> str:
        """Process image with text prompt.
        
        Args:
            image: PIL Image object
            prompt: Text prompt for the model
            
        Returns:
            Model response
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Default prompt for OCR
            if not prompt:
                prompt = "Extract all text from this image in the original layout."
            
            # Prepare inputs
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Apply chat template
            text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Process inputs
            inputs = self.processor(
                text=[text],
                images=[image],
                return_tensors="pt"
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=2048,
                    do_sample=False
                )
            
            # Decode response
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
            raise RuntimeError(f"Image processing failed: {str(e)}")
    
    def extract_fields(self, image: Image.Image, field_names: List[str]) -> Dict[str, str]:
        """Extract specific fields from document.
        
        Args:
            image: PIL Image object
            field_names: List of field names to extract
            
        Returns:
            Dictionary with extracted field values
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Create structured prompt for field extraction
            fields_list = "\n".join([f"- {field}" for field in field_names])
            prompt = f"""Extract the following information from this document and provide it in a structured format:

{fields_list}

For each field, provide the value or 'Not found' if not present. Format your response as:
Field Name: Value"""
            
            # Get model response
            response = self.process_image(image, prompt)
            
            # Parse response into fields
            extracted_fields = {}
            for field in field_names:
                extracted_fields[field] = ""
                
                # Try to find field in response
                for line in response.split('\n'):
                    if field.lower() in line.lower():
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            value = parts[1].strip()
                            if value.lower() != 'not found':
                                extracted_fields[field] = value
                        break
            
            return extracted_fields
            
        except Exception as e:
            raise RuntimeError(f"Field extraction failed: {str(e)}")
    
    def chat(self, image: Image.Image, message: str, history: Optional[List[Dict]] = None) -> str:
        """Interactive chat about an image.
        
        Args:
            image: PIL Image object
            message: User message
            history: Optional conversation history
            
        Returns:
            Model response
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Build conversation
            messages = history if history else []
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": message}
                ]
            })
            
            # Apply chat template
            text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Process and generate
            inputs = self.processor(
                text=[text],
                images=[image],
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=2048,
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
            
            # Update history
            messages.append({"role": "assistant", "content": response})
            self.conversation_history = messages
            
            return response
            
        except Exception as e:
            raise RuntimeError(f"Chat failed: {str(e)}")
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []