"""
ui_ask_ai.py - Ask AI page for AI Study Assistant.
Uses QuestionAnswerAgent (inherits from AIAgent) to answer user questions.
"""

import streamlit as st
from agent import QuestionAnswerAgent
from ui_utils import render_ai_loading


def render_ask_ai(ai_provider, storage):
    """
    Renders the Ask AI page with chat-like Q&A interface.
    """

    st.title("Ask AI")

    st.markdown(
        "Ask questions about your uploaded study material and get AI-powered "
        "answers grounded in your content."
    )

    doc = st.session_state.get("document")
    if doc is None:
        st.warning("⚠️ No document loaded. Please go to the **Upload Material** page first.")
        return

    st.info(f"**📄 Current Document:** {doc.get_title()} ({len(doc.get_content()):,} chars)")

    # Input with send button
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        question = st.text_input(
            "Your question:",
            placeholder="e.g., What are the main concepts discussed in this material?",
            label_visibility="collapsed",
            key="ask_ai_input",
        )
    with col_btn:
        ask_btn = st.button("💬 Ask", type="primary", use_container_width=True)

    if ask_btn:
        if ai_provider is None:
            st.error("OpenAI API key is not configured. Please set OPENAI_API_KEY in .env file.")
            return

        if not question or not question.strip():
            st.error("Please enter a question.")
            return

        with st.spinner("Thinking..."):
            render_ai_loading("AI is analyzing your question against the material...")
            try:
                agent = QuestionAnswerAgent(ai_provider, doc)
                answer = agent.run(question)

                if "qa_pairs" not in st.session_state:
                    st.session_state["qa_pairs"] = []
                st.session_state["qa_pairs"].append({
                    "question": question,
                    "answer": answer
                })

                storage.save_qa(doc.get_title(), question, answer)
                st.success("✅ Answer generated and saved!")

            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

    # Q&A History
    if "qa_pairs" in st.session_state and st.session_state["qa_pairs"]:
        st.markdown("---")
        st.subheader("💬 Q&A History")

        if st.button("🗑 Clear Chat History", type="secondary"):
            st.session_state.pop("qa_pairs", None)
            st.rerun()

        for i, pair in enumerate(reversed(st.session_state["qa_pairs"]), 1):
            with st.expander(f"Q{i}: {pair['question'][:100]}{'...' if len(pair['question']) > 100 else ''}"):
                st.markdown("**❓ Question:**")
                st.markdown(pair["question"])
                st.markdown("**💡 Answer:**")
                st.markdown(f"""
                <div style="background:#f8fafc;border-radius:10px;padding:1rem;border:1px solid #e2e8f0;margin:0.5rem 0;">
                    {pair["answer"]}
                </div>
                """, unsafe_allow_html=True)
