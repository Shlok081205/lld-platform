# LLD Practice Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)](https://djangoproject.com)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-1.5_Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

The **LLD Practice Platform** is an interactive web application that helps software engineering learners practice Low-Level Design (LLD) problems and receive automated, structured feedback. Unlike competitive programming judges that only validate output, this platform evaluates *how well you think about design* — your class hierarchies, design patterns, SOLID principles, and code organization — in addition to whether your code passes functional tests.

The evaluation pipeline is hybrid: submitted Python code is executed in a sandboxed environment and scored against deterministic unit tests (40 points), while the accompanying design document is analyzed by Google's **Gemini 1.5 Flash** model against a structured rubric of 7 design criteria (60 points). The combined score out of 100 is displayed with per-criterion breakdowns, evidence snippets, concerns flagged, and improvement suggestions — all from a single submission.

The platform is intentionally minimal-dependency and self-hostable. It runs on SQLite (no external database required), uses Django's built-in authentication, and requires only a Gemini API key to operate. This makes it easy to evaluate, extend, and deploy for an engineering assignment context.

---

## Features

- **5 curated LLD problems** across Easy, Medium, and Hard difficulties
- **Dual submission format** — text design document + Python code editor (CodeMirror)
- **AI-powered design evaluation** via Gemini 1.5 Flash with a structured 7-criterion rubric
- **Deterministic code testing** — each problem ships with hidden test cases
- **Per-criterion rubric breakdown** with evidence, concerns, and improvement suggestions
- **Attempt history** with score tracking and problem-level filtering
- **User authentication** — register, login, logout
- **Clean Bootstrap 5 UI** with dark navigation, responsive cards, and CodeMirror Python editor
- **Security sandbox** — code executed with subprocess isolation, timeout guards, and forbidden import filters
- **Re-submission loop** — attempt any problem multiple times to track and improve design quality

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 4.2 |
| Language | Python 3.11+ |
| Database | SQLite 3 (via Django ORM) |
| AI Evaluation | Google Gemini 1.5 Flash API |
| Frontend | Bootstrap 5.3, Bootstrap Icons |
| Code Editor | CodeMirror 5 (Python mode, Dracula theme) |
| Testing | pytest, pytest-django |
| Auth | Django built-in auth |
| Environment | python-dotenv |

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/lld-platform.git
cd lld-platform
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True
GEMINI_API_KEY=your-gemini-api-key-here
ALLOWED_HOSTS=127.0.0.1,localhost
```

> **Get a Gemini API key**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey) and create a free key.

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Load the 5 LLD problems

```bash
python manage.py loaddata problems/fixtures/problems.json
```

### 7. (Optional) Create a superuser

```bash
python manage.py createsuperuser
```

### 8. Start the development server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/problems/](http://127.0.0.1:8000/problems/) to start practicing.

---

## Project Structure

```
lld-platform/
├── lld_platform/               # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── problems/                   # Problem management app
│   ├── models.py               # Problem, Tag models
│   ├── views.py                # List + Detail views
│   ├── urls.py
│   ├── fixtures/
│   │   └── problems.json       # 5 seeded LLD problems
│   └── tests/
│       ├── test_parking_lot.py
│       ├── test_library_system.py
│       ├── test_vending_machine.py
│       ├── test_elevator.py
│       └── test_chess_game.py
│
├── attempts/                   # Submission + evaluation app
│   ├── models.py               # Attempt, RubricResult models
│   ├── views.py                # Submit, Result, History views
│   ├── urls.py
│   ├── evaluator/
│   │   ├── code_runner.py      # Sandboxed code execution
│   │   ├── ai_evaluator.py     # Gemini rubric evaluation
│   │   └── pipeline.py         # Orchestrates both evaluators
│   └── rubric.py               # 7 rubric criteria definitions
│
├── templates/
│   ├── base.html               # Bootstrap 5 base layout
│   ├── problems/
│   │   ├── list.html           # Problem grid with filters
│   │   └── detail.html         # Problem detail + sidebar
│   ├── attempts/
│   │   ├── submit.html         # Dual-panel submission form
│   │   ├── result.html         # Score + rubric breakdown
│   │   └── history.html        # Attempt history table
│   └── registration/
│       ├── login.html          # Centered login card
│       └── register.html       # Registration card
│
├── docs/
│   ├── research_note.md        # Learner problem + tool survey
│   └── design_note.md          # MVP design decisions
│
├── AI_USAGE.md                 # AI usage documentation
├── README.md
├── requirements.txt
└── manage.py
```

---

## How It Works

### The Evaluation Pipeline

```
User Submission
     │
     ├── Design Document (text)
     │        │
     │        └──► Gemini 1.5 Flash
     │                   │
     │             Structured JSON rubric
     │             (7 criteria × max pts)
     │                   │
     │             design_score / 60
     │
     └── Python Code
              │
              └──► Sandboxed Execution
                         │
                   pytest test suite
                   (problem-specific)
                         │
                   tests_passed / tests_total
                         │
                   code_score / 40
     │
     └──► overall_score = code_score + design_score
                 │
          Stored in Attempt model
                 │
          Result page rendered
