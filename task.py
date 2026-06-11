"""
task.py - Task and TaskManager classes for AI Study Assistant.

Demonstrates OOP principles:
- ENCAPSULATION: Task has protected _title, _status, _created_at attributes.
- COMPOSITION: TaskManager contains a list of Task objects.
"""

from datetime import datetime


class Task:
    """
    Represents a single study project task.
    ENCAPSULATION: Internal attributes are protected, accessed via methods.
    """

    VALID_STATUSES = ("Pending", "In Progress", "Done")

    def __init__(self, title: str, status: str = "Pending"):
        self._title = title
        self._created_at = datetime.now().isoformat()
        if status not in self.VALID_STATUSES:
            self._status = "Pending"
        else:
            self._status = status

    @property
    def title(self) -> str:
        return self._title

    @property
    def status(self) -> str:
        return self._status

    @property
    def created_at(self) -> str:
        return self._created_at

    def mark_done(self) -> None:
        self._status = "Done"

    def mark_in_progress(self) -> None:
        self._status = "In Progress"

    def is_done(self) -> bool:
        return self._status == "Done"

    def to_dict(self) -> dict:
        return {
            "title": self._title,
            "status": self._status,
            "created_at": self._created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        task = cls(title=data["title"], status=data["status"])
        task._created_at = data.get("created_at", task._created_at)
        return task

    def __repr__(self) -> str:
        return f"Task(title='{self._title}', status='{self._status}')"


class TaskManager:
    """
    Manages a collection of Task objects.
    COMPOSITION: TaskManager has-a list of Tasks.
    """

    def __init__(self):
        self._tasks = []

    def add_task(self, title: str) -> Task:
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty.")
        task = Task(title=title.strip())
        self._tasks.append(task)
        return task

    def delete_task(self, index: int) -> None:
        if 0 <= index < len(self._tasks):
            self._tasks.pop(index)
        else:
            raise IndexError(f"Invalid task index: {index}")

    def mark_task_done(self, index: int) -> None:
        if 0 <= index < len(self._tasks):
            self._tasks[index].mark_done()
        else:
            raise IndexError(f"Invalid task index: {index}")

    def mark_task_in_progress(self, index: int) -> None:
        if 0 <= index < len(self._tasks):
            self._tasks[index].mark_in_progress()
        else:
            raise IndexError(f"Invalid task index: {index}")

    def get_tasks(self) -> list:
        return self._tasks

    def get_pending_tasks(self) -> list:
        return [t for t in self._tasks if t.status != "Done"]

    def get_done_tasks(self) -> list:
        return [t for t in self._tasks if t.is_done()]

    def to_list(self) -> list:
        return [task.to_dict() for task in self._tasks]

    def load_from_list(self, data: list) -> None:
        self._tasks = [Task.from_dict(item) for item in data]

    def __len__(self) -> int:
        return len(self._tasks)
