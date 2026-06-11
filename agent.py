"""
agent.py - AI Agent class hierarchy for AI Study Assistant.

Demonstrates OOP principles:
- INHERITANCE: SummaryAgent, QuizAgent, QuestionAnswerAgent, TaskGenerationAgent
  inherit from AIAgent.
- POLYMORPHISM: run() is overridden in each subclass.
- COMPOSITION: Each agent uses an AIProvider and a Document (has-a relationship).
"""

import json
from document import Document
from ai_provider import AIProvider


class AIAgent:
    """
    Parent class for all AI agents.
    Uses COMPOSITION: receives AIProvider and Document objects.
    Demonstrates: COMPOSITION, POLYMORPHISM (run() to be overridden).
    """

    def __init__(self, ai_provider: AIProvider, document: Document):
        self._ai_provider = ai_provider
        self._document = document

    def run(self, *args, **kwargs):
        """
        POLYMORPHISM: Base method to be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement run() method")


class SummaryAgent(AIAgent):
    """
    INHERITANCE: Inherits from AIAgent.
    Generates concise summaries of document content.
    """

    def run(self) -> str:
        """POLYMORPHISM: Generates a summary of the document content."""
        content = self._document.get_content()
        if not content:
            raise ValueError("No document content available to summarize.")

        prompt = (
            "Please provide a clear and concise summary of the following text. "
            "Organize the summary with bullet points for key ideas, and include "
            "a 'Key Takeaways' section at the end:\n\n"
            f"{content[:4000]}"
        )
        return self._ai_provider.generate_response(
            prompt=prompt,
            system_message="You are a helpful study assistant. Provide clear, well-structured summaries with markdown formatting."
        )


class QuizAgent(AIAgent):
    """
    INHERITANCE: Inherits from AIAgent.
    Generates multiple-choice quiz questions from document content.
    """

    def run(self, num_questions: int = 5) -> dict:
        """
        POLYMORPHISM: Generates multiple-choice quiz questions.
        Returns dict with 'questions' list containing:
        question, options (A-D), correct, explanation.
        """
        content = self._document.get_content()
        if not content:
            raise ValueError("No document content available to generate quiz.")

        prompt = (
            f"Based on the following text, create {num_questions} multiple-choice "
            "quiz questions to test deep understanding. Each question must have "
            "4 options (A, B, C, D), one correct answer letter, and a brief "
            "explanation of why the correct answer is right.\n\n"
            "Output ONLY a valid JSON array. Each item MUST have exactly these keys:\n"
            '- "question": the question text\n'
            '- "options": ["A) ...", "B) ...", "C) ...", "D) ..."]\n'
            '- "correct": the letter of the correct option (A/B/C/D)\n'
            '- "explanation": short explanation of the answer\n\n'
            f"Text:\n{content[:5000]}"
        )

        system_msg = (
            "You are an expert quiz generator. Always output a valid JSON array "
            "with 'question', 'options', 'correct', and 'explanation' keys for each item."
        )

        raw_response = self._ai_provider.generate_response(
            prompt=prompt,
            system_message=system_msg
        )

        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = "\n".join(lines)
            questions = json.loads(cleaned)
            if not isinstance(questions, list):
                questions = []
            validated = []
            for q in questions:
                if all(k in q for k in ("question", "options", "correct", "explanation")):
                    validated.append(q)
            return {"questions": validated, "raw_response": raw_response}
        except json.JSONDecodeError:
            return {"questions": [], "raw_response": raw_response}


class QuestionAnswerAgent(AIAgent):
    """
    INHERITANCE: Inherits from AIAgent.
    Answers user questions based on document content.
    """

    def run(self, question: str) -> str:
        """POLYMORPHISM: Answers a question using the document as context."""
        content = self._document.get_content()
        if not content:
            raise ValueError("No document content available to answer questions.")
        if not question or not question.strip():
            raise ValueError("Please provide a question.")

        prompt = (
            "Answer the following question based ONLY on the provided text. "
            "If the answer cannot be found in the text, say so clearly. "
            "Provide a detailed, well-structured answer with supporting evidence "
            "from the text when possible.\n\n"
            f"Text:\n{content[:4000]}\n\n"
            f"Question: {question}"
        )

        return self._ai_provider.generate_response(
            prompt=prompt,
            system_message=(
                "You are a helpful study assistant. Answer questions accurately "
                "based on the provided text. If unsure, be honest about it."
            )
        )


class TaskGenerationAgent(AIAgent):
    """
    INHERITANCE: Inherits from AIAgent.
    Analyzes document content and generates smart study tasks.
    """

    def run(self, num_tasks: int = 5) -> list:
        """
        POLYMORPHISM: Generates study tasks based on document content.
        Returns a list of task title strings.
        """
        content = self._document.get_content()
        if not content:
            raise ValueError("No document content available to generate tasks.")

        prompt = (
            f"Based on the following study material, suggest {num_tasks} specific, "
            "actionable study tasks that a student should complete to master this "
            "content. Tasks should be concrete and achievable (e.g., 'Create flashcards "
            "for key terms in Chapter 2', 'Write a one-page summary of the main theory', "
            "'Solve 5 practice problems on topic X').\n\n"
            "Output ONLY a JSON array of strings, each string being a task title. "
            "No other text, no markdown.\n\n"
            f"Text:\n{content[:4000]}"
        )

        system_msg = (
            "You are a study planner. Output ONLY a valid JSON array of task title strings."
        )

        raw_response = self._ai_provider.generate_response(
            prompt=prompt,
            system_message=system_msg
        )

        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = "\n".join(lines)
            tasks = json.loads(cleaned)
            if isinstance(tasks, list):
                return [t for t in tasks if isinstance(t, str) and t.strip()]
            return []
        except json.JSONDecodeError:
            return []
