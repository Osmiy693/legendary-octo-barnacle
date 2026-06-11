# AI Study Assistant & Course Project Manager

A Python Streamlit application that helps students learn more effectively by combining AI capabilities with smart study management tools. The project demonstrates **Object-Oriented Programming (OOP)** principles through a clean class hierarchy.

## Features

- **Upload Study Material** - Paste text or upload TXT/PDF files
- **AI Summaries** - Generate concise summaries of your study material
- **Ask AI Questions** - Get answers based on your uploaded content
- **Quiz Generator** - Create quiz questions with answers to test your knowledge
- **Task Manager** - Track study tasks and project milestones
- **Saved History** - Review all past summaries, quizzes, Q&A, and tasks
- **Local JSON Storage** - All data persisted locally

## Tech Stack

- Python 3.9+
- Streamlit (UI framework)
- OpenAI API (AI responses)
- python-dotenv (environment variables)
- pypdf (PDF text extraction)
- JSON (local storage)

## How to Run

### 1. Navigate to the project directory

```bash
cd ai_study_assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your OpenAI API key

Edit `.env` and replace `your_openai_api_key_here` with your actual key:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Run the application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Project Structure

```
ai_study_assistant/
|-- .env.example          # API key template
|-- .env                  # Your actual API key
|-- app.py                # Main Streamlit entry point + sidebar navigation
|-- config.py             # Loads environment variables
|-- document.py           # Document, TextDocument, PDFDocument classes
|-- ai_provider.py        # AIProvider, OpenAIProvider classes
|-- agent.py              # AIAgent, SummaryAgent, QuizAgent, QuestionAnswerAgent
|-- task.py               # Task, TaskManager classes
|-- storage.py            # StorageManager class (JSON persistence)
|-- ui_home.py            # Home page
|-- ui_upload.py          # Upload Material page
|-- ui_summary.py         # Summary generation page
|-- ui_ask_ai.py          # Ask AI questions page
|-- ui_quiz.py            # Quiz Generator page
|-- ui_tasks.py           # Task Manager page
|-- ui_history.py         # Saved History page
|-- requirements.txt      # Python dependencies
|-- README.md             # This file
|-- data/
    |-- history.json      # Local storage (auto-created)
```

## OOP Principles Demonstrated

### 1. Encapsulation

Encapsulation is used throughout the project to protect internal state:

- **Document**: `_title` and `_content` are protected attributes, accessed only through `get_title()` and `get_content()` getter methods.
- **AIProvider**: `_api_key` is a protected attribute, never exposed directly. The OpenAI client is created internally.
- **Task**: `_title`, `_status`, and `_created_at` are protected. Access is through `@property` decorators.
- **TaskManager**: `_tasks` list is protected; all modifications go through `add_task()`, `delete_task()`, and `mark_task_done()` methods.
- **StorageManager**: `_file_path` is protected; file I/O is handled entirely by internal methods.

### 2. Inheritance

Class hierarchies demonstrate inheritance:

- **Document Hierarchy**: `TextDocument` and `PDFDocument` both inherit from `Document`, sharing the same interface.
- **AIProvider Hierarchy**: `OpenAIProvider` inherits from `AIProvider`, reusing the `_api_key` storage pattern.
- **AIAgent Hierarchy**: `SummaryAgent`, `QuizAgent`, and `QuestionAnswerAgent` all inherit from `AIAgent`.

### 3. Polymorphism

Polymorphism enables flexible, interchangeable behavior:

- **Document.process()**: Called identically on `TextDocument` and `PDFDocument`, but each subclass has different logic.
- **AIProvider.generate_response()**: `OpenAIProvider` overrides to make API calls.
- **AIAgent.run()**: Each agent subclass overrides `run()` with different behavior (summarize, quiz, Q&A).

### 4. Composition

Objects are composed together:

- **AIAgent** is composed with an `AIProvider` and a `Document` (has-a relationships).
- **TaskManager** is composed of a collection of `Task` objects.

### 5. Abstraction

Base classes define interfaces:

- `Document.process()` raises `NotImplementedError`
- `AIProvider.generate_response()` raises `NotImplementedError`
- `AIAgent.run()` raises `NotImplementedError`

## Usage Flow

1. **Home** - Read about the app features
2. **Upload Material** - Paste text or upload a TXT/PDF file
3. **Summary** - Generate an AI summary
4. **Ask AI** - Ask questions about your content
5. **Quiz Generator** - Create quiz questions
6. **Task Manager** - Track study tasks
7. **Saved History** - Review all saved data

## Error Handling

The application includes comprehensive error handling for:

- Missing API key (shows warning in sidebar, disables AI features gracefully)
- Empty text input (validates before processing)
- Unsupported file types (rejects non-TXT/PDF files)
- OpenAI API errors (catches and displays friendly messages)
- PDF extraction failures (handles scanned/image-based PDFs)
- JSON decode errors in quiz generation (falls back to raw text)
