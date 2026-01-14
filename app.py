import streamlit as st
import yaml
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="ChatVLMLLM - Document OCR & VLM Chat",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
@st.cache_resource
def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

# Custom CSS for modern design
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #FF4B4B;
        --secondary-color: #0068C9;
        --background-color: #0E1117;
        --secondary-bg: #262730;
        --text-color: #FAFAFA;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF4B4B 0%, #0068C9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .info-card {
        background: var(--secondary-bg);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid var(--primary-color);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
    }
    
    /* Upload area */
    .uploadedFile {
        border: 2px dashed var(--primary-color);
        border-radius: 10px;
        padding: 2rem;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #262730 0%, #1a1d26 100%);
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: 8px;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🔬 ChatVLMLLM</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #888; margin-bottom: 2rem;">'
            'Vision Language Models for Document OCR & Intelligent Chat</p>', 
            unsafe_allow_html=True)

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
    
    st.subheader("Model Settings")
    selected_model = st.selectbox(
        "Select Model",
        list(config["models"].keys()),
        format_func=lambda x: config["models"][x]["name"]
    )
    
    st.info(f"**{config['models'][selected_model]['name']}**\n\n"
            f"{config['models'][selected_model]['description']}")
    
    st.divider()
    
    with st.expander("⚙️ Advanced Settings"):
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.number_input("Max Tokens", 100, 4096, 2048, 100)
        use_gpu = st.checkbox("Use GPU", value=True)
    
    st.divider()
    st.markdown("### 📊 Project Stats")
    col1, col2 = st.columns(2)
    col1.metric("Models", "3")
    col2.metric("Status", "Beta")

