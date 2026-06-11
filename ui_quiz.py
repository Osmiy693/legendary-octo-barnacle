"""
ui_quiz.py - Interactive Quiz Test page for AI Study Assistant.
Features: timed test mode, multiple-choice, instant scoring, review mode.
Uses QuizAgent (inherits from AIAgent) to generate quiz questions.
"""

import streamlit as st
import time
from agent import QuizAgent
from ui_utils import render_ai_loading


def _get_score_class(pct: float) -> str:
    """Return CSS class for score badge."""
    if pct >= 80:
        return "score-excellent"
    elif pct >= 60:
        return "score-good"
    elif pct >= 40:
        return "score-fair"
    return "score-poor"


def _get_score_label(pct: float) -> str:
    """Return human-readable score label."""
    if pct >= 80:
        return "🏆 Excellent!"
    elif pct >= 60:
        return "👍 Good Job!"
    elif pct >= 40:
        return "📖 Keep Studying"
    return "💪 Needs Practice"


def render_quiz(ai_provider, storage):
    """
    Renders the Quiz Test page with interactive multiple-choice quiz.
    """

    st.title("Quiz Test")

    st.markdown(
        "Take an AI-generated multiple-choice test based on your study material. "
        "Timer, scoring, and review included."
    )

    doc = st.session_state.get("document")
    if doc is None:
        st.warning("⚠️ No document loaded. Please go to the **Upload Material** page first.")
        return

    st.info(f"**📄 Current Document:** {doc.get_title()} ({len(doc.get_content()):,} chars)")

    # --- Session state init ---
    if "quiz_started" not in st.session_state:
        st.session_state["quiz_started"] = False
    if "quiz_submitted" not in st.session_state:
        st.session_state["quiz_submitted"] = False
    if "quiz_questions" not in st.session_state:
        st.session_state["quiz_questions"] = []
    if "quiz_answers" not in st.session_state:
        st.session_state["quiz_answers"] = {}
    if "quiz_start_time" not in st.session_state:
        st.session_state["quiz_start_time"] = None
    if "quiz_time_limit" not in st.session_state:
        st.session_state["quiz_time_limit"] = 600  # 10 min default
    if "quiz_score" not in st.session_state:
        st.session_state["quiz_score"] = None

    # --- Setup: Generate Quiz ---
    if not st.session_state["quiz_started"] and not st.session_state["quiz_submitted"]:
        st.markdown("---")
        st.subheader("⚙️ Quiz Settings")

        col1, col2, col3 = st.columns(3)
        with col1:
            num_questions = st.selectbox(
                "Number of questions:",
                options=[3, 5, 7, 10],
                index=1,
            )
        with col2:
            time_minutes = st.selectbox(
                "Time limit:",
                options=[3, 5, 10, 15, 20],
                index=1,
                format_func=lambda x: f"{x} min",
            )
        with col3:
            st.write("")
            st.write("")
            generate_btn = st.button(
                "🚀 Start Quiz Test",
                type="primary",
                use_container_width=True,
            )

        if generate_btn:
            if ai_provider is None:
                st.error("OpenAI API key is not configured. Set OPENAI_API_KEY in .env file.")
                return

            with st.spinner("Generating quiz questions..."):
                render_ai_loading("AI is crafting your quiz questions...")
                try:
                    agent = QuizAgent(ai_provider, doc)
                    result = agent.run(num_questions)

                    if result["questions"]:
                        st.session_state["quiz_questions"] = result["questions"]
                        st.session_state["quiz_started"] = True
                        st.session_state["quiz_submitted"] = False
                        st.session_state["quiz_answers"] = {}
                        st.session_state["quiz_start_time"] = time.time()
                        st.session_state["quiz_time_limit"] = time_minutes * 60
                        st.session_state["quiz_score"] = None
                        st.rerun()
                    else:
                        st.error(
                            "Failed to generate quiz questions. The AI response "
                            "could not be parsed. Please try again."
                        )
                        with st.expander("🔍 Raw AI Response"):
                            st.text(result.get("raw_response", "No response"))
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")

    # --- Active Quiz ---
    elif st.session_state["quiz_started"] and not st.session_state["quiz_submitted"]:
        questions = st.session_state["quiz_questions"]

        # Timer — live JS countdown that runs without Streamlit interaction
        elapsed = time.time() - st.session_state["quiz_start_time"]
        remaining = max(0, st.session_state["quiz_time_limit"] - elapsed)

        # Auto-submit on time up (catches case where JS hasn't triggered yet)
        if remaining <= 0:
            st.session_state["quiz_submitted"] = True
            st.rerun()

        timer_id = f"quiz_timer_{int(st.session_state['quiz_start_time'])}"

        st.markdown(f"""
        <div id="{timer_id}" class="quiz-timer"
             data-remaining="{remaining:.1f}"
             data-submit-btn="submit_quiz_btn">⏱ --:--</div>
        <script>
        (function() {{
            var el = document.getElementById('{timer_id}');
            if (!el || el._timerRunning) return;
            el._timerRunning = true;

            var remaining = parseFloat(el.getAttribute('data-remaining'));
            var submitBtnId = el.getAttribute('data-submit-btn');

            function update() {{
                var mins = Math.floor(remaining / 60);
                var secs = Math.floor(remaining % 60);
                var disp = String(mins).padStart(2,'0') + ':' + String(secs).padStart(2,'0');
                el.textContent = '⏱ ' + disp;

                el.classList.remove('warning', 'danger');
                if (remaining <= 60) el.classList.add('danger');
                else if (remaining <= 180) el.classList.add('warning');

                if (remaining <= 0) {{
                    clearInterval(el._interval);
                    // Auto-click the submit button
                    var btns = parent.document.querySelectorAll('button');
                    for (var i = 0; i < btns.length; i++) {{
                        if (btns[i].textContent.includes('Submit Test') ||
                            btns[i].textContent.includes('📩')) {{
                            btns[i].click();
                            break;
                        }}
                    }}
                }}
            }}

            update();
            el._interval = setInterval(function() {{
                remaining -= 1;
                update();
            }}, 1000);
        }})();
        </script>
        """, unsafe_allow_html=True)

        # Progress
        answered = len(st.session_state["quiz_answers"])
        st.progress(answered / len(questions), f"Progress: {answered}/{len(questions)} answered")

        st.markdown("---")

        # Questions
        for i, q in enumerate(questions):
            q_num = i + 1
            st.markdown(f'<div class="quiz-question-card">', unsafe_allow_html=True)
            st.markdown(f"**Q{q_num}.** {q.get('question', 'N/A')}")

            options = q.get("options", [])
            if options:
                current_answer = st.session_state["quiz_answers"].get(i, None)
                idx_map = {}
                option_labels = []
                for opt in options:
                    if opt and len(opt) >= 3 and opt[2] == ")":
                        label = opt[0]
                    elif opt and len(opt) >= 2 and opt[1] == ")":
                        label = opt[0]
                    else:
                        label = chr(65 + len(option_labels))
                    idx_map[label] = opt
                    option_labels.append(f"{label}) {opt.split(')', 1)[-1].strip() if ')' in opt else opt}")

                default_idx = None
                if current_answer in idx_map:
                    keys_list = list(idx_map.keys())
                    if current_answer in keys_list:
                        default_idx = keys_list.index(current_answer)

                chosen = st.radio(
                    f"Select answer for Q{q_num}:",
                    options=list(idx_map.keys()),
                    format_func=lambda x: f"{x}) {idx_map[x].split(')', 1)[-1].strip() if ')' in idx_map[x] else idx_map[x]}",
                    key=f"quiz_q_{i}",
                    index=default_idx if default_idx is not None and default_idx < len(idx_map) else None,
                    label_visibility="collapsed",
                )

                if chosen:
                    st.session_state["quiz_answers"][i] = chosen

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        col_a, col_b = st.columns([1, 2])
        with col_a:
            if st.button("📩 Submit Test", type="primary", use_container_width=True):
                st.session_state["quiz_submitted"] = True
                st.rerun()
        with col_b:
            unanswered = len(questions) - len(st.session_state["quiz_answers"])
            if unanswered > 0:
                st.warning(f"⚠️ {unanswered} question(s) unanswered")

    # --- Results ---
    elif st.session_state["quiz_submitted"]:
        questions = st.session_state["quiz_questions"]
        user_answers = st.session_state["quiz_answers"]

        # Calculate score
        correct_count = 0
        results = []
        for i, q in enumerate(questions):
            user_ans = user_answers.get(i, None)
            correct_ans = q.get("correct", "").strip().upper()
            is_correct = (user_ans == correct_ans) if user_ans else False
            if is_correct:
                correct_count += 1
            results.append({
                "question": q,
                "user_answer": user_ans,
                "is_correct": is_correct,
                "correct_answer": correct_ans,
            })

        total = len(questions)
        pct = (correct_count / total * 100) if total > 0 else 0
        st.session_state["quiz_score"] = {"correct": correct_count, "total": total, "pct": pct}

        # Score header
        st.markdown("---")
        st.subheader("📊 Test Results")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric("Score", f"{correct_count}/{total}")
        with col2:
            st.metric("Percentage", f"{pct:.0f}%")
        with col3:
            elapsed_total = time.time() - st.session_state.get("quiz_start_time", time.time())
            mins_taken = int(elapsed_total // 60)
            secs_taken = int(elapsed_total % 60)
            st.metric("Time Taken", f"{mins_taken}m {secs_taken}s")

        st.markdown(
            f'<span class="score-badge {_get_score_class(pct)}">{_get_score_label(pct)}</span>',
            unsafe_allow_html=True,
        )

        # Progress bar
        st.progress(pct / 100)

        # Save to history
        storage.save_quiz(
            doc.get_title(),
            {
                "score": f"{correct_count}/{total} ({pct:.0f}%)",
                "questions": [
                    {**q, "user_answer": r["user_answer"], "is_correct": r["is_correct"]}
                    for q, r in zip(questions, results)
                ],
            }
        )

        st.markdown("---")
        st.subheader("📝 Review Answers")

        for i, r in enumerate(results):
            q = r["question"]
            card_class = "correct" if r["is_correct"] else "incorrect"
            status_icon = "✅" if r["is_correct"] else "❌"

            st.markdown(f'<div class="quiz-question-card {card_class}">', unsafe_allow_html=True)
            st.markdown(f"**Q{i + 1}.** {q.get('question', 'N/A')}")

            options = q.get("options", [])
            correct_letter = r["correct_answer"]
            user_letter = r["user_answer"]

            for opt in options:
                if opt and ")" in opt:
                    letter = opt.split(")")[0].strip()
                else:
                    letter = "?"

                if letter == correct_letter:
                    st.markdown(f"🟢 **{opt}** ← Correct Answer")
                elif letter == user_letter:
                    st.markdown(f"🔴 **{opt}** ← Your Answer")
                else:
                    st.markdown(f"⚪ {opt}")

            explanation = q.get("explanation", "")
            if explanation:
                st.caption(f"💡 {explanation}")

            if not r["user_answer"]:
                st.caption("⚠️ You did not answer this question.")

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        col_reset, _ = st.columns([1, 3])
        with col_reset:
            if st.button("🔄 Take Another Quiz", type="primary", use_container_width=True):
                st.session_state["quiz_started"] = False
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_questions"] = []
                st.session_state["quiz_answers"] = {}
                st.session_state["quiz_start_time"] = None
                st.session_state["quiz_score"] = None
                st.rerun()
