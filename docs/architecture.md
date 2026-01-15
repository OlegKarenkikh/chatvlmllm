# Architecture Documentation

## System Overview

ChatVLMLLM is a modular research application for exploring Vision Language Models in document OCR tasks. The architecture follows a layered design pattern with clear separation of concerns.

## Architecture Layers

```
┌─────────────────────────────────────────┐
│         UI Layer (Streamlit)            │
│  - OCR Interface                        │
│  - Chat Interface                       │
│  - Comparison Dashboard                 │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│       Application Layer (app.py)        │
│  - Route handling                       │
│  - State management                     │
│  - User interaction logic               │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│       Processing Layer (utils/)         │
│  - Image preprocessing                  │
│  - Text extraction & cleaning           │
│  - Field parsing                        │
│  - Markdown rendering                   │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│        Model Layer (models/)            │
│  - Model loading & management           │
│  - Inference execution                  │
│  - Post-processing                      │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Foundation (PyTorch, HF)            │
│  - GOT-OCR 2.0                          │
│  - Qwen2-VL                             │
└─────────────────────────────────────────┘
```

## Component Details

### 1. UI Layer

**Technology:** Streamlit with custom CSS

**Components:**
- `app.py`: Main application entry point
- `ui/styles.py`: Custom styling
- `ui/ocr_page.py`: OCR interface
- `ui/chat_page.py`: Chat interface

**Responsibilities:**
- Render user interface
- Handle user inputs
- Display results
- Manage session state

### 2. Application Layer

**Technology:** Python, Streamlit

**Components:**
- Route handling for different pages
- Configuration loading
- State management
- Error handling

**Responsibilities:**
- Coordinate between UI and processing layers
- Manage application flow
- Handle configuration
- Cache management

### 3. Processing Layer

**Technology:** Python, PIL, OpenCV, NumPy

**Components:**

#### ImageProcessor (`utils/image_processor.py`)
- Image preprocessing
- Resizing and normalization
- Enhancement (contrast, sharpness)
- Denoising
- Deskewing
- Border cropping

#### TextExtractor (`utils/text_extractor.py`)
- Text cleaning and normalization
- Entity extraction (dates, emails, phones)
- Pattern matching
- Confidence scoring

#### FieldParser (`utils/field_parser.py`)
- Structured field extraction
- Document-type-specific parsing
- Key-value pair extraction

#### MarkdownRenderer (`utils/markdown_renderer.py`)
- Result formatting
- Table generation
- Highlighting

**Responsibilities:**
- Prepare images for inference
- Clean and structure OCR output
- Extract specific information
- Format results for display

### 4. Model Layer

**Technology:** PyTorch, Transformers

**Components:**

#### BaseVLMModel (`models/base_model.py`)
- Abstract base class
- Common interface
- Shared utilities

#### GOTOCRModel (`models/got_ocr.py`)
- GOT-OCR 2.0 integration
- OCR-specific methods
- Format preservation

#### Qwen2VLModel (`models/qwen_vl.py`)
- Qwen2-VL integration
- Chat capabilities
- Multimodal understanding

#### ModelLoader (`models/model_loader.py`)
- Factory pattern for model creation
- Model lifecycle management
- Configuration handling
- Caching loaded models

**Responsibilities:**
- Load and initialize models
- Execute inference
- Manage GPU memory
- Provide unified API

## Data Flow

### OCR Workflow

```
User Upload
    ↓
Image Validation
    ↓
Preprocessing
  - Resize
  - Enhance
  - Denoise
    ↓
Model Selection
    ↓
Inference
  - GOT-OCR or Qwen2-VL
    ↓
Post-processing
  - Text cleaning
  - Field extraction
    ↓
Result Formatting
  - Markdown rendering
  - Table generation
    ↓
Display to User
    ↓
Export Options
  - JSON
  - CSV
  - Text
```

### Chat Workflow

```
User Upload Image
    ↓
Image Preprocessing
    ↓
User Message
    ↓
Context Building
  - Image context
  - Chat history
    ↓
Model Inference
  - Qwen2-VL
    ↓
Response Generation
    ↓
Markdown Rendering
    ↓
Display with History
    ↓
Continue Conversation
```

## Configuration Management

**File:** `config.yaml`

**Structure:**
```yaml
models:
  model_key:
    name: Display name
    model_id: HuggingFace ID
    precision: fp16/fp32/int8
    device_map: auto/cuda/cpu
    max_length: token limit

app:
  title: Application title
  page_icon: Emoji
  layout: wide/centered

ocr:
  supported_formats: [jpg, png, ...]
  max_image_size: bytes
  resize_max_dimension: pixels

document_templates:
  document_type:
    fields: [field1, field2, ...]
```

## State Management

**Streamlit Session State:**

```python
st.session_state = {
    "loaded_model": None,
    "chat_history": [],
    "uploaded_image": None,
    "ocr_result": None,
    "extracted_fields": {},
}
```

## Error Handling

**Strategy:**
- Try-except blocks at each layer
- User-friendly error messages
- Logging for debugging
- Graceful degradation

**Example:**
```python
try:
    result = model.process_image(image)
except torch.cuda.OutOfMemoryError:
    st.error("GPU out of memory. Try smaller image or model.")
except Exception as e:
    st.error(f"Processing failed: {str(e)}")
    logger.exception("Model inference error")
```

## Performance Optimizations

### Caching

```python
@st.cache_resource
def load_model(model_key):
    return ModelLoader.load_model(model_key)

@st.cache_data
def preprocess_image(image_bytes):
    return ImageProcessor.preprocess(image)
```

### Memory Management

- Lazy model loading
- Explicit GPU memory clearing
- Model unloading when switching
- Batch processing optimization

### Inference Optimization

- Flash Attention 2 (when available)
- Mixed precision (FP16)
- Quantization (INT8)
- Device mapping (auto)

## Security Considerations

### Input Validation

```python
# File size limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Format validation
ALLOWED_FORMATS = ["jpg", "jpeg", "png", "bmp"]

# Sanitize user inputs
def sanitize_prompt(prompt: str) -> str:
    # Remove potentially harmful content
    return prompt.strip()[:500]
```

### Resource Limits

- Maximum image dimensions
- Token generation limits
- Timeout for inference
- Rate limiting (if deployed)

## Testing Strategy

### Unit Tests

```python
# tests/test_models.py
def test_model_loading():
    model = ModelLoader.load_model("got_ocr")
    assert model is not None

# tests/test_utils.py
def test_image_preprocessing():
    image = Image.open("test.jpg")
    processed = ImageProcessor.preprocess(image)
    assert processed.size[0] <= 2048
```

### Integration Tests

- End-to-end OCR workflow
- Chat conversation flow
- Model switching

## Deployment Considerations

### Docker

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Run
CMD ["streamlit", "run", "app.py"]
```

### Resource Requirements

**Minimum:**
- 8GB RAM
- 4GB VRAM (for small models)
- 2 CPU cores

**Recommended:**
- 16GB RAM
- 16GB VRAM (for large models)
- 4+ CPU cores
- SSD storage

## Future Enhancements

### Planned Features

1. **Model Quantization**: INT8/INT4 support
2. **Batch Processing**: Multiple documents at once
3. **API Server**: REST API for programmatic access
4. **Results Database**: Store and search past results
5. **Fine-tuning**: Custom model training
6. **Multi-page PDFs**: Full document processing
7. **Cloud Deployment**: AWS/GCP hosting
8. **Authentication**: User accounts and permissions

### Architecture Evolution

- Microservices architecture for scaling
- Message queue for async processing
- Distributed model inference
- CDN for static assets
