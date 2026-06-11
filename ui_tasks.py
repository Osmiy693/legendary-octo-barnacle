"""
ui_tasks.py - Task Manager page for AI Study Assistant.
Features: CRUD tasks, AI-generated study tasks, deletion confirmation.
Uses TaskManager (composition of Task objects) and TaskGenerationAgent.
"""

import streamlit as st
from agent import TaskGenerationAgent
from ui_utils import render_ai_loading


def _render_delete_confirmation(task_index: int, task_title: str):
    """Render a deletion confirmation dialog for a task."""
    st.markdown("---")
    st.warning(f"⚠️ Are you sure you want to delete **\"{task_title}\"**?")
    col_confirm, col_cancel = st.columns(2)
    with col_confirm:
        if st.button("✅ Yes, Delete", key=f"confirm_del_{task_index}", type="primary", use_container_width=True):
            st.session_state["task_manager"].delete_task(task_index)
            st.session_state["storage"].save_tasks(st.session_state["task_manager"].to_list())
            st.session_state["confirm_delete"] = None
            st.success("Task deleted.")
            st.rerun()
    with col_cancel:
        if st.button("❌ Cancel", key=f"cancel_del_{task_index}", use_container_width=True):
            st.session_state["confirm_delete"] = None
            st.rerun()


def _render_ai_tasks_section(ai_provider):
    """Render AI-generated task suggestions section."""
    st.markdown("---")
    st.subheader("🤖 AI-Generated Study Tasks")

    doc = st.session_state.get("document")
    if doc is None:
        st.info("Upload study material first to get AI-generated task suggestions.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        num_ai_tasks = st.slider(
            "Number of AI-suggested tasks:",
            min_value=3,
            max_value=10,
            value=5,
            key="ai_task_count",
        )
    with col2:
        st.write("")
        generate_btn = st.button(
            "🧠 Generate Tasks",
            type="primary",
            use_container_width=True,
            key="generate_ai_tasks",
        )

    if generate_btn:
        if ai_provider is None:
            st.error("OpenAI API key is not configured. Set OPENAI_API_KEY in .env file.")
            return

        with st.spinner("Analyzing your material..."):
            render_ai_loading("AI is analyzing your content and generating study tasks...")
            try:
                agent = TaskGenerationAgent(ai_provider, doc)
                suggested_tasks = agent.run(num_ai_tasks)

                if suggested_tasks:
                    st.session_state["suggested_tasks"] = suggested_tasks
                    st.success(f"✅ AI generated {len(suggested_tasks)} task suggestions!")
                else:
                    st.warning("AI could not generate tasks. Try again.")
                    st.session_state["suggested_tasks"] = []
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

    # Show suggested tasks
    if "suggested_tasks" in st.session_state and st.session_state["suggested_tasks"]:
        st.markdown("**📋 Suggested Tasks — click to add:**")
        for i, task_title in enumerate(st.session_state["suggested_tasks"]):
            col_task, col_add = st.columns([5, 1])
            with col_task:
                st.markdown(f"{i + 1}. {task_title}")
            with col_add:
                if st.button("➕ Add", key=f"add_suggested_{i}", use_container_width=True):
                    try:
                        st.session_state["task_manager"].add_task(task_title)
                        st.session_state["storage"].save_tasks(
                            st.session_state["task_manager"].to_list()
                        )
                        st.session_state["suggested_tasks"].pop(i)
                        st.success("Task added!")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

        if st.button("➕ Add All Suggested Tasks", use_container_width=True):
            for task_title in list(st.session_state["suggested_tasks"]):
                try:
                    st.session_state["task_manager"].add_task(task_title)
                except ValueError:
                    pass
            st.session_state["storage"].save_tasks(
                st.session_state["task_manager"].to_list()
            )
            st.session_state["suggested_tasks"] = []
            st.success("All tasks added!")
            st.rerun()


def render_tasks(task_manager, storage):
    """
    Renders the Task Manager page with AI-generated tasks and deletion confirmation.
    """

    st.title("Task Manager")

    st.markdown("Manage your study tasks and get AI-powered task suggestions.")

    # --- Add New Task ---
    st.subheader("➕ Add New Task")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_task_title = st.text_input(
            "Task title:",
            placeholder="e.g., Review Chapter 3, Complete Assignment 2...",
            key="new_task_input",
            label_visibility="collapsed",
        )
    with col2:
        if st.button("Add Task", use_container_width=True):
            if new_task_title and new_task_title.strip():
                try:
                    task_manager.add_task(new_task_title)
                    storage.save_tasks(task_manager.to_list())
                    st.success("Task added!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
            else:
                st.error("Please enter a task title.")

    st.markdown("---")

    # --- Task List ---
    tasks = task_manager.get_tasks()

    if not tasks:
        st.info("📭 No tasks yet. Add a task above or use AI to generate suggestions.")
    else:
        st.subheader(f"📋 Your Tasks ({len(tasks)} total)")

        # Stats
        done_count = len(task_manager.get_done_tasks())
        pending_count = len(tasks) - done_count
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total", len(tasks))
        col_b.metric("✅ Done", done_count)
        col_c.metric("⏳ Pending", pending_count)

        # Progress bar
        if len(tasks) > 0:
            st.progress(done_count / len(tasks))

        st.markdown("---")

        # Task rows
        for i, task in enumerate(tasks):
            # Check if this task is pending deletion
            if st.session_state.get("confirm_delete") == i:
                _render_delete_confirmation(i, task.title)
                continue

            col1, col2, col3, col4, col5 = st.columns([4, 2, 1, 1, 1])

            with col1:
                if task.is_done():
                    st.markdown(f"~~{task.title}~~")
                else:
                    st.markdown(f"{task.title}")

            with col2:
                if task.status == "Done":
                    st.success("Done")
                elif task.status == "In Progress":
                    st.warning("In Progress")
                else:
                    st.info("Pending")

            with col3:
                if not task.is_done():
                    if st.button("▶️ Start", key=f"start_{i}", use_container_width=True):
                        task_manager.mark_task_in_progress(i)
                        storage.save_tasks(task_manager.to_list())
                        st.rerun()

            with col4:
                if not task.is_done():
                    if st.button("✅ Done", key=f"done_{i}", use_container_width=True):
                        task_manager.mark_task_done(i)
                        storage.save_tasks(task_manager.to_list())
                        st.rerun()

            with col5:
                if st.button("🗑", key=f"del_{i}", use_container_width=True, help="Delete task"):
                    st.session_state["confirm_delete"] = i
                    st.rerun()

        # Clear all with confirmation
        st.markdown("---")
        if st.session_state.get("confirm_delete") == "clear_all":
            st.warning("⚠️ Are you sure you want to delete ALL tasks? This cannot be undone.")
            col_yes, col_no, _ = st.columns([1, 1, 3])
            with col_yes:
                if st.button("✅ Yes, Clear All", type="primary", use_container_width=True):
                    for i in range(len(tasks) - 1, -1, -1):
                        task_manager.delete_task(i)
                    storage.save_tasks(task_manager.to_list())
                    st.session_state["confirm_delete"] = None
                    st.success("All tasks cleared!")
                    st.rerun()
            with col_no:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state["confirm_delete"] = None
                    st.rerun()
        else:
            if st.button("🗑 Clear All Tasks", type="secondary"):
                st.session_state["confirm_delete"] = "clear_all"
                st.rerun()

    # --- AI Task Generation ---
    ai_provider = st.session_state.get("ai_provider")
    _render_ai_tasks_section(ai_provider)
