"""Custom CSS styles for Streamlit app."""


def get_custom_css() -> str:
    """Get custom CSS for the application."""
    return """
    <style>
        /* Main theme colors */
        :root {
            --primary-color: #FF4B4B;
            --secondary-color: #0068C9;
            --background-color: #0E1117;
            --secondary-bg: #262730;
            --text-color: #FAFAFA;
            --success-color: #21C354;
            --warning-color: #FFA500;
            --error-color: #FF4B4B;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom header */
        .main-header {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(90deg, #FF4B4B 0%, #0068C9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
            animation: fadeIn 1s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Card styling */
        .info-card {
            background: var(--secondary-bg);
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 4px solid var(--primary-color);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .info-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 16px rgba(255, 75, 75, 0.3);
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
        }
        
        /* Primary button */
        .stButton>button[kind="primary"] {
            background: linear-gradient(90deg, #FF4B4B 0%, #FF6B6B 100%);
        }
        
        /* Upload area */
        .uploadedFile {
            border: 2px dashed var(--primary-color);
            border-radius: 10px;
            padding: 2rem;
            transition: border-color 0.3s ease;
        }
        
        .uploadedFile:hover {
            border-color: var(--secondary-color);
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem;
            color: #888;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #262730 0%, #1a1d26 100%);
        }
        
        [data-testid="stSidebar"] .stRadio > label {
            font-size: 1.1rem;
            font-weight: 500;
            padding: 0.5rem;
            transition: color 0.3s ease;
        }
        
        [data-testid="stSidebar"] .stRadio > label:hover {
            color: var(--primary-color);
        }
        
        /* Code blocks */
        .stCodeBlock {
            border-radius: 8px;
            border: 1px solid #333;
        }
        
        /* Success/Error messages */
        .stSuccess {
            background-color: rgba(33, 195, 84, 0.1);
            border-left: 4px solid var(--success-color);
            border-radius: 8px;
            padding: 1rem;
        }
        
        .stError {
            background-color: rgba(255, 75, 75, 0.1);
            border-left: 4px solid var(--error-color);
            border-radius: 8px;
            padding: 1rem;
        }
        
        .stWarning {
            background-color: rgba(255, 165, 0, 0.1);
            border-left: 4px solid var(--warning-color);
            border-radius: 8px;
            padding: 1rem;
        }
        
        .stInfo {
            background-color: rgba(0, 104, 201, 0.1);
            border-left: 4px solid var(--secondary-color);
            border-radius: 8px;
            padding: 1rem;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--secondary-bg);
            border-bottom: 3px solid var(--primary-color);
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background: linear-gradient(90deg, #FF4B4B 0%, #0068C9 100%);
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            border-radius: 8px;
            background-color: var(--secondary-bg);
            font-weight: 500;
        }
        
        /* Dataframe */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Chat messages */
        .stChatMessage {
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        /* File uploader */
        [data-testid="stFileUploadDropzone"] {
            border-radius: 10px;
            border: 2px dashed var(--primary-color);
            background-color: rgba(255, 75, 75, 0.05);
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--background-color);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--secondary-bg);
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-color);
        }
        
        /* Loading spinner */
        .stSpinner > div {
            border-top-color: var(--primary-color) !important;
        }
    </style>
    """