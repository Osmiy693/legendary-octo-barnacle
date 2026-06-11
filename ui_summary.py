"""
ui_summary.py - Summary generation page for AI Study Assistant.
Uses SummaryAgent (inherits from AIAgent) to generate AI summaries.
"""

import streamlit as st
from agent import SummaryAgent
from ui_utils import render_ai_loading


def render_summary(ai_provider, storage):
    """
    Renders the Summary page with AI-powered summary generation.
    """

    st.title("AI Summary")

    st.markdown(
        "Generate a comprehensive AI summary of your uploaded study material "
        "with key takeaways and structured breakdown."
    )

    doc = st.session_state.get("document")
    if doc is None:
        st.warning("⚠️ No document loaded. Please go to the **Upload Material** page first.")
        return

    st.info(f"**📄 Current Document:** {doc.get_title()} ({len(doc.get_content()):,} chars)")

    if st.button("✨ Generate Summary", type="primary"):
        if ai_provider is None:
            st.error("OpenAI API key is not configured. Please set OPENAI_API_KEY in .env file.")
            return

        with st.spinner("Generating summary..."):
            render_ai_loading("AI is reading your material and crafting a summary...")
            try:
                agent = SummaryAgent(ai_provider, doc)
                summary = agent.run()

                st.session_state["last_summary"] = summary
                storage.save_summary(doc.get_title(), summary)
                st.success("✅ Summary generated and saved to history!")

            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

    if "last_summary" in st.session_state and st.session_state["last_summary"]:
        st.markdown("---")
        st.subheader("📝 Generated Summary")

        # Display in a nice card
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:1.5rem;border:1px solid #e2e8f0;margin:1rem 0;">
            {st.session_state["last_summary"]}
        </div>
        """, unsafe_allow_html=True)

        # Copy button
        st.button("📋 Copy Summary", use_container_width=True, help="Select and copy the text above")

        # Regenerate option
        if st.button("🔄 Regenerate Summary", type="secondary"):
            st.session_state.pop("last_summary", None)
            st.rerun()
