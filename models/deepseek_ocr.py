"""DeepSeek OCR model integration.

Official: https://huggingface.co/deepseek-ai/deepseek-ocr
GitHub: https://github.com/deepseek-ai

DeepSeek OCR is a lightweight OCR model from DeepSeek AI with:
- Efficient inference
- Good accuracy for document OCR
- Small model size
- Fast processing
"""

from typing import Any, Dict, Optional, Union
from PIL import Image
import torch

from models.base_model import BaseModel
from utils.logger import logger


class DeepSeekOCRModel(BaseModel):
    """DeepSeek OCR model."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.processor = None
    
    def load_model(self) -> None:
        """Load DeepSeek OCR model."""
        try:
            logger.info(f"Loading DeepSeek OCR from {self.model_path}")
            
            device = self._get_device()
            logger.info(f"Using device: {device}")
            
            # Try different import strategies
            try:
                from transformers import AutoModel, AutoProcessor
                model_class = AutoModel
                processor_class = AutoProcessor
            except ImportError as e:
                logger.warning(f"Standard imports failed: {e}")
                try:
                    from transformers import AutoModelForCausalLM, AutoTokenizer
                    model_class = AutoModelForCausalLM
                    processor_class = AutoTokenizer
                except ImportError as e2:
                    logger.error(f"Fallback imports also failed: {e2}")
                    raise e2
            
            # Load processor with multiple fallbacks
            try:
                self.processor = processor_class.from_pretrained(
                    self.model_path,
                    trust_remote_code=True
                )
                logger.info("Processor loaded successfully")
            except Exception as proc_error:
                logger.warning(f"Processor loading failed: {proc_error}")
                try:
                    # Try tokenizer as fallback
                    from transformers import AutoTokenizer
                    self.processor = AutoTokenizer.from_pretrained(
                        self.model_path,
                        trust_remote_code=True
                    )
                    logger.info("Fallback tokenizer loaded")
                except Exception as tok_error:
                    logger.error(f"Tokenizer fallback also failed: {tok_error}")
                    # Create dummy processor
                    self.processor = None
                    logger.warning("Using dummy processor")
            
            # Build loading kwargs using base class method
            load_kwargs = self._get_load_kwargs()
            
            # Load model with error handling
            logger.info("Loading model weights...")
            try:
                self.model = model_class.from_pretrained(
                    self.model_path,
                    **load_kwargs
                )
                logger.info("Model loaded with AutoModel")
            except Exception as model_error:
                logger.warning(f"AutoModel failed: {model_error}")
                try:
                    # Try AutoModelForCausalLM
                    from transformers import AutoModelForCausalLM
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        **load_kwargs
                    )
                    logger.info("Model loaded with AutoModelForCausalLM")
                except Exception as causal_error:
                    logger.error(f"AutoModelForCausalLM also failed: {causal_error}")
                    raise causal_error
            
            self.model.eval()
            logger.info("DeepSeek OCR loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load DeepSeek OCR: {e}")
            # Don't raise, return error message instead
            self.model = None
            self.processor = None
            logger.warning("DeepSeek OCR loading failed, model will return error messages")
    
    def process_image(
        self,
        image: Union[Image.Image, str],
        prompt: Optional[str] = None
    ) -> str:
        """Process image with DeepSeek OCR.
        
        Args:
            image: PIL Image or image path
            prompt: Optional prompt (for OCR, usually not needed)
            
        Returns:
            Extracted text
        """
        if self.model is None:
            return "[DeepSeek OCR model not loaded - check model availability]"
        
        if self.processor is None:
            return "[DeepSeek OCR processor not available - using fallback]"
        
        try:
            logger.info("Processing image with DeepSeek OCR")
            
            # Ensure image is PIL Image
            if isinstance(image, str):
                image = Image.open(image)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Try different processing approaches
            try:
                # Method 1: Standard processor
                if hasattr(self.processor, 'process'):
                    inputs = self.processor.process(image, return_tensors="pt")
                elif hasattr(self.processor, '__call__'):
                    inputs = self.processor(image, return_tensors="pt")
                else:
                    raise AttributeError("Processor has no callable method")
                    
            except Exception as proc_error:
                logger.warning(f"Standard processing failed: {proc_error}")
                try:
                    # Method 2: Text + image processing
                    text_prompt = prompt or "Extract all text from this image"
                    inputs = self.processor(
                        text=text_prompt,
                        images=image,
                        return_tensors="pt",
                        padding=True
                    )
                except Exception as text_proc_error:
                    logger.warning(f"Text processing failed: {text_proc_error}")
                    # Method 3: Basic preprocessing fallback
                    inputs = self._preprocess_image(image)
            
            # Move to device
            device = next(self.model.parameters()).device
            if isinstance(inputs, dict):
                inputs = {k: v.to(device) if torch.is_tensor(v) else v for k, v in inputs.items()}
            else:
                inputs = inputs.to(device)
            
            # Generate text with multiple strategies
            with torch.no_grad():
                try:
                    # Strategy 1: Generate method
                    if hasattr(self.model, 'generate'):
                        gen_kwargs = {
                            'max_new_tokens': 2048,
                            'do_sample': False,
                            'use_cache': False  # Avoid cache issues
                        }
                        
                        if hasattr(self.processor, 'pad_token_id') and self.processor.pad_token_id is not None:
                            gen_kwargs['pad_token_id'] = self.processor.pad_token_id
                        elif hasattr(self.processor, 'eos_token_id') and self.processor.eos_token_id is not None:
                            gen_kwargs['pad_token_id'] = self.processor.eos_token_id
                        
                        outputs = self.model.generate(
                            **inputs if isinstance(inputs, dict) else {'input_ids': inputs},
                            **gen_kwargs
                        )
                        
                        # Decode output
                        if hasattr(self.processor, 'decode'):
                            result = self.processor.decode(outputs[0], skip_special_tokens=True)
                        elif hasattr(self.processor, 'batch_decode'):
                            result = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
                        else:
                            result = self._decode_output(outputs[0])
                            
                    elif hasattr(self.model, 'forward'):
                        # Strategy 2: Direct forward pass
                        outputs = self.model(**inputs if isinstance(inputs, dict) else {'input_ids': inputs})
                        result = self._process_outputs(outputs)
                    else:
                        # Strategy 3: Basic inference
                        result = self._basic_inference(image)
                        
                except Exception as gen_error:
                    logger.error(f"Generation failed: {gen_error}")
                    result = f"[DeepSeek OCR processing error: {gen_error}]"
            
            logger.info("OCR processing completed")
            return result.strip() if isinstance(result, str) else str(result)
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return f"[DeepSeek OCR error: {e}]"
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Basic image preprocessing fallback."""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Basic tensor conversion (placeholder)
        import torchvision.transforms as transforms
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        return transform(image).unsqueeze(0)
    
    def _decode_output(self, output_ids: torch.Tensor) -> str:
        """Basic output decoding fallback."""
        # This is a placeholder - actual implementation depends on model
        return f"[DeepSeek OCR output - tokens: {output_ids.shape}]"
    
    def _process_outputs(self, outputs) -> str:
        """Process model outputs."""
        # This is a placeholder - actual implementation depends on model architecture
        return "[DeepSeek OCR result - implement based on model outputs]"
    
    def _basic_inference(self, image: Image.Image) -> str:
        """Basic inference fallback."""
        return "[DeepSeek OCR inference - implement based on model API]"
    
    def chat(
        self,
        image: Union[Image.Image, str],
        prompt: str,
        **kwargs
    ) -> str:
        """Chat interface (primarily returns OCR result).
        
        Args:
            image: PIL Image or path
            prompt: User prompt
            **kwargs: Additional parameters
            
        Returns:
            OCR result or model response
        """
        # For OCR models, we primarily extract text
        ocr_result = self.process_image(image)
        
        # If prompt asks for specific processing, we could add logic here
        if "extract" in prompt.lower() or "ocr" in prompt.lower():
            return ocr_result
        else:
            return f"OCR Result: {ocr_result}"
    
    def extract_text(
        self,
        image: Union[Image.Image, str],
        language: Optional[str] = None
    ) -> str:
        """Extract text from image.
        
        Args:
            image: PIL Image or path
            language: Optional language hint (may not be used by all models)
            
        Returns:
            Extracted text
        """
        return self.process_image(image)
    
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
        logger.info("DeepSeek OCR unloaded")