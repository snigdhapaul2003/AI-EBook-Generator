import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import our modules
from config import FormatType, SYSTEM_INFO
from graph import EbookGeneratorGraph

# Page configuration
st.set_page_config(
    page_title="AI E-Book Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': "https://github.com/your-repo/issues",
        'About': "# AI E-Book Generator\nPowered by LangGraph and Gemini AI"
    }
)

# Custom CSS for ultramodern design
def get_theme_css():
    """Get CSS based on current theme"""
    # Get current theme from session state
    theme = st.session_state.get('app_settings', {}).get('theme', 'Purple Gradient')
    
    # Define theme colors
    theme_colors = {
        "Purple Gradient": {"primary": "#667eea", "secondary": "#764ba2"},
        "Blue Ocean": {"primary": "#2196F3", "secondary": "#1976D2"},
        "Sunset Orange": {"primary": "#FF9800", "secondary": "#F57C00"},
        "Forest Green": {"primary": "#4CAF50", "secondary": "#388E3C"}
    }
    
    colors = theme_colors.get(theme, theme_colors["Purple Gradient"])
    
    return f"""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global styles */
.main {{
    font-family: 'Inter', sans-serif;
}}

/* Header styling */
.main-header {{
    background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
    padding: 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    text-align: center;
}}

.main-header h1 {{
    color: white;
    font-weight: 700;
    font-size: 3rem;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}}

.main-header p {{
    color: rgba(255,255,255,0.9);
    font-size: 1.2rem;
    margin-bottom: 0;
}}

/* Card styling */
.custom-card {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}}

/* Progress bar styling */
.progress-container {{
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7);
    border-radius: 50px;
    height: 10px;
    overflow: hidden;
    margin: 1rem 0;
}}

.progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, {colors['primary']}, {colors['secondary']});
    border-radius: 50px;
    transition: width 0.3s ease;
}}

/* Button styling */
.stButton > button {{
    background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
    color: white;
    border: none;
    border-radius: 15px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba({colors['primary'][1:3]}, {colors['primary'][3:5]}, {colors['primary'][5:7]}, 0.4);
}}

.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba({colors['primary'][1:3]}, {colors['primary'][3:5]}, {colors['primary'][5:7]}, 0.6);
}}

/* Sidebar styling */
.css-1d391kg {{
    background: linear-gradient(180deg, {colors['primary']} 0%, {colors['secondary']} 100%);
}}

/* Metrics styling */
.metric-card {{
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    padding: 1.5rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}}

/* Animation classes */
.fade-in {{
    animation: fadeIn 0.8s ease-in;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(30px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
</style>
"""

# Apply theme CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Initialize session state
if 'generation_state' not in st.session_state:
    st.session_state.generation_state = 'idle'
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'current_step' not in st.session_state:
    st.session_state.current_step = ''
if 'ebook_result' not in st.session_state:
    st.session_state.ebook_result = None
if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []

def display_header():
    """Display the main header with animations"""
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🤖 AI E-Book Generator v1.0</h1>
        <p>Transform your ideas into professional e-books with AI-powered creativity</p>
    </div>
    """, unsafe_allow_html=True)

def display_stats():
    """Display statistics dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📚</h3>
            <h2>{}</h2>
            <p>E-books Generated</p>
        </div>
        """.format(len(st.session_state.generation_history)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡</h3>
            <h2>Active</h2>
            <p>AI Status</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯</h3>
            <h2>100%</h2>
            <p>Success Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🚀</h3>
            <h2>v1.0</h2>
            <p>Version</p>
        </div>
        """, unsafe_allow_html=True)

