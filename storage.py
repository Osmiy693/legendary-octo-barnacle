"""
storage.py - StorageManager class for AI Study Assistant.

Demonstrates OOP principles:
- ENCAPSULATION: _file_path and _data are protected.
- Single Responsibility: StorageManager handles only persistence logic.
"""

import json
import os
from datetime import datetime


class StorageManager:
    """
    Manages persistent storage of all application data using JSON.
    ENCAPSULATION: Internal file path and data are protected.
    """

    def __init__(self, file_path: str = "data/history.json"):
        self._file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensures the data directory and JSON file exist."""
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        if not os.path.exists(self._file_path):
            self._write_data(self._get_empty_data())

    def _get_empty_data(self) -> dict:
        """Returns the default empty data structure."""
        return {
            "summaries": [],
            "quizzes": [],
            "qa_history": [],
            "tasks": [],
        }

    def _read_data(self) -> dict:
        """Reads all data from the JSON file."""
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                default = self._get_empty_data()
                for key in default:
                    if key not in data:
                        data[key] = default[key]
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return self._get_empty_data()

    def _write_data(self, data: dict) -> None:
        """Writes data to the JSON file."""
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_summary(self, title: str, content: str) -> None:
        """Saves a generated summary to history."""
        data = self._read_data()
        data["summaries"].append({
            "title": title,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        self._write_data(data)

    def save_quiz(self, title: str, questions) -> None:
        """Saves a generated quiz (list or dict with score+questions) to history."""
        data = self._read_data()
        data["quizzes"].append({
            "title": title,
            "questions": questions,
            "timestamp": datetime.now().isoformat(),
        })
        self._write_data(data)

    def save_qa(self, title: str, question: str, answer: str) -> None:
        """Saves a Q&A interaction to history."""
        data = self._read_data()
        data["qa_history"].append({
            "title": title,
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat(),
        })
        self._write_data(data)

    def save_tasks(self, tasks: list) -> None:
        """Saves task list to persistent storage."""
        data = self._read_data()
        data["tasks"] = tasks
        self._write_data(data)

    def load_all(self) -> dict:
        """Loads all saved history data."""
        return self._read_data()

    def clear_all(self) -> None:
        """Clears all saved history."""
        self._write_data(self._get_empty_data())
