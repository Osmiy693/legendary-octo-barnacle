"""
ui_history.py - Saved History page for AI Study Assistant.
Loads and displays all previously saved data with deletion confirmation.
"""

import streamlit as st


def render_history(storage):
    """
    Renders the Saved History page with tabbed view and clear confirmation.
    """

    st.title("Saved History")

    st.markdown("Review your saved summaries, quiz results, Q&A, and tasks.")

    data = storage.load_all()

    # Init confirmation state
    if "confirm_clear_history" not in st.session_state:
        st.session_state["confirm_clear_history"] = False

    tab1, tab2, tab3, tab4 = st.tabs([
        f"📝 Summaries ({len(data.get('summaries', []))})",
        f"🧠 Quizzes ({len(data.get('quizzes', []))})",
        f"💬 Q&A ({len(data.get('qa_history', []))})",
        f"✅ Tasks ({len(data.get('tasks', []))})",
    ])

    # --- Summaries Tab ---
    with tab1:
        st.subheader("Saved Summaries")
        summaries = data.get("summaries", [])
        if not summaries:
            st.info("No summaries saved yet. Generate one from the Summary page.")
        else:
            for i, s in enumerate(reversed(summaries), 1):
                with st.expander(f"{i}. {s.get('title', 'Untitled')} — {s.get('timestamp', '')[:10]}"):
                    st.markdown(s.get("content", "No content"))

    # --- Quizzes Tab ---
    with tab2:
        st.subheader("Saved Quiz Results")
        quizzes = data.get("quizzes", [])
        if not quizzes:
            st.info("No quizzes saved yet. Take a quiz from the Quiz Generator page.")
        else:
            for i, q in enumerate(reversed(quizzes), 1):
                title = q.get("title", "Untitled")
                ts = q.get("timestamp", "")[:10]
                questions = q.get("questions", [])

                label = f"{i}. {title} — {ts}"
                if isinstance(questions, dict) and "score" in questions:
                    label += f" | Score: {questions['score']}"
                elif isinstance(questions, list):
                    label += f" | {len(questions)} questions"

                with st.expander(label):
                    if isinstance(questions, dict):
                        st.markdown(f"**Score:** {questions.get('score', 'N/A')}")
                        qs = questions.get("questions", [])
                        for j, q_item in enumerate(qs, 1):
                            user_ans = q_item.get("user_answer", "—")
                            is_correct = q_item.get("is_correct", False)
                            icon = "✅" if is_correct else "❌"
                            st.markdown(f"{icon} **Q{j}.** {q_item.get('question', 'N/A')}")
                            st.caption(f"Your answer: {user_ans} | Correct: {q_item.get('correct', 'N/A')}")
                            st.markdown("---")
                    elif isinstance(questions, list):
                        for j, q_item in enumerate(questions, 1):
                            st.markdown(f"**Q{j}.** {q_item.get('question', 'N/A')}")
                            st.markdown(f"*A:* {q_item.get('answer', 'N/A')}")
                            st.markdown("---")
                    elif isinstance(questions, str):
                        st.text(questions)

    # --- Q&A Tab ---
    with tab3:
        st.subheader("Saved Q&A")
        qa_history = data.get("qa_history", [])
        if not qa_history:
            st.info("No Q&A saved yet. Ask a question from the Ask AI page.")
        else:
            for i, item in enumerate(reversed(qa_history), 1):
                with st.expander(f"{i}. {item.get('title', 'Untitled')} — {item.get('timestamp', '')[:10]}"):
                    st.markdown(f"**❓ Q:** {item.get('question', 'N/A')}")
                    st.markdown(f"**💡 A:** {item.get('answer', 'N/A')}")

    # --- Tasks Tab ---
    with tab4:
        st.subheader("Saved Tasks")
        tasks = data.get("tasks", [])
        if not tasks:
            st.info("No tasks saved yet. Add tasks from the Task Manager page.")
        else:
            done_count = sum(1 for t in tasks if t.get("status") == "Done")
            pending_count = len(tasks) - done_count

            col_a, col_b = st.columns(2)
            col_a.metric("✅ Done", done_count)
            col_b.metric("⏳ Pending", pending_count)

            st.markdown("---")
            for task in tasks:
                status = task.get("status", "Unknown")
                title = task.get("title", "Untitled")
                created = task.get("created_at", "")[:10]
                if status == "Done":
                    st.markdown(f"✅ ~~{title}~~ — *{created}*")
                elif status == "In Progress":
                    st.markdown(f"🔄 {title} — *In Progress · {created}*")
                else:
                    st.markdown(f"⏳ {title} — *Pending · {created}*")

    # --- Clear All with Confirmation ---
    st.markdown("---")

    if st.session_state.get("confirm_clear_history"):
        st.warning("⚠️ Are you sure you want to delete ALL saved history? This cannot be undone.")
        col_yes, col_no, _ = st.columns([1, 1, 3])
        with col_yes:
            if st.button("✅ Yes, Clear Everything", type="primary", use_container_width=True):
                storage.clear_all()
                st.session_state["confirm_clear_history"] = False
                st.success("All history cleared!")
                st.rerun()
        with col_no:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state["confirm_clear_history"] = False
                st.rerun()
    else:
        has_data = any(len(data.get(k, [])) > 0 for k in ["summaries", "quizzes", "qa_history", "tasks"])
        if has_data:
            if st.button("🗑 Clear All History", type="secondary"):
                st.session_state["confirm_clear_history"] = True
                st.rerun()
