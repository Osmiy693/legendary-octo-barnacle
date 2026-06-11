"""
app.py - Main entry point for the AI Study Assistant & Course Project Manager.

This is a Streamlit application that demonstrates Object-Oriented Programming (OOP)
principles through a class hierarchy for document processing, AI interaction,
task management, and persistent storage.

Run with: streamlit run app.py
"""

import streamlit as st

from config import get_api_key

from document import Document, TextDocument, PDFDocument, MultiFileDocument
from ai_provider import AIProvider, OpenAIProvider
from agent import AIAgent, SummaryAgent, QuizAgent, QuestionAnswerAgent, TaskGenerationAgent
from task import Task, TaskManager
from storage import StorageManager

from ui_home import render_home
from ui_upload import render_upload
from ui_summary import render_summary
from ui_ask_ai import render_ask_ai
from ui_quiz import render_quiz
from ui_tasks import render_tasks
from ui_history import render_history


st.set_page_config(
    page_title="AI Study Assistant",
    page_icon=":books:",
    layout="wide",
    initial_sidebar_state="expanded",
)


GLOBAL_CSS = """
<style>
    /* ===== Modern Global Styles ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Headers */
    h1 {
        font-weight: 700 !important;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        font-weight: 600 !important;
        color: #1e293b !important;
    }

    h3 {
        font-weight: 600 !important;
        color: #334155 !important;
    }

    /* Cards */
    .stCard {
        border-radius: 16px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04) !important;
        transition: all 0.2s ease !important;
    }

    .stCard:hover {
        box-shadow: 0 10px 25px rgba(0,0,0,0.08), 0 4px 10px rgba(0,0,0,0.05) !important;
        transform: translateY(-1px);
    }

    /* Primary buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        padding: 0.5rem 1.25rem !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    }

    /* Secondary buttons */
    .stButton > button[kind="secondary"]:hover {
        border-color: #6366f1 !important;
        color: #6366f1 !important;
    }

    /* Danger buttons */
    .stButton > button[kind="secondary"]:has(+ div) {
        /* for delete buttons */
    }

    /* Expanders */
    .streamlit-expanderHeader {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* Info/Warning/Success/Error boxes */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.25rem;
    }

    [data-testid="stSidebar"] .stRadio label {
        padding: 0.75rem 1rem !important;
        border-radius: 10px !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(99, 102, 241, 0.08) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #f8fafc;
        border-radius: 12px;
        padding: 0.25rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: white;
        border-radius: 14px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }

    /* Spinner / AI loading animation */
    .ai-loading-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #ede9fe 0%, #fae8ff 100%);
        border-radius: 14px;
        border: 1px solid #d8b4fe;
        margin: 1rem 0;
    }

    @keyframes pulse-dot {
        0%, 100% { opacity: 0.2; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1.2); }
    }

    .ai-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #8b5cf6;
        display: inline-block;
        animation: pulse-dot 1.4s infinite ease-in-out;
    }
    .ai-dot:nth-child(2) { animation-delay: 0.2s; }
    .ai-dot:nth-child(3) { animation-delay: 0.4s; }

    /* File Tree (Finder-like) */
    .file-tree {
        background: #fafbfc;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        padding: 0.5rem;
        font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
        font-size: 0.875rem;
    }

    /* Quiz cards */
    .quiz-question-card {
        background: white;
        border-radius: 14px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #6366f1;
        transition: all 0.2s ease;
    }
    .quiz-question-card.correct {
        border-left-color: #22c55e;
        background: #f0fdf4;
    }
    .quiz-question-card.incorrect {
        border-left-color: #ef4444;
        background: #fef2f2;
    }

    /* Timer */
    .quiz-timer {
        font-size: 2rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        color: #6366f1;
        text-align: center;
        padding: 0.75rem;
        background: #f8fafc;
        border-radius: 12px;
    }
    .quiz-timer.warning {
        color: #f59e0b;
        animation: timer-pulse 0.5s ease-in-out infinite alternate;
    }
    .quiz-timer.danger {
        color: #ef4444;
        animation: timer-pulse 0.3s ease-in-out infinite alternate;
    }

    @keyframes timer-pulse {
        from { opacity: 1; }
        to { opacity: 0.5; }
    }

    /* Score display */
    .score-badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 1.1rem;
    }
    .score-excellent { background: #dcfce7; color: #166534; }
    .score-good { background: #dbeafe; color: #1e40af; }
    .score-fair { background: #fef3c7; color: #92400e; }
    .score-poor { background: #fee2e2; color: #991b1b; }

    /* Delete confirmation dialog */
    .confirm-overlay {
        background: rgba(0,0,0,0.5);
        position: fixed;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #a855f7) !important;
        border-radius: 999px !important;
    }

    /* File upload zone */
    [data-testid="stFileUploader"] {
        border-radius: 14px !important;
        border: 2px dashed #cbd5e1 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #8b5cf6 !important;
        background: #faf5ff !important;
    }

    /* ===== File Upload Cards (ChatGPT-style) ===== */
    .file-card {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .file-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }
    .file-card.loading {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-color: #f59e0b;
    }
    .file-card.success {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border-color: #22c55e;
    }

    .file-card-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    .file-card-icon.pdf { background: linear-gradient(135deg, #fee2e2, #fecaca); }
    .file-card-icon.docx { background: linear-gradient(135deg, #dbeafe, #bfdbfe); }
    .file-card-icon.xlsx { background: linear-gradient(135deg, #dcfce7, #bbf7d0); }
    .file-card-icon.pptx { background: linear-gradient(135deg, #fef3c7, #fde68a); }
    .file-card-icon.txt { background: linear-gradient(135deg, #f3f4f6, #e5e7eb); }

    .file-card-info {
        flex: 1;
        min-width: 0;
    }
    .file-card-name {
        font-weight: 600;
        font-size: 0.9rem;
        color: #1e293b;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 0.15rem;
    }
    .file-card-meta {
        font-size: 0.75rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .file-card-badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        background: #f1f5f9;
        color: #475569;
    }
    .file-card-badge.pdf { background: #fee2e2; color: #dc2626; }
    .file-card-badge.docx { background: #dbeafe; color: #2563eb; }
    .file-card-badge.xlsx { background: #dcfce7; color: #16a34a; }
    .file-card-badge.pptx { background: #fef3c7; color: #d97706; }

    .file-card-close {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        border: none;
        background: #f1f5f9;
        color: #64748b;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        transition: all 0.15s ease;
        flex-shrink: 0;
    }
    .file-card-close:hover {
        background: #ef4444;
        color: white;
    }

    /* Loading spinner for file cards */
    .file-card-spinner {
        width: 20px;
        height: 20px;
        border: 2px solid #f59e0b;
        border-top-color: transparent;
        border-radius: 50%;
        animation: file-spin 0.8s linear infinite;
    }
    @keyframes file-spin {
        to { transform: rotate(360deg); }
    }

    /* Progress bar inside file card */
    .file-card-progress {
        width: 100%;
        height: 4px;
        background: #e5e7eb;
        border-radius: 2px;
        overflow: hidden;
        margin-top: 0.25rem;
    }
    .file-card-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        border-radius: 2px;
        animation: file-progress-anim 1.5s ease-in-out infinite;
    }
    @keyframes file-progress-anim {
        0% { width: 0%; }
        50% { width: 70%; }
        100% { width: 100%; }
    }

    /* Folder dropdown selector */
    .folder-dropdown {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 1.25rem;
        background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
        border: 2px solid #8b5cf6;
        border-radius: 14px;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .folder-dropdown:hover {
        background: linear-gradient(135deg, #ddd6fe 0%, #c4b5fd 100%);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
    }
    .folder-dropdown-icon {
        font-size: 1.75rem;
    }
    .folder-dropdown-text {
        flex: 1;
    }
    .folder-dropdown-label {
        font-size: 0.8rem;
        color: #6b21a8;
        font-weight: 500;
    }
    .folder-dropdown-name {
        font-size: 1rem;
        font-weight: 700;
        color: #4c1d95;
    }
    .folder-dropdown-arrow {
        font-size: 1.25rem;
        color: #6b21a8;
    }

    /* File list container */
    .file-list-container {
        background: #f8fafc;
        border-radius: 14px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    .file-list-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.75rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .file-list-title {
        font-weight: 700;
        font-size: 0.95rem;
        color: #334155;
    }
    .file-list-count {
        font-size: 0.8rem;
        color: #64748b;
        background: #e2e8f0;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: 600;
    }
</style>
"""


