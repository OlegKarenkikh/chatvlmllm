# Model Documentation

## Overview

This project integrates multiple Vision Language Models (VLM) for document OCR and analysis tasks.

## Supported Models

### 1. GOT-OCR 2.0

**Repository:** [stepfun-ai/GOT-OCR2_0](https://huggingface.co/stepfun-ai/GOT-OCR2_0)

**Description:**
GOT-OCR 2.0 is a specialized optical character recognition model designed for complex document layouts. It excels at recognizing text in various formats including tables, mathematical formulas, and multi-column documents.

**Architecture:**
- Vision Encoder: Enhanced vision transformer
- Text Decoder: Autoregressive language model
- Parameters: ~580M
- Precision: FP16/FP32

**Capabilities:**
- Plain text OCR
- Formatted text with layout preservation
- Table structure recognition
- Mathematical formula OCR
- Multi-language support (100+ languages)
- Handwriting recognition

**Usage Modes:**
```python
# Plain OCR
result = model.process_image(image, prompt="ocr")

# Formatted OCR (preserves layout)
result = model.process_image(image, prompt="format")

# Table extraction
result = model.process_image(image, prompt="table")
```

**Performance:**
- Accuracy: High (95%+ on clear documents)
- Speed: ~2-3 seconds per page on GPU
- Memory: ~3GB VRAM

**Best For:**
- Scientific papers with formulas
- Financial documents with tables
- Forms with complex layouts
- Multi-language documents

---

### 2. Qwen2-VL

**Repository:** [Qwen/Qwen2-VL](https://huggingface.co/Qwen)

**Description:**
Qwen2-VL is a multimodal large language model from Alibaba Cloud that understands both images and text. It can engage in conversations about visual content, answer questions about images, and extract information with contextual understanding.

**Variants:**

#### Qwen2-VL-2B-Instruct
- Parameters: 2 billion
- VRAM: ~5GB
- Speed: Fast inference
- Best for: Quick analysis, resource-constrained environments

#### Qwen2-VL-7B-Instruct
- Parameters: 7 billion
- VRAM: ~14GB
- Speed: Moderate inference
- Best for: Complex understanding, detailed analysis

**Architecture:**
- Vision Encoder: ViT-based image encoder
- Language Model: Qwen2 transformer
- Multimodal Fusion: Cross-attention mechanisms
- Context Length: 4K-8K tokens

**Capabilities:**
- Visual question answering
- Document understanding
- OCR with context
- Multi-turn conversations about images
- Reasoning about visual content
- Structured data extraction

**Usage Examples:**
```python
# Simple OCR
result = model.process_image(image, "Extract all text from this document")

# Question answering
result = model.process_image(image, "What is the invoice total?")

# Interactive chat
response = model.chat(image, "Tell me about this document", history)
```

**Performance:**
- Accuracy: Very high with contextual understanding
- Speed: 3-5 seconds per query (2B), 5-8 seconds (7B)
- Memory: 5GB (2B), 14GB (7B) VRAM

**Best For:**
- Interactive document analysis
- Question-answering on documents
- Context-aware information extraction
- Multi-turn conversations

---

## Model Comparison

| Feature | GOT-OCR 2.0 | Qwen2-VL-2B | Qwen2-VL-7B |
|---------|-------------|-------------|-------------|
| **Primary Use** | OCR | Multimodal Chat | Advanced Analysis |
| **Parameters** | 580M | 2B | 7B |
| **VRAM Required** | 3GB | 5GB | 14GB |
| **Speed** | Fast | Fast | Moderate |
| **Layout Understanding** | Excellent | Good | Excellent |
| **Conversational** | No | Yes | Yes |
| **Reasoning** | Limited | Good | Excellent |
| **Languages** | 100+ | Multilingual | Multilingual |

## Choosing the Right Model

### Use GOT-OCR 2.0 when:
- You need fast, accurate OCR
- Working with complex layouts (tables, formulas)
- Processing scientific or technical documents
- Resource efficiency is important
- No conversational features needed

### Use Qwen2-VL-2B when:
- You need conversational capabilities
- Want to ask questions about documents
- Working with limited GPU resources
- Need fast responses with good understanding

### Use Qwen2-VL-7B when:
- Complex reasoning is required
- Working with ambiguous or challenging documents
- Need the highest accuracy
- Have sufficient GPU resources
- Performing detailed document analysis

## Integration Examples

### Loading Models

```python
from models import ModelLoader

# Load GOT-OCR
got_model = ModelLoader.load_model("got_ocr")

# Load Qwen2-VL 2B
qwen_2b = ModelLoader.load_model("qwen_vl_2b")

# Load Qwen2-VL 7B
qwen_7b = ModelLoader.load_model("qwen_vl_7b")
```

### Processing Documents

```python
from PIL import Image

# Load image
image = Image.open("document.jpg")

# GOT-OCR for fast extraction
text = got_model.process_image(image)

# Qwen2-VL for intelligent extraction
fields = qwen_2b.process_image(
    image,
    "Extract the invoice number, date, and total amount as JSON"
)
```

### Interactive Analysis

```python
# Start conversation
response1 = qwen_7b.chat(image, "What type of document is this?")
print(response1)

# Continue conversation
history = [{"role": "assistant", "content": response1}]
response2 = qwen_7b.chat(
    image,
    "What is the total amount?",
    history=history
)
print(response2)
```

## Optimization Tips

### Memory Optimization

```python
# Use 8-bit quantization for lower memory usage
config = {
    "precision": "int8",
    "device_map": "auto"
}

# Unload models when not in use
ModelLoader.unload_model("qwen_vl_7b")
```

### Speed Optimization

```python
# Enable Flash Attention 2 (CUDA only)
config = {
    "attn_implementation": "flash_attention_2"
}

# Batch processing
images = [img1, img2, img3]
results = [model.process_image(img) for img in images]
```

## Troubleshooting

### Out of Memory
- Reduce batch size
- Use smaller model variant
- Enable int8 quantization
- Resize images before processing

### Slow Inference
- Ensure GPU is being used
- Enable Flash Attention
- Close other GPU-intensive applications
- Consider using smaller model

### Poor Accuracy
- Preprocess images (enhance, denoise)
- Try different prompts
- Use larger model variant
- Ensure image quality is sufficient

## References

- [GOT-OCR 2.0 Paper](https://arxiv.org/abs/2409.01704)
- [Qwen2-VL Technical Report](https://arxiv.org/abs/2409.12191)
- [Transformers Documentation](https://huggingface.co/docs/transformers)
