"""
ui_home.py - Home page for AI Study Assistant.
Modern dashboard with feature overview and quick stats.
"""

import streamlit as st


def render_home():
    """Renders the Home page with modern dashboard design."""

    st.title("AI Study Assistant")

    st.markdown(
        "<p style='font-size:1.15rem;color:#64748b;margin-bottom:1.5rem;'>"
        "Your intelligent study companion — upload materials, get AI summaries, "
        "take interactive quizzes, and manage your learning journey.</p>",
        unsafe_allow_html=True,
    )

    # --- Quick Stats Row ---
    doc = st.session_state.get("document")
    tasks = st.session_state.get("task_manager")
    storage = st.session_state.get("storage")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        doc_status = "📄 Loaded" if doc else "📭 None"
        st.metric("Document", doc_status)

    with col2:
        task_count = len(tasks.get_tasks()) if tasks else 0
        st.metric("Tasks", str(task_count))

    with col3:
        done = len(tasks.get_done_tasks()) if tasks else 0
        st.metric("Completed", str(done))

    with col4:
        data = storage.load_all() if storage else {}
        history_count = (
            len(data.get("summaries", []))
            + len(data.get("quizzes", []))
            + len(data.get("qa_history", []))
        )
        st.metric("Saved Items", str(history_count))

    st.markdown("---")

    # --- Feature Cards ---
    st.subheader("✨ Features")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 🧠 AI-Powered Learning")
        with st.container():
            st.markdown("""
            <div style="background:white;border-radius:14px;padding:1.25rem;border:1px solid #e2e8f0;margin-bottom:1rem;">
                <h4 style="margin:0 0 0.5rem 0;">📤 Upload Material</h4>
                <p style="color:#64748b;margin:0;">Paste text, upload TXT/PDF files, or drop entire folders. Supports multi-file with Finder-like browsing.</p>
            </div>
            <div style="background:white;border-radius:14px;padding:1.25rem;border:1px solid #e2e8f0;margin-bottom:1rem;">
                <h4 style="margin:0 0 0.5rem 0;">📝 AI Summaries</h4>
                <p style="color:#64748b;margin:0;">Get instant, well-structured summaries with key takeaways extracted by AI.</p>
            </div>
            <div style="background:white;border-radius:14px;padding:1.25rem;border:1px solid #e2e8f0;margin-bottom:1rem;">
                <h4 style="margin:0 0 0.5rem 0;">💬 Ask AI</h4>
                <p style="color:#64748b;margin:0;">Chat with AI about your materials — ask questions and get answers grounded in your content.</p>
            </div>
            """, unsafe_allow_html=True)

    with col_b:
        st.markdown("### ⚡ Study Tools")
        with st.container():
            st.markdown("""
            <div style="background:white;border-radius:14px;padding:1.25rem;border:1px solid #e2e8f0;margin-bottom:1rem;">
                <h4 style="margin:0 0 0.5rem 0;">🧠 Interactive Quiz Tests</h4>
                <p style="color:#64748b;margin:0;">Take timed multiple-choice tests with instant scoring, progress tracking, and answer review.</p>
            </div>
            <div style="background:white;border-radius:14px;padding:1.25rem;border:1px solid #e2e8f0;margin-bottom:1rem;">
                <h4 style="margin:0 0 0.5rem 0;">✅ Smart Task Manager</h4>
                <p style="color:#64748b;margin:0;">Track study tasks with statuses and get AI-generated task suggestions based on your materials.</p>
            </div>
            <div style="background:white;border-radius:14px;padding:1.25rem;border:1px solid #e2e8f0;margin-bottom:1rem;">
                <h4 style="margin:0 0 0.5rem 0;">📋 Saved History</h4>
                <p style="color:#64748b;margin:0;">All summaries, quizzes, and Q&A automatically saved locally for future review.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Getting Started ---
    st.subheader("🚀 Getting Started")

    steps = [
        ("1", "Set API Key", "Add your OPENAI_API_KEY to the .env file"),
        ("2", "Upload Material", "Go to Upload Material and add your study content"),
        ("3", "Explore AI Features", "Generate summaries, take quizzes, or ask questions"),
        ("4", "Manage Tasks", "Use the Task Manager with AI-suggested study tasks"),
        ("5", "Review Progress", "Check Saved History for past summaries and quiz results"),
    ]

    cols = st.columns(len(steps))
    for i, (num, title, desc) in enumerate(steps):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align:center;padding:1rem;">
                <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;">{num}</div>
                <h4 style="margin:0.25rem 0;">{title}</h4>
                <p style="color:#94a3b8;font-size:0.85rem;margin:0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