def inject_css():
    """Inject global CSS styles."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def init_session_state():
    """Initialize all session state variables with OOP objects."""

    if "document" not in st.session_state:
        st.session_state["document"] = None

    if "ai_provider" not in st.session_state:
        api_key = get_api_key()
        try:
            if api_key:
                st.session_state["ai_provider"] = OpenAIProvider(api_key)
            else:
                st.session_state["ai_provider"] = None
        except Exception:
            st.session_state["ai_provider"] = None

    if "task_manager" not in st.session_state:
        st.session_state["task_manager"] = TaskManager()

    if "storage" not in st.session_state:
        st.session_state["storage"] = StorageManager()

    if "tasks_loaded" not in st.session_state:
        task_data = st.session_state["storage"].load_all().get("tasks", [])
        if task_data:
            st.session_state["task_manager"].load_from_list(task_data)
        st.session_state["tasks_loaded"] = True

    # Deletion confirmation state
    if "confirm_delete" not in st.session_state:
        st.session_state["confirm_delete"] = None


def render_sidebar():
    """Renders the sidebar with navigation and status indicators."""

    with st.sidebar:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
            <span style="font-size:2rem;">📚</span>
            <span style="font-size:1.3rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">AI Study Assistant</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        page = st.radio(
            "Navigate to:",
            [
                "🏠 Home",
                "📤 Upload Material",
                "📝 Summary",
                "💬 Ask AI",
                "🧠 Quiz Generator",
                "✅ Task Manager",
                "📋 Saved History",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")

        api_key = get_api_key()
        if api_key:
            st.success("🔑 API Key: Configured")
        else:
            st.error("🔑 API Key: Not set")
            st.caption("Add OPENAI_API_KEY to .env file")

        doc = st.session_state.get("document")
        if doc:
            file_count = ""
            if hasattr(doc, 'get_file_count'):
                file_count = f" | {doc.get_file_count()} files"
            st.info(f"📄 {doc.get_title()}{file_count}")
        else:
            st.caption("No document loaded")

        # Clean page name for routing
        page_clean = page.split(" ", 1)[1] if " " in page else page
        return page_clean


def main():
    """
    Main application entry point.
    Orchestrates the OOP model objects and routes to UI pages.
    """

    inject_css()
    init_session_state()

    page = render_sidebar()

    ai_provider = st.session_state.get("ai_provider")
    storage = st.session_state.get("storage")
    task_manager = st.session_state.get("task_manager")

    if page == "Home":
        render_home()

    elif page == "Upload Material":
        render_upload()

    elif page == "Summary":
        render_summary(ai_provider, storage)

    elif page == "Ask AI":
        render_ask_ai(ai_provider, storage)

    elif page == "Quiz Generator":
        render_quiz(ai_provider, storage)

    elif page == "Task Manager":
        render_tasks(task_manager, storage)

    elif page == "Saved History":
        render_history(storage)


if __name__ == "__main__":
    main()