# Main content area
if "🏠 Home" in page:
    st.header("Welcome to ChatVLMLLM Research Project")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📄 OCR Mode")
        st.write("Extract text and structured data from documents using specialized VLM models.")
        st.markdown("**Features:**")
        st.markdown("- Text recognition\n- Field extraction\n- Multi-format support")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 💬 Chat Mode")
        st.write("Interactive conversation with VLM models about document content.")
        st.markdown("**Features:**")
        st.markdown("- Visual Q&A\n- Context understanding\n- Markdown support")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Comparison")
        st.write("Compare different models' performance on various document types.")
        st.markdown("**Metrics:**")
        st.markdown("- Accuracy\n- Speed\n- Memory usage")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.header("🎯 Research Goals")
    
    tabs = st.tabs(["Overview", "Timeline", "Learning Objectives", "Results"])
    
    with tabs[0]:
        st.markdown("""
        This educational project explores modern Vision Language Models for document OCR tasks.
        We investigate different architectures, compare their performance, and develop practical
        applications for real-world document processing.
        
        **Key Research Questions:**
        1. How do specialized OCR models compare to general VLM models?
        2. What trade-offs exist between model size and accuracy?
        3. Can VLMs handle structured data extraction reliably?
        4. How does context understanding improve OCR results?
        """)
    
    with tabs[1]:
        st.markdown("""
        **Phase 1: Preparation** (2 weeks)
        - ✅ Environment setup
        - ✅ Architecture research
        - 🔄 Dataset collection
        
        **Phase 2: Model Integration** (3 weeks)
        - 🔄 GOT-OCR integration
        - ⏳ Qwen2-VL integration
        - ⏳ API development
        
        **Phase 3: UI Development** (2 weeks)
        - ⏳ Streamlit interface
        - ⏳ OCR workflow
        - ⏳ Chat interface
        
        **Phase 4: Testing** (2 weeks)
        - ⏳ Accuracy testing
        - ⏳ Performance optimization
        - ⏳ Comparative analysis
        
        **Phase 5: Documentation** (1 week)
        - ⏳ Final report
        - ⏳ Presentation
        """)
    
    with tabs[2]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Technical Skills:**
            - VLM model deployment
            - Image preprocessing
            - Inference optimization
            - Streamlit development
            - Docker containerization
            """)
        
        with col2:
            st.markdown("""
            **Research Skills:**
            - Model comparison
            - Metric evaluation
            - Scientific documentation
            - Critical analysis
            - Result presentation
            """)
    
    with tabs[3]:
        st.info("Results will be updated as the research progresses.")
        st.markdown("""
        **Expected Outcomes:**
        - Comparative analysis report
        - Performance benchmarks
        - Best practices guide
        - Open-source implementation
        """)

elif "📄 OCR Mode" in page:
    st.header("📄 Document OCR Mode")
    
    st.info("⚠️ This feature is under development. Model integration in progress.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Document")
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=config["ocr"]["supported_formats"],
            help="Supported formats: JPG, PNG, BMP, TIFF"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            
        document_type = st.selectbox(
            "Document Type",
            list(config["document_templates"].keys()),
            format_func=lambda x: x.capitalize()
        )
        
        if st.button("🚀 Extract Text", type="primary"):
            if uploaded_file:
                with st.spinner("Processing document..."):
                    st.warning("Model loading functionality will be implemented in Phase 2")
            else:
                st.error("Please upload an image first")
    
    with col2:
        st.subheader("Extraction Results")
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**Recognized Text:**")
        st.code("Text will appear here after OCR processing...", language="text")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**Extracted Fields:**")
        if document_type:
            fields = config["document_templates"][document_type]["fields"]
            for field in fields:
                st.text_input(field, placeholder=f"{field} will be extracted here", disabled=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif "💬 Chat Mode" in page:
    st.header("💬 Interactive VLM Chat")
    
    st.info("⚠️ This feature is under development. Model integration in progress.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Upload Image")
        chat_image = st.file_uploader(
            "Image for chat context",
            type=config["ocr"]["supported_formats"],
            key="chat_upload"
        )
        
        if chat_image:
            st.image(chat_image, caption="Context Image", use_container_width=True)
    
    with col2:
        st.subheader("Conversation")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about the image..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                st.markdown("Model response will appear here after integration is complete.")

elif "📊 Model Comparison" in page:
    st.header("📊 Model Comparison")
    
    st.info("Comparative analysis will be available after model testing phase.")
    
    comparison_data = {
        "Model": ["GOT-OCR 2.0", "Qwen2-VL 2B", "Qwen2-VL 7B"],
        "Parameters": ["580M", "2B", "7B"],
        "Accuracy (CER)": ["-", "-", "-"],
        "Speed (sec/page)": ["-", "-", "-"],
        "Memory (GB)": ["-", "-", "-"],
        "Best For": ["Complex layouts", "General OCR", "Advanced analysis"]
    }
    
    st.table(comparison_data)
    
    st.markdown("""
    **Evaluation Metrics:**
    - **CER (Character Error Rate)**: Lower is better
    - **WER (Word Error Rate)**: Accuracy at word level
    - **Field Extraction Accuracy**: Structured data extraction
    - **Processing Speed**: Time per document
    - **Memory Usage**: RAM requirements
    """)

else:  # Documentation
    st.header("📚 Documentation")
    
    doc_tabs = st.tabs(["Quick Start", "Models", "Architecture", "API Reference", "Contributing"])
    
    with doc_tabs[0]:
        st.markdown("""
        ## Quick Start Guide
        
        ### Installation
        
        ```bash
        # Clone repository
        git clone https://github.com/OlegKarenkikh/chatvlmllm.git
        cd chatvlmllm
        
        # Create virtual environment
        python -m venv venv
        source venv/bin/activate
        
        # Install dependencies
        pip install -r requirements.txt
        ```
        
        ### Running the Application
        
        ```bash
        streamlit run app.py
        ```
        
        ### First Steps
        
        1. Select a model from the sidebar
        2. Choose OCR or Chat mode
        3. Upload your document/image
        4. Get results instantly!
        """)
    
    with doc_tabs[1]:
        st.markdown("""
        ## Supported Models
        
        ### GOT-OCR 2.0
        
        **Description**: Specialized OCR model with state-of-the-art accuracy for document understanding.
        
        **Strengths**:
        - Complex layout recognition
        - Table extraction
        - Mathematical formula OCR
        - Multi-language support
        
        **Use Cases**:
        - Scientific papers
        - Financial documents
        - Forms and tables
        
        ### Qwen2-VL
        
        **Description**: General-purpose vision-language model from Alibaba Cloud.
        
        **Strengths**:
        - Multimodal understanding
        - Context-aware responses
        - Interactive chat
        - Reasoning capabilities
        
        **Use Cases**:
        - Document Q&A
        - Visual analysis
        - Content extraction
        """)
    
    with doc_tabs[2]:
        st.markdown("""
        ## Architecture Overview
        
        ### System Components
        
        1. **Model Layer**: VLM model integration and inference
        2. **Processing Layer**: Image preprocessing and text extraction
        3. **UI Layer**: Streamlit interface and visualization
        4. **Storage Layer**: Results caching and history
        
        ### Data Flow
        
        ```
        User Upload → Image Preprocessing → Model Inference → 
        Post-processing → Result Display → Export Options
        ```
        
        ### Technology Stack
        
        - **Frontend**: Streamlit + Custom CSS
        - **Backend**: PyTorch + Transformers
        - **Image Processing**: Pillow + OpenCV
        - **Data Handling**: Pandas + NumPy
        """)
    
    with doc_tabs[3]:
        st.markdown("""
        ## API Reference
        
        ### Model Interface
        
        ```python
        from models import ModelLoader
        
        # Load model
        model = ModelLoader.load("got_ocr")
        
        # Process image
        result = model.process_image(
            image_path="document.jpg",
            mode="ocr"
        )
        
        # Extract fields
        fields = model.extract_fields(
            result,
            template="passport"
        )
        ```
        
        ### Utility Functions
        
        ```python
        from utils import ImageProcessor
        
        # Preprocess image
        processed = ImageProcessor.preprocess(
            image,
            resize=True,
            enhance=True
        )
        ```
        """)
    
    with doc_tabs[4]:
        st.markdown("""
        ## Contributing
        
        We welcome contributions! Here's how you can help:
        
        ### Development Setup
        
        1. Fork the repository
        2. Create a feature branch
        3. Make your changes
        4. Write tests
        5. Submit a pull request
        
        ### Code Style
        
        - Follow PEP 8
        - Use type hints
        - Add docstrings
        - Write unit tests
        
        ### Areas for Contribution
        
        - 🐛 Bug fixes
        - ✨ New features
        - 📝 Documentation
        - 🧪 Tests
        - 🎨 UI improvements
        """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; padding: 2rem;">
    <p>ChatVLMLLM - Educational Research Project</p>
    <p>Built with ❤️ using Streamlit | 
    <a href="https://github.com/OlegKarenkikh/chatvlmllm" target="_blank">GitHub</a> | 
    MIT License</p>
</div>
""", unsafe_allow_html=True)