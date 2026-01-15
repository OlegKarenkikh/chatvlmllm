"""Image preprocessing utilities."""

from typing import Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np


class ImageProcessor:
    """Image preprocessing for OCR optimization."""
    
    @staticmethod
    def load_image(image_path: str) -> Image.Image:
        """Load image from file path."""
        return Image.open(image_path).convert("RGB")
    
    @staticmethod
    def resize_image(
        image: Image.Image,
        max_dimension: int = 2048,
        maintain_aspect: bool = True
    ) -> Image.Image:
        """
        Resize image to maximum dimension.
        
        Args:
            image: Input PIL Image
            max_dimension: Maximum width or height
            maintain_aspect: Keep aspect ratio
            
        Returns:
            Resized image
        """
        width, height = image.size
        
        if width <= max_dimension and height <= max_dimension:
            return image
        
        if maintain_aspect:
            if width > height:
                new_width = max_dimension
                new_height = int((max_dimension / width) * height)
            else:
                new_height = max_dimension
                new_width = int((max_dimension / height) * width)
        else:
            new_width = new_height = max_dimension
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    @staticmethod
    def enhance_image(
        image: Image.Image,
        contrast: float = 1.2,
        sharpness: float = 1.5,
        brightness: float = 1.0
    ) -> Image.Image:
        """
        Enhance image for better OCR results.
        
        Args:
            image: Input PIL Image
            contrast: Contrast factor (1.0 = original)
            sharpness: Sharpness factor
            brightness: Brightness factor
            
        Returns:
            Enhanced image
        """
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(sharpness)
        
        # Adjust brightness
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        return image
    
    @staticmethod
    def denoise_image(image: Image.Image, strength: int = 10) -> Image.Image:
        """
        Remove noise from image.
        
        Args:
            image: Input PIL Image
            strength: Denoising strength
            
        Returns:
            Denoised image
        """
        # Convert to numpy array
        img_array = np.array(image)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoisingColored(
            img_array,
            None,
            strength,
            strength,
            7,
            21
        )
        
        return Image.fromarray(denoised)
    
    @staticmethod
    def deskew_image(image: Image.Image) -> Image.Image:
        """
        Correct image skew/rotation.
        
        Args:
            image: Input PIL Image
            
        Returns:
            Deskewed image
        """
        # Convert to numpy array
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is not None:
            # Calculate average angle
            angles = []
            for line in lines:
                rho, theta = line[0]
                angle = theta * 180 / np.pi
                if 85 < angle < 95 or -5 < angle < 5:
                    angles.append(angle)
            
            if angles:
                median_angle = np.median(angles)
                rotation_angle = median_angle - 90 if median_angle > 45 else median_angle
                
                # Rotate image
                if abs(rotation_angle) > 0.5:
                    return image.rotate(rotation_angle, expand=True, fillcolor=(255, 255, 255))
        
        return image
    
    @staticmethod
    def preprocess(
        image: Image.Image,
        resize: bool = True,
        enhance: bool = True,
        denoise: bool = False,
        deskew: bool = False,
        max_dimension: int = 2048
    ) -> Image.Image:
        """
        Full preprocessing pipeline.
        
        Args:
            image: Input PIL Image
            resize: Apply resizing
            enhance: Apply enhancement
            denoise: Apply denoising
            deskew: Apply deskewing
            max_dimension: Maximum dimension for resizing
            
        Returns:
            Preprocessed image
        """
        if resize:
            image = ImageProcessor.resize_image(image, max_dimension)
        
        if deskew:
            image = ImageProcessor.deskew_image(image)
        
        if denoise:
            image = ImageProcessor.denoise_image(image)
        
        if enhance:
            image = ImageProcessor.enhance_image(image)
        
        return image