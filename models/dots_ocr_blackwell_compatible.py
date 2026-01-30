#!/usr/bin/env python3
"""
dots.ocr модель, оптимизированная для RTX 5070 Ti Blackwell
Без flash-attn, с eager attention и bfloat16 оптимизациями
"""

import torch
import time
from transformers import AutoModelForCausalLM, AutoProcessor
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class DotsOCRBlackwellModel:
    def __init__(self):
        self.model = None
        self.processor = None
        self.model_name = "rednote-hilab/dots.ocr"
        
    def load_model(self):
        """Загрузка модели с Blackwell оптимизациями"""
        try:
            start_time = time.time()
            
            # Применяем Blackwell оптимизации
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.enable_flash_sdp(True)
            
            logger.info("🚀 Загружаем dots.ocr с Blackwell оптимизациями...")
            
            # Загрузка модели с правильными параметрами для Blackwell
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,  # Оптимально для Blackwell
                attn_implementation="eager",  # Обязательно для RTX 5070 Ti
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Загрузка процессора
            self.processor = AutoProcessor.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            load_time = time.time() - start_time
            
            # Информация о модели
            vram_used = torch.cuda.memory_allocated() / 1024**3
            
            logger.info(f"✅ dots.ocr загружена за {load_time:.2f}s")
            logger.info(f"✅ Dtype: {self.model.dtype}")
            logger.info(f"✅ Device: {self.model.device}")
            logger.info(f"✅ VRAM: {vram_used:.2f}GB")
            logger.info(f"✅ Attention: eager (Blackwell compatible)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки dots.ocr: {e}")
            return False
    
    def process_image(self, image, prompt="Extract all text from this image"):
        """Обработка изображения с оптимизированными параметрами"""
        if not self.model or not self.processor:
            logger.error("❌ Модель не загружена")
            return None
            
        try:
            start_time = time.time()
            
            # Подготовка входных данных
            if isinstance(image, str):
                image = Image.open(image).convert('RGB')
            elif not isinstance(image, Image.Image):
                logger.error("❌ Неподдерживаемый формат изображения")
                return None
            
            # Создание conversation в правильном формате
            conversation = [
                {
                    "role": "user", 
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Применение chat template
            text_prompt = self.processor.apply_chat_template(
                conversation, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # Обработка входных данных
            inputs = self.processor(
                text=[text_prompt],
                images=[image],
                padding=True,
                return_tensors="pt"
            ).to("cuda")
            
            # Генерация с оптимизированными параметрами для Blackwell
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    do_sample=False,
                    temperature=0.0,
                    use_cache=True,
                    pad_token_id=self.processor.tokenizer.eos_token_id,
                    # Дополнительные параметры для стабильности
                    repetition_penalty=1.1,
                    length_penalty=1.0
                )
            
            # Декодирование результата
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )[0]
            
            processing_time = time.time() - start_time
            
            logger.info(f"⏱️ Обработка завершена за {processing_time:.3f}s")
            logger.info(f"📝 Длина результата: {len(output_text)} символов")
            
            return output_text.strip()
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки изображения: {e}")
            return None
    
    def cleanup(self):
        """Очистка памяти"""
        if self.model:
            del self.model
        if self.processor:
            del self.processor
        torch.cuda.empty_cache()
        logger.info("🧹 Память очищена")

def test_dots_ocr_blackwell():
    """Тест dots.ocr с Blackwell оптимизациями"""
    print("🧪 ТЕСТ DOTS.OCR BLACKWELL COMPATIBLE")
    print("=" * 60)
    
    # Информация о системе
    print(f"🖥️ GPU: {torch.cuda.get_device_name(0)}")
    print(f"🔧 Compute Capability: {torch.cuda.get_device_capability(0)}")
    print(f"🐍 PyTorch: {torch.__version__}")
    print(f"⚡ CUDA: {torch.version.cuda}")
    print(f"✅ bfloat16: {torch.cuda.is_bf16_supported()}")
    print()
    
    # Создание и загрузка модели
    model = DotsOCRBlackwellModel()
    
    if not model.load_model():
        print("❌ Не удалось загрузить модель")
        return False
    
    # Создание тестового изображения
    print("🔍 Создание тестового изображения...")
    test_image = Image.new('RGB', (800, 600), color='white')
    
    # Тест обработки
    print("🔍 Тестируем обработку изображения...")
    result = model.process_image(
        test_image, 
        "Extract all text from this image in Russian"
    )
    
    if result:
        print(f"✅ Результат получен: {result[:100]}...")
        print("🎉 DOTS.OCR РАБОТАЕТ С BLACKWELL!")
        success = True
    else:
        print("❌ Не удалось получить результат")
        success = False
    
    # Очистка
    model.cleanup()
    
    return success

if __name__ == "__main__":
    success = test_dots_ocr_blackwell()
    if success:
        print("\n🚀 DOTS.OCR ГОТОВА К ИСПОЛЬЗОВАНИЮ НА RTX 5070 TI!")
    else:
        print("\n❌ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ НАСТРОЙКА")