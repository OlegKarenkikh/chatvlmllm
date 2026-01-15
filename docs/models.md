# Models Documentation

## Overview

This document provides detailed information about the Vision Language Models (VLMs) used in the ChatVLMLLM project.

## Supported Models

### 1. GOT-OCR 2.0

#### Description
GOT-OCR 2.0 (General OCR Theory) is a specialized OCR model designed for understanding complex document layouts. It excels at extracting text from structured documents like forms, tables, and scientific papers.

#### Key Features
- **High Accuracy**: State-of-the-art OCR performance
- **Complex Layouts**: Handles multi-column documents, tables, and nested structures
- **Mathematical Formulas**: Can recognize LaTeX formulas
- **Multi-language**: Supports various languages
- **Format Preservation**: Maintains document structure

#### Technical Specifications
- **Parameters**: ~580M
- **Architecture**: Transformer-based vision encoder + language decoder
- **Input Resolution**: Up to 2048px
- **Inference Speed**: ~2-3 seconds per page (GPU)
- **Memory Requirements**: 4-6GB VRAM (fp16)

#### Use Cases
- Scientific papers and academic documents
- Financial statements and reports
- Government forms and applications
- Technical documentation
- Tables and structured data extraction

#### Example Usage

```python
from models import ModelLoader
from PIL import Image

# Load model
model = ModelLoader.load("got_ocr")

# Process image
image = Image.open("document.jpg")
text = model.process_image(image)

print(text)
```

### 2. Qwen2-VL

#### Description
Qwen2-VL is a general-purpose Vision Language Model developed by Alibaba Cloud. It combines strong visual understanding with natural language generation capabilities, making it ideal for interactive document analysis.

#### Key Features
- **Multimodal Understanding**: Processes both images and text
- **Interactive Chat**: Conversational interface for document queries
- **Context Awareness**: Understands document context and semantics
- **Reasoning**: Can answer complex questions about document content
- **Multiple Sizes**: Available in 2B and 7B parameter versions

#### Technical Specifications

**Qwen2-VL 2B:**
- **Parameters**: 2 billion
- **Speed**: Fast inference (~1-2 seconds)
- **Memory**: 4-6GB VRAM (fp16)
- **Best For**: Real-time applications, batch processing

**Qwen2-VL 7B:**
- **Parameters**: 7 billion
- **Speed**: Moderate (~3-4 seconds)
- **Memory**: 12-16GB VRAM (fp16)
- **Best For**: Complex analysis, detailed reasoning

#### Use Cases
- Document Q&A systems
- Visual content analysis
- Multi-modal chatbots
- Educational tools
- Content summarization

#### Example Usage

```python
from models import ModelLoader
from PIL import Image

# Load model
model = ModelLoader.load("qwen_vl_2b")

# OCR mode
image = Image.open("document.jpg")
text = model.process_image(image, "Extract all text")

# Chat mode
response = model.chat(
    image=image,
    message="What is the total amount on this invoice?",
    history=[]
)

print(response)
```

## Model Comparison

| Feature | GOT-OCR 2.0 | Qwen2-VL 2B | Qwen2-VL 7B |
|---------|-------------|-------------|-------------|
| **Primary Use** | OCR | Multimodal Chat | Advanced Analysis |
| **Parameters** | 580M | 2B | 7B |
| **OCR Accuracy** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Chat Capability** | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Speed** | Fast | Very Fast | Moderate |
| **Memory (fp16)** | 4-6GB | 4-6GB | 12-16GB |
| **Best For** | Complex layouts | General OCR + Chat | Advanced reasoning |

## Performance Benchmarks

### Character Error Rate (CER)

*Results will be updated after testing phase*

| Document Type | GOT-OCR 2.0 | Qwen2-VL 2B | Qwen2-VL 7B |
|---------------|-------------|-------------|-------------|
| Printed Text | TBD | TBD | TBD |
| Handwritten | TBD | TBD | TBD |
| Tables | TBD | TBD | TBD |
| Forms | TBD | TBD | TBD |

### Processing Speed

*GPU: NVIDIA RTX 4090, Resolution: 1024x1024*

| Model | Average Time | Throughput |
|-------|--------------|------------|
| GOT-OCR 2.0 | TBD | TBD pages/min |
| Qwen2-VL 2B | TBD | TBD pages/min |
| Qwen2-VL 7B | TBD | TBD pages/min |

## Model Selection Guide

### Choose GOT-OCR 2.0 when:
- You need maximum OCR accuracy
- Working with complex document layouts
- Extracting tables and structured data
- Processing scientific or technical documents
- Format preservation is critical

### Choose Qwen2-VL 2B when:
- You need real-time processing
- Want interactive document Q&A
- Limited GPU memory available
- Processing simple to moderate documents
- Need both OCR and understanding

### Choose Qwen2-VL 7B when:
- You need advanced reasoning capabilities
- Working with complex multi-page documents
- Require detailed analysis and insights
- GPU memory is not a constraint
- Need best possible understanding

## Optimization Tips

### Memory Optimization
1. Use `fp16` precision instead of `fp32`
2. Enable 8-bit quantization for larger models
3. Process images in batches
4. Unload models when not in use

### Speed Optimization
1. Use Flash Attention 2 (if available)
2. Optimize image resolution (don't exceed 2048px)
3. Use GPU acceleration
4. Enable model caching
5. Batch similar requests

### Accuracy Optimization
1. Preprocess images (enhance, denoise)
2. Use appropriate prompts
3. Adjust temperature for generation
4. Post-process extracted text
5. Use ensemble methods for critical tasks

## Future Models

Planned additions:
- **DeepSeek-VL**: Open-source VLM with strong performance
- **LLaVA-NeXT**: Advanced multimodal understanding
- **PaddleOCR**: Lightweight OCR solution

## References

- [GOT-OCR 2.0 Paper](https://arxiv.org/abs/2409.01704)
- [Qwen2-VL Documentation](https://github.com/QwenLM/Qwen2-VL)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)