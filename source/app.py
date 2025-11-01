import streamlit as st
from Smarth_da import CSVChat
import os
from dotenv import load_dotenv

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")

# Page config
st.set_page_config(
    page_title="Smart Data Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid #1f77b4;
        }
        .user-message {
            background-color: #e3f2fd;
            border-left-color: #2196f3;
        }
        .assistant-message {
            background-color: #f5f5f5;
            border-left-color: #4caf50;
        }
        .stButton>button {
            width: 100%;
            background-color: #1f77b4;
            color: white;
            font-weight: bold;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
        }
        .stButton>button:hover {
            background-color: #1565c0;
        }
        .info-box {
            background-color: #2d3748;
            color: #e2e8f0;
            padding: 1.2rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            border: 1px solid #4a5568;
        }
        .info-box ul {
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }
        .info-box li {
            margin: 0.3rem 0;
        }
        .sidebar-info {
            background-color: #2d3748;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            border: 1px solid #4a5568;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat' not in st.session_state:
    with st.spinner("🔄 Loading datasets... This may take a moment."):
        csv_files = {
            'agriculture': '../dataset/Districtwise_Statewise crop area and production (All India, 1997 – present).csv',
            'climate': '../dataset/imd_rainfall_clean.csv'
        }
        st.session_state.chat = CSVChat(csv_files, OPEN_AI_API_KEY)
        st.session_state.messages = []
        st.session_state.initialized = True

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown('<h1 class="main-header">📊 Smart Data Analysis</h1>', unsafe_allow_html=True)

# Sidebar with info
with st.sidebar:
    st.markdown("### 💡 About")
    st.markdown("""
    <div class="sidebar-info">
        Ask questions about your agricultural and climate data.
        The AI will analyze the datasets and provide insights.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📁 Available Datasets")
    st.success("✅ Agriculture Data")
    st.info("🌧️ Climate/Rainfall Data")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Display chat history
chat_container = st.container()

with chat_container:
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="info-box">
            👋 Welcome! Ask me anything about your data. For example:
            <ul>
                <li>What is the average rainfall in Maharashtra?</li>
                <li>Compare crop production across different states</li>
                <li>Which state has the highest production of rice?</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display assistant message in a container with better layout
            st.markdown("""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant:</strong>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(message["content"])
            
            # Show code in a separate expandable section if available
            if message.get("code"):
                st.markdown("---")
                with st.expander("💻 View Generated Code", expanded=False):
                    st.code(message["code"], language="python")

# Input area
st.markdown("---")
col1, col2 = st.columns([4, 1])

with col1:
    question = st.text_input(
        "💬 Ask your question:",
        placeholder="e.g., What is the average rainfall in Maharashtra?",
        key="question_input",
        label_visibility="collapsed"
    )

with col2:
    ask_button = st.button("🚀 Ask", use_container_width=True)

# Process question
if ask_button and question:
    if question.strip():
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Show loading state
        with st.spinner("🤔 Analyzing your question... This may take a few seconds."):
            try:
                result = st.session_state.chat.chat(question)
                
                # Add assistant response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result['answer'],
                    "code": result.get('code', '')
                })
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "code": ""
                })
        
        # Clear input and rerun to show new message
        st.rerun()

elif ask_button:
    st.warning("⚠️ Please enter a question before asking.")
