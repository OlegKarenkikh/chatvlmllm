"""Microsoft Phi-3.5 Vision model integration.

Official: https://huggingface.co/microsoft/Phi-3.5-vision-instruct
GitHub: https://github.com/microsoft/Phi-3CookBook

Phi-3.5 Vision is Microsoft's powerful vision-language model with:
- 4.2B parameters
- Strong multimodal capabilities
- Efficient inference
- Good performance on vision tasks
"""

from typing import Any, Dict, List, Optional, Union
from PIL import Image
import torch

from models.base_model import BaseModel
from utils.logger import logger


class Phi3VisionModel(BaseModel):
    """Microsoft Phi-3.5 Vision model."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.processor = None
        
        # Phi-3.5 Vision specific settings
        self.min_pixels = config.get('min_pixels', 256)
        self.max_pixels = config.get('max_pixels', 1280)
    
    def load_model(self) -> None:
        """Load Phi-3.5 Vision model."""
        try:
            logger.info(f"Loading Phi-3.5 Vision from {self.model_path}")
            
            from transformers import AutoModelForCausalLM, AutoProcessor
            
            device = self._get_device()
            logger.info(f"Using device: {device}")
            
            # Load processor
            self.processor = AutoProcessor.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            # Build loading kwargs
            load_kwargs = {
                'device_map': self.device_map,
                'trust_remote_code': True,
            }
            
            # Set precision
            if self.precision == "fp16":
                load_kwargs['torch_dtype'] = torch.float16
            elif self.precision == "bf16":
                load_kwargs['torch_dtype'] = torch.bfloat16
            elif self.precision == "int8":
                load_kwargs['load_in_8bit'] = True
            elif self.precision == "int4":
                from transformers import BitsAndBytesConfig
                load_kwargs['quantization_config'] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            
            # Enable Flash Attention 2 if requested and not disabled
            if self.config.get('use_flash_attention', False):
                try:
                    import flash_attn
                    load_kwargs['attn_implementation'] = "flash_attention_2"
                except ImportError:
                    logger.warning("Flash Attention not available, using standard attention")
                    # Don't set attn_implementation to avoid errors
            
            # Load model
            logger.info("Loading model weights...")
            
            # Try to load with eager attention first
            try:
                load_kwargs['attn_implementation'] = "eager"
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    **load_kwargs
                )
            except Exception as e:
                logger.warning(f"Failed with eager attention: {e}")
                # Remove attn_implementation and try default
                load_kwargs.pop('attn_implementation', None)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    **load_kwargs
                )
            
            self.model.eval()
            logger.info("Phi-3.5 Vision loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Phi-3.5 Vision: {e}")
            raise
    
    def process_image(
        self,
        image: Union[Image.Image, str],
        prompt: str = "Describe this image in detail.",
        **kwargs
    ) -> str:
        """Process image with Phi-3.5 Vision.
        
        Args:
            image: PIL Image or image path
            prompt: Text prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Model response
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            logger.info("Processing image with Phi-3.5 Vision")
            
            # Prepare messages in chat format
            messages = [
                {
                    "role": "user", 
                    "content": f"<|image_1|>\n{prompt}"
                }
            ]
            
            # Apply chat template
            prompt_text = self.processor.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # Process inputs
            inputs = self.processor(
                prompt_text, 
                [image], 
                return_tensors="pt"
            )
            
            # Move to device
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generation parameters
            gen_kwargs = {
                'max_new_tokens': kwargs.get('max_new_tokens', 512),
                'do_sample': kwargs.get('do_sample', False),
                'eos_token_id': self.processor.tokenizer.eos_token_id,
            }
            
            if kwargs.get('temperature'):
                gen_kwargs['temperature'] = kwargs['temperature']
                gen_kwargs['do_sample'] = True
            if kwargs.get('top_p'):
                gen_kwargs['top_p'] = kwargs['top_p']
                gen_kwargs['do_sample'] = True
            
            # Generate
            with torch.no_grad():
                generated_ids = self.model.generate(**inputs, **gen_kwargs)
            
            # Decode only the new tokens
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output = self.processor.tokenizer.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            logger.info("Processing completed")
            return output.strip()
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def chat(
        self,
        image: Union[Image.Image, str],
        prompt: str,
        **kwargs
    ) -> str:
        """Chat with Phi-3.5 Vision about image.
        
        Args:
            image: PIL Image or path
            prompt: User question
            **kwargs: Generation parameters
            
        Returns:
            Model response
        """
        return self.process_image(image, prompt, **kwargs)
    
    def extract_text(
        self,
        image: Union[Image.Image, str],
        language: Optional[str] = None
    ) -> str:
        """Extract text from image using Phi-3.5 Vision.
        
        Args:
            image: PIL Image or path
            language: Optional language hint
            
        Returns:
            Extracted text
        """
        prompt = "Extract all text from this image. "
        if language:
            prompt += f"The text is in {language}. "
        prompt += "Maintain the original structure and formatting. Only return the extracted text."
        
        return self.process_image(image, prompt, max_new_tokens=1024)
    
    def analyze_document(
        self,
        image: Union[Image.Image, str],
        focus: str = "general"
    ) -> str:
        """Analyze document with specific focus.
        
        Args:
            image: PIL Image or path
            focus: Analysis focus (general, layout, content, tables)
            
        Returns:
            Analysis result
        """
        prompts = {
            "general": "Analyze this document and provide a comprehensive summary of its content and structure.",
            "layout": "Describe the layout, structure, and visual organization of this document.",
            "content": "Extract and summarize the main content and key information from this document.",
            "tables": "Identify and extract all tables from this document. Format them clearly."
        }
        
        prompt = prompts.get(focus, prompts["general"])
        return self.process_image(image, prompt, max_new_tokens=1024)
    
    def unload(self) -> None:
        """Unload model from memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.processor is not None:
            del self.processor
            self.processor = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Phi-3.5 Vision unloaded")