def display_progress(progress_value, step_name):
    """Display animated progress bar"""
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress_value}%"></div>
    </div>
    <p style="text-align: center; color: #667eea; font-weight: 600;">
        <span class="status-indicator status-generating"></span>
        {step_name}
    </p>
    """, unsafe_allow_html=True)

def get_user_inputs():
    """Get user inputs with modern UI and default settings"""
    st.markdown("### 🎨 Creative Parameters")
    
    # Load saved settings
    settings = st.session_state.get('app_settings', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input(
            "📖 E-book Topic",
            value="How to win friends and influence people",
            help="Enter the main topic or theme for your e-book"
        )
        
        audience = st.text_input(
            "👥 Target Audience",
            value="general readers",
            help="Specify who your e-book is intended for"
        )
        
        tone = st.selectbox(
            "🎭 Writing Tone",
            options=[
                "professional but conversational",
                "casual and friendly",
                "formal and academic",
                "inspiring and motivational",
                "humorous and engaging",
                "technical and detailed"
            ],
            index=[
                "professional but conversational",
                "casual and friendly",
                "formal and academic",
                "inspiring and motivational",
                "humorous and engaging",
                "technical and detailed"
            ].index(settings.get('default_tone', 'professional but conversational')),
            help="Choose the tone that best fits your audience"
        )
    
    with col2:
        format_type = st.selectbox(
            "📄 Output Format",
            options=["doc", "markdown", "pdf"],
            index=["doc", "markdown", "pdf"].index(settings.get('default_format', 'doc')),
            help="Select the format for your final e-book"
        )
        
        additional_description = st.text_area(
            "✨ Additional Requirements",
            placeholder="e.g., Include practical exercises, Focus on real-world examples, Add case studies...",
            help="Provide specific requirements or context for your e-book",
            height=100
        )
        
        api_key = st.text_input(
            "🔑 Gemini API Key",
            type="password",
            value=settings.get('api_key', ''),
            help="Enter your Gemini API key"
        )
    
    return topic, audience, tone, format_type, additional_description, api_key

def display_generation_steps():
    """Display the generation process steps"""
    steps = [
        "🚀 Initializing",
        "📝 Generating Outline",
        "🔍 Reviewing Structure",
        "📚 Creating Chapters",
        "✅ Quality Check",
        "📦 Compiling Content",
        "🎨 Formatting",
        "💾 Exporting"
    ]
    
    st.markdown("### 🔄 Generation Process")
    
    progress_cols = st.columns(len(steps))
    
    for i, (col, step) in enumerate(zip(progress_cols, steps)):
        with col:
            if i < st.session_state.progress * len(steps) / 100:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-size: 0.8rem; color: #00b894; font-weight: 600;">{step}</div>
                </div>
                """, unsafe_allow_html=True)
            elif i == int(st.session_state.progress * len(steps) / 100):
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;" class="pulse">⏳</div>
                    <div style="font-size: 0.8rem; color: #ffeaa7; font-weight: 600;">{step}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem; opacity: 0.3;">⏸️</div>
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5); font-weight: 600;">{step}</div>
                </div>
                """, unsafe_allow_html=True)

def update_progress_callback(step_name, progress_value):
    """Callback function to update progress during generation"""
    if 'progress_bar' in st.session_state and 'status_text' in st.session_state:
        st.session_state.progress = progress_value
        st.session_state.current_step = step_name
        st.session_state.progress_bar.progress(progress_value / 100)
        st.session_state.status_text.text(f"🔄 {step_name}")
        st.rerun()

def get_progress_steps():
    """Get the actual progress steps from the workflow"""
    return [
        ("🚀 Initializing", 5),
        ("📝 Generating Outline", 15),
        ("🔍 Reviewing Structure", 25),
        ("📚 Creating Chapter 1", 35),
        ("📚 Creating Chapter 2", 45),
        ("📚 Creating Chapter 3", 55),
        ("📚 Creating Chapters...", 70),
        ("✅ Quality Check", 80),
        ("� Compiling Content", 90),
        ("🎨 Formatting", 95),
        ("💾 Exporting", 100)
    ]

def run_ebook_generation(topic, audience, tone, format_type, additional_description, api_key):
    """Run the e-book generation process with real-time updates"""
    try:
        # Set API key in environment
        os.environ["GEMINI_API_KEY"] = api_key
        
        # Initialize progress tracking (single progress bar)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Update progress: Initializing
        progress_bar.progress(5)
        status_text.markdown("🚀 **Initializing AI systems...**")
        
        # Initialize the graph
        ebook_generator = EbookGeneratorGraph(api_key=api_key)
        
        # Update progress: Starting generation
        progress_bar.progress(10)
        status_text.markdown("📝 **Starting e-book generation...**")
        
        # Run the workflow with detailed error handling
        try:
            # Create a callback to update progress
            def update_progress(node_name, chapter_info=None):
                """Update progress based on current node"""
                progress_map = {
                    "initialize": (15, "🎯 **Initializing workflow...**"),
                    "generate_outline": (25, "📋 **Generating e-book outline...**"),
                    "review_outline": (35, "🔍 **Reviewing outline structure...**"),
                    "revise_outline": (40, "✏️ **Refining outline...**"),
                    "context_manager": (45, "📖 **Preparing chapter context...**"),
                    "generate_chapter": (50, f"✍️ **Generating {chapter_info or 'chapter'}...**"),
                    "review_chapter": (70, f"🔍 **Reviewing {chapter_info or 'chapter'}...**"),
                    "revise_chapter": (75, f"✏️ **Refining {chapter_info or 'chapter'}...**"),
                    "chapter_completion": (80, f"✅ **Completing {chapter_info or 'chapter'}...**"),
                    "compilation": (90, "📚 **Compiling e-book...**"),
                    "format_conversion": (95, "🎨 **Formatting document...**"),
                    "export": (98, "💾 **Finalizing export...**")
                }
                
                if node_name in progress_map:
                    progress_val, message = progress_map[node_name]
                    progress_bar.progress(progress_val)
                    status_text.markdown(message)
                    time.sleep(0.1)  # Small delay for visual feedback
            
            # Store the callback in session state for nodes to access
            st.session_state.progress_callback = update_progress
            
            result = ebook_generator.run(
                topic=topic,
                target_audience=audience,
                tone=tone,
                format_type=format_type,
                additional_description=additional_description
            )
            
            # Check for errors in the result
            if result and "error" in result:
                error_msg = result["error"]
                
                # Provide user-friendly error messages
                if "JSON" in error_msg or "parsing" in error_msg.lower():
                    user_friendly_error = """
                    🤖 **AI Response Format Issue**: The AI generated a response that couldn't be properly parsed. 
                    This usually happens when the AI response is incomplete or malformed.
                    
                    **Suggestions:**
                    • Try again with a simpler topic
                    • Check your internet connection
                    • Verify your API key is valid
                    • Try a different tone or format
                    """
                elif "API" in error_msg or "key" in error_msg.lower():
                    user_friendly_error = """
                    🔑 **API Key Issue**: There's a problem with your Gemini API key.
                    
                    **Suggestions:**
                    • Verify your API key is correct
                    • Check if you have sufficient API credits
                    • Make sure the API key has the required permissions
                    """
                else:
                    user_friendly_error = f"""
                    ❌ **Generation Error**: {error_msg}
                    
                    **Suggestions:**
                    • Try again with different parameters
                    • Check your internet connection
                    • Simplify your topic or requirements
                    """
                
                st.error(user_friendly_error)
                return None
            
            # Update progress: Completed
            progress_bar.progress(100)
            status_text.markdown("✅ **E-book generation complete!**")
            
            return result
            
        except Exception as workflow_error:
            # Handle workflow-specific errors
            error_msg = str(workflow_error)
            
            if "JSON" in error_msg or "parsing" in error_msg:
                st.error("""
                🤖 **AI Response Processing Error**: The AI generated content that couldn't be processed properly.
                
                **What happened:** The AI's response format was unexpected or incomplete.
                
                **Try these solutions:**
                1. **Simplify your topic** - Use a more straightforward topic
                2. **Reduce additional requirements** - Try with fewer custom requirements
                3. **Check your connection** - Ensure stable internet connectivity
                4. **Try again** - Sometimes the AI needs a second attempt
                """)
            elif "API" in error_msg or "key" in error_msg:
                st.error("""
                🔑 **API Connection Error**: There's an issue with your API key or connection.
                
                **What happened:** The system couldn't connect to the Gemini API.
                
                **Try these solutions:**
                1. **Verify API key** - Check if your Gemini API key is correct
                2. **Check credits** - Ensure you have sufficient API credits
                3. **Network connection** - Verify your internet connection
                4. **Try again** - The API might be temporarily unavailable
                """)
            else:
                st.error(f"""
                ⚠️ **Generation Error**: {error_msg}
                
                **What happened:** An unexpected error occurred during e-book generation.
                
                **Try these solutions:**
                1. **Refresh the page** - Sometimes a simple refresh helps
                2. **Try different parameters** - Change topic, tone, or format
                3. **Check all inputs** - Ensure all required fields are filled
                4. **Try again later** - The service might be temporarily busy
                """)
            
            return None
        
    except Exception as e:
        # Handle initialization errors
        error_msg = str(e)
        
        if "GEMINI_API_KEY" in error_msg:
            st.error("""
            🔑 **API Key Required**: No valid Gemini API key found.
            
            **What to do:**
            1. Enter your API key in the form above
            2. Or set the GEMINI_API_KEY environment variable
            3. Get an API key from: https://makersuite.google.com/app/apikey
            """)
        else:
            st.error(f"""
            🚨 **Initialization Error**: {error_msg}
            
            **What happened:** The system couldn't initialize properly.
            
            **Try these solutions:**
            1. **Check your API key** - Ensure it's valid and has permissions
            2. **Refresh the page** - Sometimes a refresh resolves issues
            3. **Check your connection** - Ensure stable internet connectivity
            """)
        
        st.session_state.generation_state = 'error'
        return None

def display_result(result):
    """Display the generation result with proper error handling"""
    if not result:
        st.error("❌ E-book generation failed. Please check your inputs and try again.")
        return
    
    if "error" in result:
        st.error(f"❌ Generation Error: {result['error']}")
        return
    
    if "export_complete" in result and result["export_complete"]:
        st.success("🎉 E-book Generation Complete!")
        
        # Display summary
        if "ebook_state" in result:
            ebook_state = result["ebook_state"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="custom-card">
                    <h3>📖 {ebook_state.get('title', 'Unknown')}</h3>
                    <p><strong>Chapters:</strong> {len(ebook_state.get('chapters', []))}</p>
                    <p><strong>Format:</strong> {ebook_state.get('format_type', 'doc').upper()}</p>
                    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                output_file = result.get("output_filename", "ebook.md")
                output_path = os.path.join("output", output_file)

                if not os.path.exists(output_path):
                    st.warning("⚠️ Output file not found.")
                else:
                    file_ext = os.path.splitext(output_file)[-1].lower()

                    # Read binary or text depending on extension
                    if file_ext == ".pdf":
                        with open(output_path, "rb") as f:
                            file_data = f.read()
                        mime_type = "application/pdf"
                    elif file_ext == ".docx":
                        with open(output_path, "rb") as f:
                            file_data = f.read()
                        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    else:  # default to text
                        with open(output_path, "r", encoding="utf-8") as f:
                            file_data = f.read()
                        mime_type = "text/plain"

                    # Download button
                    st.download_button(
                        label="📥 Download E-book",
                        data=file_data,
                        file_name=output_file,
                        mime=mime_type,
                        key="download_ebook"
                    )

                    # File size display
                    file_size = os.path.getsize(output_path)
                    if file_size > 1024 * 1024:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    elif file_size > 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size} bytes"
                    st.info(f"📄 File size: {size_str}")
        
        
        # Display chapter summary
        if "ebook_state" in result and "chapters" in result["ebook_state"]:
            chapters = result["ebook_state"]["chapters"]
            
            st.markdown("### 📚 Chapter Overview")
            for i, chapter in enumerate(chapters, 1):
                with st.expander(f"Chapter {i}: {chapter.get('title', 'Untitled')}", expanded=False):
                    if chapter.get('content'):
                        # Show first 200 characters of content
                        content_preview = chapter['content'][:200] + "..." if len(chapter['content']) > 200 else chapter['content']
                        st.markdown(f"**Preview:** {content_preview}")
                    
                    if chapter.get('bullet_points'):
                        st.markdown("**Key Points:**")
                        for point in chapter['bullet_points']:
                            st.markdown(f"• {point}")
        
        # Add to history
        if "ebook_state" in result:
            st.session_state.generation_history.append({
                'title': ebook_state.get('title', 'Unknown'),
                'timestamp': datetime.now().isoformat(),
                'chapters': len(ebook_state.get('chapters', [])),
                'format': ebook_state.get('format_type', 'doc'),
                'topic': ebook_state.get('topic', 'Unknown'),
                'audience': ebook_state.get('target_audience', 'Unknown')
            })
        
    else:
        st.warning("⚠️ E-book generation completed but no exportable content was found.")
        if result:
            st.json(result)  # Show raw result for debugging

def display_outline(ebook_state):
    """Display the e-book outline"""
    chapters = ebook_state.get("chapters", [])
    
    for chapter in chapters:
        chapter_num = chapter.get("chapter_number", 0)
        chapter_title = chapter.get("title", "Untitled Chapter")
        bullet_points = chapter.get("bullet_points", [])
        
        st.markdown(f"**Chapter {chapter_num}: {chapter_title}**")
        for point in bullet_points:
            st.markdown(f"• {point}")
        st.markdown("---")

def display_sidebar():
    """Display the sidebar with additional features"""
    with st.sidebar:
        st.markdown("### 🎛️ Control Panel")
        
        # Quick actions
        st.markdown("#### ⚡ Quick Actions")
        if st.button("🔄 New Generation", use_container_width=True):
            st.session_state.generation_state = 'idle'
            st.session_state.progress = 0
            st.rerun()
        
        # Generation history
        if st.session_state.generation_history:
            st.markdown("### 📚 Recent E-books")
            for i, item in enumerate(st.session_state.generation_history[-5:]):
                with st.expander(f"📖 {item['title'][:30]}{'...' if len(item['title']) > 30 else ''}", expanded=False):
                    st.markdown(f"**Topic:** {item.get('topic', 'N/A')}")
                    st.markdown(f"**Audience:** {item.get('audience', 'N/A')}")
                    st.markdown(f"**Chapters:** {item['chapters']}")
                    st.markdown(f"**Format:** {item['format'].upper()}")
                    st.markdown(f"**Generated:** {pd.to_datetime(item['timestamp']).strftime('%Y-%m-%d %H:%M')}")
        
        # Current generation status
        if st.session_state.generation_state != 'idle':
            st.markdown("### 🔄 Current Status")
            if st.session_state.generation_state == 'generating':
                st.markdown("🟡 **Generating...**")
                st.progress(st.session_state.progress / 100)
                st.markdown(f"*{st.session_state.current_step}*")
            elif st.session_state.generation_state == 'complete':
                st.markdown("🟢 **Complete!**")
            elif st.session_state.generation_state == 'error':
                st.markdown("🔴 **Error occurred**")
        
        # Tips and tricks
        st.markdown("### 💡 Pro Tips")
        tips = [
            "Great for self-help and motivational books",
            "Ideal for journals, prompts, and how-to guides",
            "Best for general, topic-based content",
            "Not suited for technical or code-heavy writing",
            "Avoid fiction, storytelling, or character-driven plots",
            "Check sample books for inspiration"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")
        
        
        # Resources
        st.markdown("### 📚 Resources")
        st.markdown("[📖 Documentation](https://github.com/your-repo)")
        st.markdown("[🐛 Report Issues](https://github.com/your-repo/issues)")
        st.markdown("[💬 Discord Community](https://discord.gg/your-server)")
        st.markdown("[⭐ Star on GitHub](https://github.com/your-repo)")
        
        # Footer
        st.markdown("---")
        st.markdown(
            '<p style="text-align: center; color: #666; font-size: 0.8em;">'
            'Made with ❤️ using Streamlit<br>'
            'AI E-Book Generator v1.0'
            '</p>',
            unsafe_allow_html=True
        )

def main():
    """Main application function"""
    display_header()
    display_stats()
    display_sidebar()
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Generate", "📚 Sample Books", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        # Input form
        topic, audience, tone, format_type, additional_description, api_key = get_user_inputs()
        
        # Generation button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            generate_button = st.button("🚀 Generate E-book", use_container_width=True)
        
        # Validation
        if generate_button:
            if not topic:
                st.error("❌ Please enter a topic for your e-book")
            elif not api_key:
                st.error("❌ Please provide your Gemini API key")
            else:
                st.session_state.generation_state = 'generating'
                st.session_state.progress = 0
                
                # Show progress header
                st.markdown("### 🔄 Generation in Progress")
                
                # Run actual generation (progress bar will be created inside the function)
                with st.spinner("🤖 AI is crafting your e-book..."):
                    result = run_ebook_generation(
                        topic, audience, tone, format_type, 
                        additional_description, api_key
                    )
                
                if result:
                    st.session_state.ebook_result = result
                    st.session_state.generation_state = 'complete'
                    display_result(result)
                else:
                        st.session_state.generation_state = 'error'
                        st.error("❌ Generation failed. Please check your inputs and try again.")
        
        # Display generation steps
        if st.session_state.generation_state == 'generating':
            display_generation_steps()
    
    with tab2:
        st.markdown("### 📚 Sample E-Books")
        st.markdown("*Explore our collection of professionally generated e-books for inspiration*")
        
        # Create sample books data
        sample_books = [
            {
                "title": "Time Management Mastery for Students",
                "description": "A comprehensive guide to effective time management techniques specifically designed for students balancing academics, social life, and personal growth.",
                "category": "Education & Self-Help",
                "pages": "37 pages",
                "format": "PDF",
                "path": "sample_books/Unlock_Your_A-Game__The_Student's_Guide_to_Mastering_Time_&_Crushing_Goals.pdf",  # Path to be provided
                "cover_color": "#4CAF50",
                "icon": "⏰"
            },
            {
                "title": "How to Win Friends and Influence People",
                "description": "Master the art of human connection and social influence with timeless principles and modern applications for building meaningful relationships.",
                "category": "Personal Development",
                "pages": "38 pages", 
                "format": "PDF",
                "path": "sample_books/The_Human_Connection_Code_Unlock_Influence_&_Build_Unforgettable_Relationships.pdf",  # Path to be provided
                "cover_color": "#2196F3",
                "icon": "🤝"
            },
            {
                "title": "Bonsai Tree Care for Beginners",
                "description": "Learn the ancient art of bonsai cultivation with step-by-step instructions, care tips, and styling techniques for creating beautiful miniature trees.",
                "category": "Gardening & Hobbies",
                "pages": "39 pages",
                "format": "PDF", 
                "path": "sample_books/Bonsai_Beginner's_Blueprint__Your_Simple_Guide_to_Thriving_Miniature_Trees.pdf",  # Path to be provided
                "cover_color": "#FF9800",
                "icon": "🌳"
            },
            {
                "title": "10 Principles for Being a Good Leader",
                "description": "Essential leadership principles that transform managers into inspiring leaders who motivate teams and drive organizational success.",
                "category": "Leadership & Management",
                "pages": "37 pages",
                "format": "PDF",
                "path": "sample_books/The_Manager's_Edge__10_Principles_for_Exceptional_Leadership.pdf",  # Path to be provided  
                "cover_color": "#9C27B0",
                "icon": "👑"
            }
        ]
        
        # Display sample books in a grid
        for i in range(0, len(sample_books), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(sample_books):
                    book = sample_books[i + j]
                    with col:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, {book['cover_color']}20 0%, {book['cover_color']}10 100%);
                            border: 1px solid {book['cover_color']}30;
                            border-radius: 15px;
                            padding: 20px;
                            margin: 10px 0;
                            transition: transform 0.3s ease;
                        ">
                            <div style="text-align: center; font-size: 2em; margin-bottom: 10px;">
                                {book['icon']}
                            </div>
                            <h4 style="color: {book['cover_color']}; margin-bottom: 10px; text-align: center;">
                                {book['title']}
                            </h4>
                            <p style="font-size: 0.9em; opacity: 0.8; margin-bottom: 15px;">
                                {book['description']}
                            </p>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <span style="background: {book['cover_color']}20; padding: 5px 10px; border-radius: 20px; font-size: 0.8em;">
                                    {book['category']}
                                </span>
                                <span style="font-size: 0.8em; opacity: 0.7;">
                                    {book['pages']} • {book['format']}
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Download button (disabled until path is provided)
                        if book['path']:
                            if st.button(f"📥 Download {book['title']}", key=f"download_{i+j}"):
                                st.success(f"Downloading {book['title']}...")
                        else:
                            st.button(f"📥 Download {book['title']}", key=f"download_{i+j}", disabled=True, help="PDF path not yet configured")
        
        # Add note about sample books
        st.markdown("---")
        st.info("💡 **Note**: These are sample e-books generated by our AI system.")
    
    with tab3:
        st.markdown("### 📊 Generation Analytics")
        
        if st.session_state.generation_history:
            # Create analytics charts
            df = pd.DataFrame(st.session_state.generation_history)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_ebooks = len(df)
                st.metric("📚 Total E-books", total_ebooks)
            
            with col2:
                avg_chapters = df['chapters'].mean()
                st.metric("📖 Avg Chapters", f"{avg_chapters:.1f}")
            
            with col3:
                most_common_format = df['format'].mode()[0] if len(df) > 0 else "N/A"
                st.metric("📄 Popular Format", most_common_format.upper())
            
            with col4:
                recent_count = len(df[df['timestamp'] > (datetime.now() - pd.Timedelta(days=7)).isoformat()])
                st.metric("🗓️ This Week", recent_count)
            
            # Charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Format distribution
                format_counts = df['format'].value_counts()
                fig_pie = px.pie(
                    values=format_counts.values,
                    names=format_counts.index,
                    title="📄 Format Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with chart_col2:
                # Chapters distribution
                fig_hist = px.histogram(
                    df, x='chapters',
                    title="📚 Chapter Count Distribution",
                    nbins=10,
                    color_discrete_sequence=['#667eea']
                )
                fig_hist.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # Timeline
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df_timeline = df.copy()
            df_timeline['end_time'] = df_timeline['timestamp'] + pd.Timedelta(minutes=30)  # Assume 30 min generation time
            
            fig_timeline = px.timeline(
                df_timeline, 
                x_start='timestamp', 
                x_end='end_time',
                y='title', 
                title="📅 Generation Timeline",
                color='format',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_timeline.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Detailed table
            st.markdown("### 📋 Generation History")
            
            # Format the dataframe for display
            display_df = df.copy()
            display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            display_df = display_df.rename(columns={
                'title': 'Title',
                'timestamp': 'Generated',
                'chapters': 'Chapters',
                'format': 'Format',
                'topic': 'Topic',
                'audience': 'Audience'
            })
            
            st.dataframe(
                display_df[['Title', 'Generated', 'Chapters', 'Format', 'Topic', 'Audience']],
                use_container_width=True
            )
            
            # Export analytics
            if st.button("📊 Export Analytics"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Analytics CSV",
                    data=csv,
                    file_name=f"ebook_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("📊 No generation history available yet. Generate your first e-book to see analytics!")
            
            # Show sample analytics
            st.markdown("### 📈 Sample Analytics Preview")
            sample_data = {
                'Format': ['DOC', 'PDF', 'Markdown'],
                'Count': [5, 3, 2]
            }
            fig_sample = px.bar(sample_data, x='Format', y='Count', title="Format Distribution (Sample)")
            fig_sample.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_sample, use_container_width=True)
    
    with tab4:
        st.markdown("### ⚙️ Application Settings")
        
        # Load current settings
        if 'app_settings' not in st.session_state:
            st.session_state.app_settings = {
                'theme': 'Purple Gradient',
                'max_chapters': 15,
                'quality_level': 'Balanced',
                'api_key': "",
                'default_format': 'doc',
                'default_tone': 'professional but conversational'
            }
        
        settings = st.session_state.app_settings
        
        # Theme settings
        st.markdown("#### 🎨 Theme Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            theme_option = st.selectbox(
                "Color Theme",
                ["Purple Gradient", "Blue Ocean", "Sunset Orange", "Forest Green"],
                index=["Purple Gradient", "Blue Ocean", "Sunset Orange", "Forest Green"].index(settings['theme'])
            )
            
            # Apply theme change immediately
            if theme_option != settings['theme']:
                settings['theme'] = theme_option
                st.session_state.app_settings['theme'] = theme_option
                st.rerun()
        
        with col2:
            # Show current theme preview
            theme_colors = {
                "Purple Gradient": "#667eea",
                "Blue Ocean": "#2196F3", 
                "Sunset Orange": "#FF9800",
                "Forest Green": "#4CAF50"
            }
            current_color = theme_colors.get(settings['theme'], "#667eea")
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {current_color} 0%, {current_color}80 100%);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                color: white;
                margin: 10px 0;
            ">
                <h4>Current Theme</h4>
                <p>{settings['theme']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Advanced settings
        st.markdown("#### 🔧 Advanced Options")
        col1, col2 = st.columns(2)
        
        with col1:
            max_chapters = st.slider(
                "Maximum Chapters", 
                5, 20, 
                settings['max_chapters'],
                help="Maximum number of chapters to generate"
            )
            
            quality_level = st.select_slider(
                "Quality Level",
                options=["Fast", "Balanced", "High Quality"],
                value=settings['quality_level'],
                help="Higher quality takes longer but produces better results"
            )
        
        with col2:
            default_format = st.selectbox(
                "Default Format",
                ["doc", "markdown", "pdf"],
                index=["doc", "markdown", "pdf"].index(settings['default_format'])
            )
            
            default_tone = st.selectbox(
                "Default Tone",
                [
                    "professional but conversational",
                    "casual and friendly",
                    "formal and academic",
                    "inspiring and motivational",
                    "humorous and engaging",
                    "technical and detailed"
                ],
                index=[
                    "professional but conversational",
                    "casual and friendly",
                    "formal and academic",
                    "inspiring and motivational",
                    "humorous and engaging",
                    "technical and detailed"
                ].index(settings['default_tone'])
            )
        
        # API Configuration
        st.markdown("#### 🔑 API Configuration")
        api_key_input = st.text_input(
            "Default Gemini API Key",
            value=settings['api_key'],
            type="password",
            help="Set your default API key to avoid entering it each time"
        )
        
        # Data Management
        st.markdown("#### 📊 Data Management")
        
        if st.button("🗑️ Clear History"):
            if st.session_state.generation_history:
                st.session_state.generation_history.clear()
                st.success("✅ Generation history cleared!")
            else:
                st.info("ℹ️ No history to clear")
        
        # Save settings
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("💾 Save Settings", use_container_width=True):
                # Update settings
                st.session_state.app_settings.update({
                    'theme': theme_option,
                    'max_chapters': max_chapters,
                    'quality_level': quality_level,
                    'api_key': api_key_input,
                    'default_format': default_format,
                    'default_tone': default_tone
                })
                
                # Save API key to environment if provided
                if api_key_input:
                    os.environ["GEMINI_API_KEY"] = api_key_input
                
                st.success("✅ Settings saved successfully!")
                st.balloons()
        
        # Reset to defaults
        st.markdown("#### 🔄 Reset Options")
        if st.button("🔄 Reset to Defaults"):
            st.session_state.app_settings = {
                'theme': 'Purple Gradient',
                'max_chapters': 15,
                'quality_level': 'Balanced',
                'api_key': "",
                'default_format': 'doc',
                'default_tone': 'professional but conversational'
            }
            st.success("✅ Settings reset to defaults!")
            st.rerun()

if __name__ == "__main__":
    main()
