import streamlit as st
import yaml
from pathlib import Path
from PIL import Image
import io

# Import UI components
from ui.styles import get_custom_css

# Page configuration
st.set_page_config(
    page_title="ChatVLMLLM - Document OCR & VLM Chat",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Load configuration
@st.cache_resource
def load_config():
    """Load configuration from YAML file."""
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None
if "loaded_model" not in st.session_state:
    st.session_state.loaded_model = None

# Header
st.markdown('<h1 class="gradient-text" style="text-align: center;">🔬 ChatVLMLLM</h1>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align: center; font-size: 1.2rem; color: #888; margin-bottom: 2rem;">'
    'Vision Language Models for Document OCR & Intelligent Chat</p>', 
    unsafe_allow_html=True
)

# Sidebar navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", width=80)
    st.title("Navigation")
    
    page = st.radio(
        "Select Mode",
        ["🏠 Home", "📄 OCR Mode", "💬 Chat Mode", "📊 Model Comparison", "📚 Documentation"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.subheader("⚙️ Model Settings")
    selected_model = st.selectbox(
        "Select Model",
        list(config["models"].keys()),
        format_func=lambda x: config["models"][x]["name"],
        key="model_selector"
    )
    
    # Display model info
    model_info = config["models"][selected_model]
    st.info(
        f"**{model_info['name']}**\n\n"
        f"{model_info['description']}\n\n"
        f"📊 Max tokens: {model_info['max_length']}"
    )
    
    st.divider()
    
    with st.expander("🔧 Advanced Settings"):
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, help="Controls randomness in generation")
        max_tokens = st.number_input("Max Tokens", 100, 4096, 2048, 100, help="Maximum length of generated text")
        use_gpu = st.checkbox("Use GPU", value=True, help="Enable GPU acceleration if available")
    
    st.divider()
    
    # Project stats
    st.markdown("### 📊 Project Stats")
    col1, col2 = st.columns(2)
    col1.metric("Models", "3")
    col2.metric("Status", "✅ Ready")
    
    # Model loading status
    if st.session_state.loaded_model:
        st.success(f"✅ Loaded: {st.session_state.loaded_model}")
    else:
        st.warning("⚠️ No model loaded")

# Main content area
if "🏠 Home" in page:
    st.header("Welcome to ChatVLMLLM Research Project")
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            '<div class="feature-card">'
            '<h3>📄 OCR Mode</h3>'
            '<p>Extract text and structured data from documents using specialized VLM models.</p>'
            '<ul style="text-align: left; margin-top: 1rem;">'
            '<li>✅ Text recognition</li>'
            '<li>✅ Field extraction</li>'
            '<li>✅ Multi-format support</li>'
            '<li>✅ Export to JSON/CSV</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            '<div class="feature-card">'
            '<h3>💬 Chat Mode</h3>'
            '<p>Interactive conversation with VLM models about document content.</p>'
            '<ul style="text-align: left; margin-top: 1rem;">'
            '<li>✅ Visual Q&A</li>'
            '<li>✅ Context understanding</li>'
            '<li>✅ Markdown support</li>'
            '<li>✅ Chat history</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            '<div class="feature-card">'
            '<h3>📊 Comparison</h3>'
            '<p>Compare different models\' performance on various document types.</p>'
            '<ul style="text-align: left; margin-top: 1rem;">'
            '<li>✅ Accuracy metrics</li>'
            '<li>✅ Speed benchmarks</li>'
            '<li>✅ Memory usage</li>'
            '<li>✅ Quality analysis</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True
        )
    
    st.divider()
    
    # Research goals in tabs
    st.header("🎯 Research Goals & Timeline")
    
    tabs = st.tabs(["📋 Overview", "📅 Timeline", "🎓 Learning", "📈 Results"])
    
    with tabs[0]:
        st.markdown("""
        This educational project explores modern **Vision Language Models** for document OCR tasks.
        We investigate different architectures, compare their performance, and develop practical
        applications for real-world document processing.
        
        ### Key Research Questions
        
        1. 🔍 **Model Comparison**: How do specialized OCR models compare to general VLM models?
        2. ⚖️ **Trade-offs**: What are the performance vs. accuracy trade-offs?
        3. 📊 **Structured Extraction**: Can VLMs reliably extract structured data?
        4. 🧠 **Context Understanding**: How does context improve OCR results?
        
        ### Methodology
        
        - **Quantitative Analysis**: CER, WER, field accuracy metrics
        - **Qualitative Assessment**: Layout preservation, structure understanding
        - **Performance Benchmarking**: Speed, memory, scalability
        - **Comparative Studies**: Model-to-model comparisons
        """)
    
    with tabs[1]:
        progress_data = [
            ("Phase 1: Preparation", 100, "✅ Complete"),
            ("Phase 2: Model Integration", 60, "🔄 In Progress"),
            ("Phase 3: UI Development", 40, "🔄 In Progress"),
            ("Phase 4: Testing", 0, "⏳ Pending"),
            ("Phase 5: Documentation", 20, "🔄 In Progress"),
        ]
        
        for phase, progress, status in progress_data:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{phase}**")
                st.progress(progress / 100)
            with col2:
                st.markdown(f"<p style='text-align: right;'>{status}</p>", unsafe_allow_html=True)
    
    with tabs[2]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 💻 Technical Skills
            
            - VLM model deployment & optimization
            - Image preprocessing pipelines
            - Inference optimization (Flash Attention, quantization)
            - Full-stack development with Streamlit
            - Docker containerization & deployment
            - Testing & quality assurance
            - Git version control & collaboration
            """)
        
        with col2:
            st.markdown("""
            ### 🔬 Research Skills
            
            - Model architecture analysis
            - Comparative evaluation methodology
            - Statistical analysis & metrics
            - Scientific documentation
            - Critical thinking & problem-solving
            - Data visualization & presentation
            - Technical writing & reporting
            """)
    
    with tabs[3]:
        st.info("📊 Results will be updated as experiments are conducted")
        
        st.markdown("""
        ### Expected Outcomes
        
        - 📄 Comprehensive comparison report
        - 📊 Performance benchmarks across models
        - 📚 Best practices guide for VLM OCR
        - 💻 Open-source implementation
        - 🎓 Educational materials & tutorials
        """)

elif "📄 OCR Mode" in page:
    st.header("📄 Document OCR Mode")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Document")
        
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=config["ocr"]["supported_formats"],
            help="Supported formats: JPG, PNG, BMP, TIFF",
            key="ocr_upload"
        )
        
        if uploaded_file:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.session_state.uploaded_image = image
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Image info
            st.caption(f"📐 Size: {image.size[0]}x{image.size[1]} | Format: {image.format}")
        
        st.divider()
        
        # Document type selection
        document_type = st.selectbox(
            "📋 Document Type",
            list(config["document_templates"].keys()),
            format_func=lambda x: x.capitalize(),
            help="Select the type of document for optimized field extraction"
        )
        
        # Processing options
        with st.expander("⚙️ Processing Options"):
            enhance_image = st.checkbox("Enhance image quality", value=True)
            denoise = st.checkbox("Apply denoising", value=False)
            deskew = st.checkbox("Auto-deskew", value=False)
        
        st.divider()
        
        # Process button
        if st.button("🚀 Extract Text", type="primary", use_container_width=True):
            if uploaded_file:
                with st.spinner("🔄 Processing document..."):
                    # Placeholder for actual model integration
                    import time
                    time.sleep(1.5)
                    
                    # Demo output
                    st.session_state.ocr_result = {
                        "text": "Sample extracted text will appear here after model integration.\n\nThis is a placeholder demonstrating the UI flow.",
                        "confidence": 0.92,
                        "processing_time": 1.5
                    }
                    
                    st.success("✅ Text extracted successfully!")
                    st.rerun()
            else:
                st.error("❌ Please upload an image first")
    
    with col2:
        st.subheader("📊 Extraction Results")
        
        if st.session_state.ocr_result:
            result = st.session_state.ocr_result
            
            # Metrics
            metric_col1, metric_col2 = st.columns(2)
            metric_col1.metric("Confidence", f"{result['confidence']:.1%}")
            metric_col2.metric("Processing Time", f"{result['processing_time']:.2f}s")
            
            st.divider()
            
            # Extracted text
            st.markdown("**🔤 Recognized Text:**")
            st.code(result["text"], language="text")
            
            st.divider()
            
            # Extracted fields
            st.markdown("**📋 Extracted Fields:**")
            
            if document_type:
                fields = config["document_templates"][document_type]["fields"]
                for field in fields:
                    st.text_input(
                        field,
                        placeholder=f"{field} will be extracted here",
                        disabled=True,
                        key=f"field_{field}"
                    )
            
            st.divider()
            
            # Export options
            st.markdown("**💾 Export Options:**")
            col_json, col_csv = st.columns(2)
            with col_json:
                st.download_button(
                    "📄 Export JSON",
                    data="{}",
                    file_name="ocr_result.json",
                    mime="application/json",
                    use_container_width=True
                )
            with col_csv:
                st.download_button(
                    "📊 Export CSV",
                    data="",
                    file_name="ocr_result.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("💡 Upload an image and click 'Extract Text' to see results here")

elif "💬 Chat Mode" in page:
    st.header("💬 Interactive VLM Chat")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🖼️ Upload Image")
        
        chat_image = st.file_uploader(
            "Image for chat context",
            type=config["ocr"]["supported_formats"],
            key="chat_upload"
        )
        
        if chat_image:
            image = Image.open(chat_image)
            st.session_state.uploaded_image = image
            st.image(image, caption="Context Image", use_container_width=True)
            
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
    
    with col2:
        st.subheader("💭 Conversation")
        
        # Chat container
        chat_container = st.container(height=400)
        
        with chat_container:
            if not st.session_state.messages:
                st.info("👋 Upload an image and start asking questions about it!")
            
            # Display chat messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about the image...", disabled=not chat_image):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response (placeholder)
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    import time
                    time.sleep(1)
                    
                    response = f"This is a demo response. After model integration, I will analyze the image and answer: '{prompt}'"
                    st.markdown(response)
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

elif "📊 Model Comparison" in page:
    st.header("📊 Model Performance Comparison")
    
    st.info("📈 Comparative analysis will be available after benchmark testing")
    
    # Comparison table
    import pandas as pd
    
    comparison_data = pd.DataFrame({
        "Model": ["GOT-OCR 2.0", "Qwen2-VL 2B", "Qwen2-VL 7B"],
        "Parameters": ["580M", "2B", "7B"],
        "VRAM (GB)": ["3", "5", "14"],
        "CER (%)": ["-", "-", "-"],
        "Speed (s/page)": ["-", "-", "-"],
        "Best For": ["Complex layouts", "General OCR", "Advanced analysis"]
    })
    
    st.dataframe(comparison_data, use_container_width=True, hide_index=True)
    
    st.divider()
    
    st.subheader("📏 Evaluation Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Character Error Rate (CER)**
        
        Measures accuracy at character level:
        
        ```
        CER = (S + D + I) / N
        ```
        
        Where:
        - S = Substitutions
        - D = Deletions
        - I = Insertions
        - N = Total characters
        """)
    
    with col2:
        st.markdown("""
        **Word Error Rate (WER)**
        
        Measures accuracy at word level:
        
        ```
        WER = (S + D + I) / N
        ```
        
        Where:
        - S = Substitutions
        - D = Deletions
        - I = Insertions
        - N = Total words
        """)
    
    with col3:
        st.markdown("""
        **Field Accuracy**
        
        Structured data extraction:
        
        ```
        Accuracy = Correct / Total
        ```
        
        Where:
        - Correct = Correctly extracted fields
        - Total = Total fields
        """)

