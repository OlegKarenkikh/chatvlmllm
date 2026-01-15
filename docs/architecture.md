# Architecture Documentation

## System Overview

ChatVLMLLM is designed as a modular, extensible system for document OCR and vision-language interaction. The architecture follows clean separation of concerns with distinct layers for model management, processing, and presentation.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐│
│  │ OCR Page   │  │ Chat Page  │  │  Model Comparison     ││
│  └────────────┘  └────────────┘  └────────────────────────┘│
│                   Streamlit Components                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Logic Layer                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Model Loader & Manager                      ││
│  │  - Model caching                                         ││
│  │  - Configuration management                              ││
│  │  - Resource optimization                                 ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Processing Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Image        │  │ Text         │  │ Field Parser     │  │
│  │ Processor    │  │ Extractor    │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Model Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ GOT-OCR 2.0  │  │ Qwen2-VL 2B  │  │ Qwen2-VL 7B      │  │
│  │              │  │              │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                   Base VLM Model                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

**Responsibility**: User interaction and result presentation

**Components**:
- `app.py`: Main Streamlit application
- `ui/styles.py`: Custom CSS styling
- Page components (OCR, Chat, Comparison)

**Key Features**:
- Modern, responsive design
- Real-time feedback
- Multiple view modes
- Export capabilities

### 2. Application Logic Layer

**Responsibility**: Business logic and workflow orchestration

**Components**:
- `models/model_loader.py`: Model factory and caching
- Configuration management
- Request routing
- Resource management

**Key Features**:
- Model lifecycle management
- Configuration-driven behavior
- Memory optimization
- Error handling

### 3. Processing Layer

**Responsibility**: Data preprocessing and post-processing

**Components**:
- `utils/image_processor.py`: Image preprocessing
- `utils/text_extractor.py`: Text extraction and cleaning
- `utils/field_parser.py`: Structured data extraction
- `utils/markdown_renderer.py`: Output formatting

**Key Features**:
- Image enhancement
- Text normalization
- Pattern matching
- Format conversion

### 4. Model Layer

**Responsibility**: ML model integration and inference

**Components**:
- `models/base_model.py`: Abstract base class
- `models/got_ocr.py`: GOT-OCR implementation
- `models/qwen_vl.py`: Qwen2-VL implementation

**Key Features**:
- Unified interface
- Device management
- Precision control
- Inference optimization

## Data Flow

### OCR Workflow

```
1. User uploads image
   │
   ▼
2. Image preprocessing
   │ - Resize
   │ - Enhance
   │ - Denoise (optional)
   │ - Deskew (optional)
   │
   ▼
3. Model selection and loading
   │
   ▼
4. OCR inference
   │ - Image encoding
   │ - Model forward pass
   │ - Text generation
   │
   ▼
5. Post-processing
   │ - Text cleaning
   │ - Field extraction
   │ - Formatting
   │
   ▼
6. Result display
   │ - Text output
   │ - Extracted fields
   │ - Export options
```

### Chat Workflow

```
1. User uploads image + enters message
   │
   ▼
2. Image preprocessing
   │
   ▼
3. Conversation history management
   │ - Load previous context
   │ - Append new message
   │
   ▼
4. Model inference
   │ - Multimodal input encoding
   │ - Response generation
   │
   ▼
5. Response formatting
   │ - Markdown rendering
   │ - Code highlighting
   │
   ▼
6. Display and history update
```

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|----------|
| Language | Python | 3.10+ | Core development |
| ML Framework | PyTorch | 2.1+ | Model inference |
| Transformers | HuggingFace | 4.36+ | Model loading |
| UI Framework | Streamlit | 1.30+ | Web interface |
| Image Processing | Pillow + OpenCV | Latest | Preprocessing |

### Key Libraries

- **transformers**: Model loading and inference
- **accelerate**: Multi-GPU support and optimization
- **flash-attn**: Attention optimization
- **bitsandbytes**: Quantization
- **streamlit**: Web UI
- **pyyaml**: Configuration
- **pandas**: Data handling

## Design Patterns

### 1. Factory Pattern
**Location**: `models/model_loader.py`
**Purpose**: Create model instances based on configuration

### 2. Strategy Pattern
**Location**: `models/base_model.py`
**Purpose**: Different model implementations with unified interface

### 3. Singleton Pattern
**Location**: Model caching in `ModelLoader`
**Purpose**: Reuse loaded models to save memory

### 4. Template Method
**Location**: `models/base_model.py`
**Purpose**: Define common model workflow with customizable steps

## Configuration Management

Configuration is managed through `config.yaml`:

```yaml
models:
  model_name:
    name: "Display Name"
    model_id: "HuggingFace ID"
    precision: "fp16"
    device_map: "auto"
    max_length: 2048
    description: "Model description"
```

**Benefits**:
- Easy model addition
- Environment-specific settings
- No code changes needed
- Version control friendly

## Scalability Considerations

### Horizontal Scaling
- Stateless design allows multiple instances
- Load balancer friendly
- Shared model storage

### Vertical Scaling
- GPU utilization optimization
- Memory management
- Batch processing support

### Future Enhancements
- Model serving with FastAPI
- Async processing queue
- Result caching
- API rate limiting

## Security Considerations

1. **Input Validation**
   - File type checking
   - Size limits
   - Image format validation

2. **Resource Limits**
   - Memory caps
   - Processing timeouts
   - Rate limiting

3. **Data Privacy**
   - No persistent storage of uploads
   - Session isolation
   - Secure model access

## Testing Strategy

### Unit Tests
- Model loading
- Image processing functions
- Text extraction utilities
- Field parsers

### Integration Tests
- End-to-end OCR workflow
- Chat interactions
- Model switching

### Performance Tests
- Inference speed
- Memory usage
- Concurrent requests

## Deployment

### Local Development
```bash
streamlit run app.py
```

### Docker Deployment
```bash
docker build -t chatvlmllm .
docker run -p 8501:8501 chatvlmllm
```

### Production Considerations
- Use process manager (systemd, supervisord)
- Configure reverse proxy (nginx)
- Enable HTTPS
- Set up monitoring
- Configure logging

## Monitoring and Logging

### Metrics to Track
- Request count
- Average response time
- Error rate
- Memory usage
- GPU utilization

### Logging Strategy
- Application logs: INFO level
- Error logs: ERROR level with stack traces
- Performance logs: DEBUG level
- User actions: audit log

## Future Architecture Plans

1. **Microservices Split**
   - Model service
   - Processing service
   - API gateway

2. **Async Processing**
   - Job queue (Celery/RQ)
   - Background workers
   - Status tracking

3. **Caching Layer**
   - Redis for results
   - Model output caching
   - Session management

4. **API Layer**
   - RESTful API
   - WebSocket support
   - API documentation