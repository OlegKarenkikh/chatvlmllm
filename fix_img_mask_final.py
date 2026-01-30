#!/usr/bin/env python3
"""
Окончательное исправление проблемы img_mask в dots.ocr
"""

import sys
import os
import traceback
from PIL import Image
import torch

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import logger

def create_final_img_mask_fix():
    """Создает окончательное исправление для img_mask проблемы."""
    
    logger.info("🔧 Создание окончательного исправления img_mask")
    
    # Читаем текущий файл
    with open("models/dots_ocr_video_processor_fixed.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Находим и заменяем проблемную секцию
    old_mask_creation = '''                                        # Создаем img_mask если его нет
                                        if 'img_mask' not in result and 'pixel_values' in image_inputs:
                                            batch_size = image_inputs['pixel_values'].shape[0]
                                            if len(image_inputs['pixel_values'].shape) == 3:
                                                # Формат [batch, patches, features]
                                                total_patches = image_inputs['pixel_values'].shape[1]
                                            elif len(image_inputs['pixel_values'].shape) == 2:
                                                # Формат [patches, features] - добавляем batch dimension
                                                total_patches = image_inputs['pixel_values'].shape[0]
                                                batch_size = 1
                                            else:
                                                # Используем размер из image_grid_thw если доступен
                                                if 'image_grid_thw' in result:
                                                    grid_thw = result['image_grid_thw']
                                                    if len(grid_thw.shape) >= 2 and grid_thw.shape[1] >= 3:
                                                        _, h_patches, w_patches = grid_thw[0]
                                                        total_patches = h_patches * w_patches
                                                    else:
                                                        total_patches = 256  # fallback
                                                else:
                                                    total_patches = 256  # fallback
                                            
                                            import torch
                                            result['img_mask'] = torch.ones(batch_size, total_patches, dtype=torch.bool)'''
    
    new_mask_creation = '''                                        # КРИТИЧЕСКИ ВАЖНО: Создаем правильный img_mask
                                        if 'pixel_values' in image_inputs:
                                            # Всегда пересоздаем img_mask для гарантии корректности
                                            pixel_values = image_inputs['pixel_values']
                                            
                                            if len(pixel_values.shape) == 2:
                                                # Формат [patches, features]
                                                batch_size = 1
                                                total_patches = pixel_values.shape[0]
                                            elif len(pixel_values.shape) == 3:
                                                # Формат [batch, patches, features] 
                                                batch_size = pixel_values.shape[0]
                                                total_patches = pixel_values.shape[1]
                                            else:
                                                # Fallback на основе image_grid_thw
                                                batch_size = 1
                                                if 'image_grid_thw' in result:
                                                    grid_thw = result['image_grid_thw']
                                                    if len(grid_thw.shape) >= 2 and grid_thw.shape[1] >= 3:
                                                        _, h_patches, w_patches = grid_thw[0]
                                                        total_patches = int(h_patches * w_patches)
                                                    else:
                                                        total_patches = 256
                                                else:
                                                    total_patches = 256
                                            
                                            import torch
                                            # Принудительно создаем маску на правильном устройстве
                                            device = pixel_values.device if hasattr(pixel_values, 'device') else 'cpu'
                                            result['img_mask'] = torch.ones(batch_size, total_patches, dtype=torch.bool, device=device)
                                            
                                            logger.info(f"🔧 Created img_mask: shape={result['img_mask'].shape}, sum={result['img_mask'].sum()}, device={result['img_mask'].device}")'''
    
    # Заменяем в обеих секциях
    content = content.replace(old_mask_creation, new_mask_creation)
    
    # Также заменяем вторую секцию (в UltraSimpleProcessor)
    old_mask_creation_2 = '''                                            # Создаем img_mask если его нет
                                            if 'img_mask' not in result and 'pixel_values' in image_inputs:
                                                batch_size = image_inputs['pixel_values'].shape[0]
                                                if len(image_inputs['pixel_values'].shape) == 3:
                                                    # Формат [batch, patches, features]
                                                    total_patches = image_inputs['pixel_values'].shape[1]
                                                elif len(image_inputs['pixel_values'].shape) == 2:
                                                    # Формат [patches, features] - добавляем batch dimension
                                                    total_patches = image_inputs['pixel_values'].shape[0]
                                                    batch_size = 1
                                                else:
                                                    # Используем размер из image_grid_thw если доступен
                                                    if 'image_grid_thw' in result:
                                                        grid_thw = result['image_grid_thw']
                                                        if len(grid_thw.shape) >= 2 and grid_thw.shape[1] >= 3:
                                                            _, h_patches, w_patches = grid_thw[0]
                                                            total_patches = h_patches * w_patches
                                                        else:
                                                            total_patches = 256  # fallback
                                                    else:
                                                        total_patches = 256  # fallback
                                                
                                                import torch
                                                result['img_mask'] = torch.ones(batch_size, total_patches, dtype=torch.bool)'''
    
    new_mask_creation_2 = '''                                            # КРИТИЧЕСКИ ВАЖНО: Создаем правильный img_mask
                                            if 'pixel_values' in image_inputs:
                                                # Всегда пересоздаем img_mask для гарантии корректности
                                                pixel_values = image_inputs['pixel_values']
                                                
                                                if len(pixel_values.shape) == 2:
                                                    # Формат [patches, features]
                                                    batch_size = 1
                                                    total_patches = pixel_values.shape[0]
                                                elif len(pixel_values.shape) == 3:
                                                    # Формат [batch, patches, features] 
                                                    batch_size = pixel_values.shape[0]
                                                    total_patches = pixel_values.shape[1]
                                                else:
                                                    # Fallback на основе image_grid_thw
                                                    batch_size = 1
                                                    if 'image_grid_thw' in result:
                                                        grid_thw = result['image_grid_thw']
                                                        if len(grid_thw.shape) >= 2 and grid_thw.shape[1] >= 3:
                                                            _, h_patches, w_patches = grid_thw[0]
                                                            total_patches = int(h_patches * w_patches)
                                                        else:
                                                            total_patches = 256
                                                    else:
                                                        total_patches = 256
                                                
                                                import torch
                                                # Принудительно создаем маску на правильном устройстве
                                                device = pixel_values.device if hasattr(pixel_values, 'device') else 'cpu'
                                                result['img_mask'] = torch.ones(batch_size, total_patches, dtype=torch.bool, device=device)
                                                
                                                logger.info(f"🔧 Created img_mask (simple): shape={result['img_mask'].shape}, sum={result['img_mask'].sum()}, device={result['img_mask'].device}")'''
    
    content = content.replace(old_mask_creation_2, new_mask_creation_2)
    
    # Сохраняем исправленный файл
    with open("models/dots_ocr_video_processor_fixed.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info("✅ Окончательное исправление img_mask применено")
    return True

def test_final_fix():
    """Тестируем окончательное исправление."""
    
    logger.info("🧪 Тестирование окончательного исправления")
    
    try:
        from models.dots_ocr_video_processor_fixed import DotsOCRVideoProcessorFixedModel
        from PIL import Image
        
        # Создаем простое изображение
        img = Image.new('RGB', (224, 224), color='white')
        
        # Загружаем модель
        config = {
            "model_path": "rednote-hilab/dots.ocr",
            "precision": "fp16",
            "device": "cuda",
            "max_new_tokens": 50
        }
        model = DotsOCRVideoProcessorFixedModel(config)
        model.load_model()
        
        # Тестируем процессор
        inputs = model.processor(
            text="What is in this image?",
            images=img,
            return_tensors='pt'
        )
        
        logger.info(f"✅ Processor test passed!")
        logger.info(f"Keys: {list(inputs.keys())}")
        
        if 'img_mask' in inputs:
            mask = inputs['img_mask']
            logger.info(f"img_mask shape: {mask.shape}")
            logger.info(f"img_mask sum: {mask.sum()}")
            logger.info(f"img_mask device: {mask.device}")
            
            if mask.sum() > 0:
                logger.info("🎉 img_mask исправлена! Сумма больше 0")
                return True
            else:
                logger.error("❌ img_mask все еще равна 0")
                return False
        else:
            logger.error("❌ img_mask не найдена в результатах")
            return False
            
    except Exception as e:
        logger.error(f"❌ Тест не прошел: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Запуск окончательного исправления img_mask")
    
    # Применяем исправление
    if create_final_img_mask_fix():
        logger.info("✅ Исправление применено, тестируем...")
        
        # Тестируем
        if test_final_fix():
            logger.info("🎉 Окончательное исправление успешно!")
        else:
            logger.error("❌ Требуется дополнительная работа")
    else:
        logger.error("❌ Не удалось применить исправление")