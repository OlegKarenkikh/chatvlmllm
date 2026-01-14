"""Image preprocessing utilities."""

from typing import Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2


class ImageProcessor:
    """Utility class for image preprocessing."""
    
    @staticmethod
    def preprocess(
        image: Image.Image,
        resize: bool = True,
        max_dimension: int = 2048,
        enhance: bool = True,
        denoise: bool = False
    ) -> Image.Image:
        """
        Preprocess image for OCR.
        
        Args:
            image: Input PIL Image
            resize: Whether to resize image
            max_dimension: Maximum dimension for resizing
            enhance: Whether to enhance contrast and sharpness
            denoise: Whether to apply denoising
            
        Returns:
            Preprocessed PIL Image
        """
        processed = image.copy()
        
        # Convert to RGB if needed
        if processed.mode != 'RGB':
            processed = processed.convert('RGB')
        
        # Resize if needed
        if resize:
            processed = ImageProcessor.resize_image(processed, max_dimension)
        
        # Enhance image
        if enhance:
            processed = ImageProcessor.enhance_image(processed)
        
        # Denoise
        if denoise:
            processed = ImageProcessor.denoise_image(processed)
        
        return processed
    
    @staticmethod
    def resize_image(image: Image.Image, max_dimension: int) -> Image.Image:
        """Resize image while maintaining aspect ratio."""
        width, height = image.size
        
        if max(width, height) <= max_dimension:
            return image
        
        # Calculate new dimensions
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    @staticmethod
    def enhance_image(image: Image.Image) -> Image.Image:
        """Enhance image contrast and sharpness."""
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)
        
        return image
    
    @staticmethod
    def denoise_image(image: Image.Image) -> Image.Image:
        """Apply denoising to image."""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Apply bilateral filter for denoising
        denoised = cv2.bilateralFilter(img_array, 9, 75, 75)
        
        # Convert back to PIL Image
        return Image.fromarray(denoised)
    
    @staticmethod
    def deskew_image(image: Image.Image) -> Image.Image:
        """Deskew image (correct rotation)."""
        img_array = np.array(image.convert('L'))
        
        # Detect angle
        coords = np.column_stack(np.where(img_array > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Rotate image
        (h, w) = img_array.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            np.array(image),
            M,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return Image.fromarray(rotated)
    
    @staticmethod
    def get_image_info(image: Image.Image) -> dict:
        """Get image information."""
        return {
            'size': image.size,
            'mode': image.mode,
            'format': image.format,
            'width': image.width,
            'height': image.height,
            'aspect_ratio': image.width / image.height
        }