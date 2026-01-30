"""Visualization utilities for OCR results."""

from typing import List, Tuple, Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2


class ResultVisualizer:
    """Visualize OCR and extraction results on images."""
    
    # Color scheme
    COLORS = {
        'text': (0, 255, 0),      # Green for text regions
        'field': (255, 165, 0),   # Orange for extracted fields
        'highlight': (255, 0, 0),  # Red for highlights
        'box': (0, 150, 255),     # Blue for bounding boxes
    }
    
    @staticmethod
    def draw_text_overlay(
        image: Image.Image,
        text: str,
        position: str = 'bottom',
        alpha: float = 0.7
    ) -> Image.Image:
        """
        Draw semi-transparent text overlay on image.
        
        Args:
            image: Input PIL Image
            text: Text to overlay
            position: Position ('top' or 'bottom')
            alpha: Transparency (0-1)
            
        Returns:
            Image with text overlay
        """
        img_array = np.array(image)
        overlay = img_array.copy()
        
        height, width = img_array.shape[:2]
        
        # Create text area
        if position == 'bottom':
            y_start = int(height * 0.85)
            y_end = height
        else:
            y_start = 0
            y_end = int(height * 0.15)
        
        # Draw semi-transparent rectangle
        cv2.rectangle(
            overlay,
            (0, y_start),
            (width, y_end),
            (0, 0, 0),
            -1
        )
        
        # Blend with original
        result = cv2.addWeighted(img_array, 1 - alpha, overlay, alpha, 0)
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        color = (255, 255, 255)
        
        # Split text into lines if too long
        max_width = width - 40
        lines = ResultVisualizer._wrap_text(text, font, font_scale, thickness, max_width)
        
        y_offset = y_start + 30
        for line in lines:
            cv2.putText(
                result,
                line,
                (20, y_offset),
                font,
                font_scale,
                color,
                thickness
            )
            y_offset += 30
        
        return Image.fromarray(result)
    
    @staticmethod
    def draw_boxes(
        image: Image.Image,
        boxes: List[Tuple[int, int, int, int]],
        labels: Optional[List[str]] = None,
        color_key: str = 'box'
    ) -> Image.Image:
        """
        Draw bounding boxes on image.
        
        Args:
            image: Input PIL Image
            boxes: List of boxes [(x1, y1, x2, y2), ...]
            labels: Optional labels for each box
            color_key: Color scheme key
            
        Returns:
            Image with boxes drawn
        """
        img_array = np.array(image)
        result = img_array.copy()
        
        color = ResultVisualizer.COLORS.get(color_key, (0, 255, 0))
        
        for idx, (x1, y1, x2, y2) in enumerate(boxes):
            # Draw rectangle
            cv2.rectangle(result, (x1, y1), (x2, y2), color, 2)
            
            # Draw label if provided
            if labels and idx < len(labels):
                label = labels[idx]
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 1
                
                # Get text size
                (text_width, text_height), _ = cv2.getTextSize(
                    label, font, font_scale, thickness
                )
                
                # Draw label background
                cv2.rectangle(
                    result,
                    (x1, y1 - text_height - 10),
                    (x1 + text_width + 10, y1),
                    color,
                    -1
                )
                
                # Draw label text
                cv2.putText(
                    result,
                    label,
                    (x1 + 5, y1 - 5),
                    font,
                    font_scale,
                    (255, 255, 255),
                    thickness
                )
        
        return Image.fromarray(result)
    
    @staticmethod
    def create_comparison(
        original: Image.Image,
        processed: Image.Image,
        title1: str = "Original",
        title2: str = "Processed"
    ) -> Image.Image:
        """
        Create side-by-side comparison of images.
        
        Args:
            original: Original image
            processed: Processed image
            title1: Title for original
            title2: Title for processed
            
        Returns:
            Combined comparison image
        """
        # Resize images to same height
        target_height = min(original.height, processed.height)
        
        orig_ratio = original.width / original.height
        proc_ratio = processed.width / processed.height
        
        orig_resized = original.resize(
            (int(target_height * orig_ratio), target_height),
            Image.Resampling.LANCZOS
        )
        proc_resized = processed.resize(
            (int(target_height * proc_ratio), target_height),
            Image.Resampling.LANCZOS
        )
        
        # Create combined image
        total_width = orig_resized.width + proc_resized.width + 20
        combined = Image.new('RGB', (total_width, target_height + 40), (255, 255, 255))
        
        # Paste images
        combined.paste(orig_resized, (10, 40))
        combined.paste(proc_resized, (orig_resized.width + 10, 40))
        
        # Add titles
        draw = ImageDraw.Draw(combined)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Draw titles
        draw.text((10, 10), title1, fill=(0, 0, 0), font=font)
        draw.text((orig_resized.width + 10, 10), title2, fill=(0, 0, 0), font=font)
        
        return combined
    
    @staticmethod
    def highlight_text_regions(
        image: Image.Image,
        text: str,
        confidence: float = 0.0
    ) -> Image.Image:
        """
        Highlight detected text regions with confidence-based coloring.
        
        Args:
            image: Input image
            text: Detected text (for visualization)
            confidence: OCR confidence score
            
        Returns:
            Image with highlighted regions
        """
        img_array = np.array(image)
        overlay = img_array.copy()
        
        # Color based on confidence
        if confidence > 0.8:
            color = (0, 255, 0)  # Green - high confidence
        elif confidence > 0.5:
            color = (255, 165, 0)  # Orange - medium confidence
        else:
            color = (255, 0, 0)  # Red - low confidence
        
        # Add border with confidence color
        border_size = 5
        cv2.rectangle(
            overlay,
            (border_size, border_size),
            (img_array.shape[1] - border_size, img_array.shape[0] - border_size),
            color,
            border_size * 2
        )
        
        # Blend
        result = cv2.addWeighted(img_array, 0.7, overlay, 0.3, 0)
        
        return Image.fromarray(result)
    
    @staticmethod
    def _wrap_text(
        text: str,
        font: int,
        font_scale: float,
        thickness: int,
        max_width: int
    ) -> List[str]:
        """Wrap text to fit within max width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            (text_width, _), _ = cv2.getTextSize(
                test_line, font, font_scale, thickness
            )
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    @staticmethod
    def create_result_card(
        image: Image.Image,
        stats: Dict[str, Any],
        title: str = "OCR Results"
    ) -> Image.Image:
        """
        Create a visual card showing image and statistics.
        
        Args:
            image: Processed image
            stats: Statistics dictionary
            title: Card title
            
        Returns:
            Result card image
        """
        # Resize image
        max_size = 800
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Create card
        card_width = image.width + 40
        stats_height = len(stats) * 30 + 100
        card_height = image.height + stats_height + 60
        
        card = Image.new('RGB', (card_width, card_height), (245, 245, 245))
        
        # Paste image
        card.paste(image, (20, 50))
        
        # Add title and stats
        draw = ImageDraw.Draw(card)
        try:
            title_font = ImageFont.truetype("arial.ttf", 24)
            stat_font = ImageFont.truetype("arial.ttf", 16)
        except:
            title_font = ImageFont.load_default()
            stat_font = ImageFont.load_default()
        
        # Draw title
        draw.text((20, 15), title, fill=(0, 0, 0), font=title_font)
        
        # Draw stats
        y_offset = image.height + 70
        for key, value in stats.items():
            text = f"{key}: {value}"
            draw.text((20, y_offset), text, fill=(50, 50, 50), font=stat_font)
            y_offset += 30
        
        return card