```

1. **Submission received** → `SubmitAttemptView` creates an `Attempt` record with status `pending`
2. **Code execution** → `code_runner.py` runs the submitted Python in a restricted `exec()` environment with a 10-second timeout, then imports and runs the problem's pytest tests against the user's classes
3. **AI evaluation** → `ai_evaluator.py` constructs a structured prompt embedding the design document and problem context, calls Gemini, and parses the JSON response into `RubricResult` rows
4. **Score aggregation** → `pipeline.py` combines both scores, updates the `Attempt` record to `completed`, and redirects to the result page

---

## Scoring Breakdown

| Component | Weight | Evaluated By |
|---|---|---|
| Code Tests | 40 pts | pytest (deterministic) |
| Class Design | ~12 pts | Gemini AI |
| SOLID Principles | ~10 pts | Gemini AI |
| Design Patterns | ~10 pts | Gemini AI |
| Abstraction Quality | ~8 pts | Gemini AI |
| Encapsulation | ~8 pts | Gemini AI |
| Extensibility | ~7 pts | Gemini AI |
| Naming & Clarity | ~5 pts | Gemini AI |
| **Total** | **100 pts** | |

**Grade bands:**
- 🟢 ≥ 70 — Excellent
- 🟡 50–69 — Needs Improvement  
- 🔴 < 50 — Needs Work

---

## The 5 LLD Problems

| # | Problem | Difficulty | Key Concepts |
|---|---|---|---|
| 1 | Parking Lot System | 🟢 Easy | OOP basics, state management |
| 2 | Library Management System | 🟡 Medium | Associations, borrowing logic |
| 3 | Vending Machine | 🟡 Medium | State pattern, transaction flow |
| 4 | Elevator System | 🔴 Hard | Scheduling, observer pattern |
| 5 | Chess Game | 🔴 Hard | Polymorphism, move validation |

---

## Running Tests

```bash
# Run all problem test suites
pytest problems/tests/ -v

# Run a single problem's tests
pytest problems/tests/test_parking_lot.py -v

# Run with coverage
pip install pytest-cov
pytest --cov=problems --cov-report=term-missing
```

---

## Limitations and Future Work

**Current Limitations:**
- Code execution uses `exec()` with restricted builtins — not a true container sandbox; should use Docker for production
- Gemini API calls are synchronous; large submissions may feel slow (~10–15s)
- No rate limiting on submissions (can be abused in a shared deployment)
- SQLite is not suitable for concurrent multi-user production deployment

**Future Work:**
- [ ] Async evaluation via Celery + Redis (show progress indicator)
- [ ] Docker-based code sandbox (gVisor or nsjail)
- [ ] Leaderboard per problem with anonymized scores
- [ ] Diagram submission support (draw.io XML or PlantUML text)
- [ ] Admin panel for adding new problems without fixtures
- [ ] Email verification for registration

---

## License

MIT License — see [LICENSE](LICENSE) for details.

```
Copyright (c) 2026 LLD Practice Platform Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```