else:  # Documentation
    st.header("📚 Documentation")
    
    doc_tabs = st.tabs(["🚀 Quick Start", "🤖 Models", "🏗️ Architecture", "📖 API", "🤝 Contributing"])
    
    with doc_tabs[0]:
        st.markdown("""
        ## Quick Start Guide
        
        ### Installation
        
        ```bash
        # Clone repository
        git clone https://github.com/OlegKarenkikh/chatvlmllm.git
        cd chatvlmllm
        
        # Setup (automated)
        bash scripts/setup.sh  # Linux/Mac
        scripts\\setup.bat      # Windows
        
        # Run application
        streamlit run app.py
        ```
        
        ### First Steps
        
        1. ✅ Select a model from the sidebar
        2. 📄 Choose OCR or Chat mode
        3. 📤 Upload your document
        4. 🚀 Get instant results!
        
        ### Model Selection
        
        - **GOT-OCR**: Fast, accurate text extraction
        - **Qwen2-VL 2B**: Lightweight multimodal chat
        - **Qwen2-VL 7B**: Advanced document analysis
        """)
        
        st.info("📖 For detailed instructions, see [QUICKSTART.md](https://github.com/OlegKarenkikh/chatvlmllm/blob/main/QUICKSTART.md)")
    
    with doc_tabs[1]:
        st.markdown("""
        ## Supported Models
        
        ### GOT-OCR 2.0
        
        Specialized OCR model for complex document layouts.
        
        **Strengths:**
        - ✅ High accuracy on structured documents
        - ✅ Table extraction
        - ✅ Mathematical formula recognition
        - ✅ Multi-language support (100+ languages)
        
        **Use Cases:**
        - Scientific papers
        - Financial documents
        - Forms and tables
        
        ### Qwen2-VL
        
        General-purpose vision-language models.
        
        **Strengths:**
        - ✅ Multimodal understanding
        - ✅ Context-aware responses
        - ✅ Interactive chat
        - ✅ Reasoning capabilities
        
        **Use Cases:**
        - Document Q&A
        - Visual analysis
        - Content extraction
        """)
        
        st.info("📖 For detailed documentation, see [docs/models.md](https://github.com/OlegKarenkikh/chatvlmllm/blob/main/docs/models.md)")
    
    with doc_tabs[2]:
        st.markdown("""
        ## System Architecture
        
        ### Layered Design
        
        ```
        UI Layer (Streamlit)
              ↓
        Application Layer
              ↓
        Processing Layer (Utils)
              ↓
        Model Layer (VLM Models)
              ↓
        Foundation (PyTorch/HF)
        ```
        
        ### Key Components
        
        - **Models**: VLM integration and inference
        - **Utils**: Image processing and text extraction
        - **UI**: Streamlit interface and styling
        - **Tests**: Quality assurance
        """)
        
        st.info("📖 For architecture details, see [docs/architecture.md](https://github.com/OlegKarenkikh/chatvlmllm/blob/main/docs/architecture.md)")
    
    with doc_tabs[3]:
        st.markdown("""
        ## API Reference
        
        ### Loading Models
        
        ```python
        from models import ModelLoader
        
        # Load a model
        model = ModelLoader.load_model('got_ocr')
        
        # Process image
        from PIL import Image
        image = Image.open('document.jpg')
        text = model.process_image(image)
        ```
        
        ### Field Extraction
        
        ```python
        from utils.field_parser import FieldParser
        
        # Parse invoice
        fields = FieldParser.parse_invoice(text)
        print(fields['invoice_number'])
        ```
        
        ### Chat Interface
        
        ```python
        # Interactive chat
        model = ModelLoader.load_model('qwen_vl_2b')
        response = model.chat(image, "What's in this document?")
        ```
        """)
    
    with doc_tabs[4]:
        st.markdown("""
        ## Contributing
        
        We welcome contributions! 🎉
        
        ### How to Contribute
        
        1. 🍴 Fork the repository
        2. 🌿 Create a feature branch
        3. ✍️ Make your changes
        4. ✅ Write tests
        5. 📝 Update documentation
        6. 🚀 Submit a pull request
        
        ### Areas for Contribution
        
        - 🐛 Bug fixes
        - ✨ New features
        - 📝 Documentation
        - 🧪 Tests
        - 🎨 UI improvements
        """)
        
        st.info("📖 For contribution guidelines, see [CONTRIBUTING.md](https://github.com/OlegKarenkikh/chatvlmllm/blob/main/CONTRIBUTING.md)")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; padding: 2rem;">
    <p><strong>ChatVLMLLM</strong> - Educational Research Project</p>
    <p>Built with ❤️ using Streamlit | 
    <a href="https://github.com/OlegKarenkikh/chatvlmllm" target="_blank" style="color: #FF4B4B;">GitHub</a> | 
    MIT License</p>
    <p style="font-size: 0.9rem; margin-top: 1rem;">🔬 Exploring Vision Language Models for Document OCR</p>
</div>
""", unsafe_allow_html=True)