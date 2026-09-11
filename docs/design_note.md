# Technical Design Note: LLD Practice Platform MVP

**Type:** Architecture & System Design Document  
**Version:** 1.0  
**Date:** September 2026  
**Status:** Implemented & Verified  
**Project:** LLD Practice Platform  

---

## 1. MVP Scope & Boundaries

The MVP delivers a focused, end-to-end Low-Level Design practice platform tailored around the core learner loop:
```
Problem Selection → Architectural Design & Coding → Submission → Hybrid Evaluation → Feedback Review → Iterative Improvement
```

### In Scope
- **Problem Directory:** 5 curated LLD problems (Splitwise, Parking Lot, Library Management, Vending Machine, Snake & Ladder) with difficulty tiers and tagged design patterns.
- **Dual Submission Interface:** Markdown/text design document (for architectural rationale, class contracts, pattern justification) + CodeMirror in-browser Python editor (for runnable OOP classes).
- **Hybrid Evaluation Engine:**
  - **Deterministic Unit Testing (40 pts):** Subprocess-isolated test runner with security filters and 10-second timeout guard.
  - **AI Rubric Review (60 pts):** Powered by Gemini 3.6 Flash evaluating 7 specific object-oriented design dimensions and returning structured JSON.
- **Explainable Evaluation Report:** KPI metrics, structured rubric data table with evidence quotes, identified concerns, recommended actions, and collapsible test execution logs.
- **Submission History:** Progress tracking across past attempts, per-problem filtering, and score breakdown logs.
- **Django Authentication:** Session-based user registration, login, and access control.

### Out of Scope (Deliberate Non-Goals)
- Distributed infrastructure: Microservices, Kubernetes orchestration, Redis/Celery background queues, multi-region database sharding (as specified in assignment brief section 5).
- Heavyweight containerization daemons (Docker daemon dependencies avoided to ensure zero-friction setup on Windows developer environments).

---

## 2. End-to-End User Flow

1. **Browse Problems (`/problems/`):** Learner browses catalogue cards with difficulty badges (`Easy`, `Medium`, `Hard`) and pattern tags; filterable by tier.
2. **View Specification (`/problems/<slug>/`):** Learner reviews the detailed problem statement, functional requirements, and usage samples, alongside personal attempt history.
3. **Submit Solution (`/attempts/submit/<slug>/`):** Learner writes architectural design notes on the left panel and Python code in the right CodeMirror editor.
4. **Synchronous Evaluation Pipeline:** Form submission triggers:
   - Immediate `Attempt` persistence with `EVALUATING` state.
   - `CodeExecutor` execution against 8 hidden unit test assertions in an isolated subprocess.
   - `AIEvaluator` structured prompt transmission to Gemini 3.6 Flash with fallback resilience.
   - Score synthesis (`overall_score = code_score + ai_score`) and `Evaluation` record creation.
   - Transition of `Attempt` status to `COMPLETED`.
5. **Review Report (`/attempts/<id>/result/`):** Learner examines the executive scorecard, 7-criterion rubric table, evidence citations, and stdout logs.
6. **Iterate & Improve (`/attempts/history/`):** Learner reviews historical progression and submits revised attempts to close identified architectural gaps.

---

## 3. Domain Model Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Django User (django.contrib.auth)                               │
│  ─────────────────────────────────                               │
│  id, username, email, password                                   │
└─────────────────┬────────────────────────────────────────────────┘
                  │ 1
                  │ creates
                  ▼ N
┌──────────────────────────────────────────────────────────────────┐
│  Attempt (attempts.models.Attempt)                               │
│  ─────────────────────────────────                               │
│  id            : BigAutoField (PK)                               │
│  learner       : ForeignKey → User (CASCADE)                     │
│  problem       : ForeignKey → Problem (CASCADE)                  │
│  text_design   : TextField (Architectural rationale)             │
│  code          : TextField (Python source code)                  │
│  status        : CharField (SUBMITTED | EVALUATING |             │
│                             COMPLETED | FAILED)                  │
│  submitted_at  : DateTimeField (auto_now_add=True)               │
│  completed_at  : DateTimeField (null=True, blank=True)           │
└─────────────────┬────────────────────────────────────────────────┘
                  │ 1
                  │ has exactly one
                  ▼ 1
┌──────────────────────────────────────────────────────────────────┐
│  Evaluation (attempts.models.Evaluation)                         │
│  ───────────────────────────────────────                         │
│  id                 : BigAutoField (PK)                          │
│  attempt            : OneToOneField → Attempt (CASCADE)          │
│  test_cases_passed  : IntegerField                               │
│  test_cases_total   : IntegerField                               │
│  execution_output   : TextField (stdout capture)                 │
│  execution_error    : TextField (stderr capture)                 │
│  ai_feedback        : JSONField (Structured rubric dictionary)  │
│  overall_score      : IntegerField (0–100 scale)                 │
│  created_at         : DateTimeField (auto_now_add=True)          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Problem (problems.models.Problem)                               │
│  ─────────────────────────────────                               │
│  id            : BigAutoField (PK)                               │
│  title         : CharField(max_length=200)                       │
│  slug          : SlugField(unique=True)                          │
│  description   : TextField                                       │
│  requirements  : TextField                                       │
│  difficulty    : CharField (Easy | Medium | Hard)                │
│  tags          : CharField (Comma-separated pattern labels)      │
│  sample_input  : TextField                                       │
│  is_active     : BooleanField(default=True)                      │
│  created_at    : DateTimeField(auto_now_add=True)                │
│  updated_at    : DateTimeField(auto_now=True)                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Evaluation Architecture & Key Design Decisions

### A. Dual-Input Submission Model
- **Rationale:** Evaluating LLD solely through code reduces the exercise to basic unit-test passing. Evaluating solely through text misses functional execution and runtime bugs.
- **Implementation:** Text design documents capture architectural rationale, interface abstractions, and design pattern choices. Python code verifies that classes instantiate, maintain encapsulation, and fulfill behavioral contracts.

### B. Scoring Split: 40% Deterministic Code / 60% AI Rubric
- **Code Score (Max 40 points):** `(test_cases_passed / test_cases_total) * 40`.
- **AI Rubric Score (Max 60 points):** `(sum(criteria_scores) / total_max_score) * 60`.
- **Overall Score (Max 100 points):** `code_score + ai_score`.
- **Guaranteed Fallback:** If the external AI service is unavailable or in mock mode, learners still receive deterministic unit test scoring and structured mock feedback.

### C. Execution Sandbox Strategy
- **Implementation:** `evaluation/executor.py` runs learner code in an ephemeral temporary file via Python `subprocess.run()`.
- **Safety Filters:**
  - Static AST/token check blocking dangerous imports and builtins (`os`, `sys`, `subprocess`, `socket`, `open`, `eval`, `exec`).
  - Strict 10-second timeout guard (`timeout=10`).
  - Temporary files cleaned up in `finally` blocks.

### D. Structured Prompt Schema & Arithmetic Protection
- Rather than unconstrained text generation, the prompt enforces a rigid JSON schema:
  ```json
  {
    "criteria": [
      {
        "name": "Class Responsibilities",
        "score": 8,
        "max_score": 10,
        "evidence": "Quoted observation from student submission",
        "concern": "Identified architectural gap or anti-pattern",
        "suggestion": "Concrete refactoring recommendation"
      }
    ],
    "summary": "Overall synthesis and top recommendation"
  }
  ```
- **Math Integrity:** Total scores, percentages, and grade bands are calculated exclusively in Python rather than relying on LLM arithmetic.

---

## 5. Architectural Extensibility & Change Tests

### Change Test A: Transitioning from Text to Class Diagram Submission
*Requirement: How easily can the architecture accommodate diagram inputs (e.g., PlantUML, Mermaid, draw.io XML)?*

1. **Domain Model:** Add a `diagram_source = models.TextField(blank=True)` field to `Attempt` model.
2. **Input Layer:** Update `attempts/submit.html` to include a diagram editor/upload component.
3. **Evaluation Layer:** Introduce a `DiagramParser` service that extracts class relations, inheritance hierarchies, and methods from the diagram format into structured text.
4. **AI Evaluator:** Pass the parsed diagram structure into `AIEvaluator._build_prompt()`.
5. **Untouched Components:** `CodeExecutor`, unit test suites, `Evaluation` schema, result presentation tables, and user history remain 100% unchanged.

### Change Test B: Swapping or Composing Evaluators (e.g., Rule-Based or Human Review)
*Requirement: Can alternative evaluation strategies be integrated without rewriting practice workflows?*

1. **Evaluator Interface:** Both `CodeExecutor` and `AIEvaluator` are loosely coupled modules called in `attempts/views.py`.
2. **Integration:** A new evaluator (e.g. `StaticAnalysisEvaluator` using `pylint`/`flake8` or a `HumanReviewEvaluator`) simply implements an evaluation method returning `{name, score, max_score, evidence, concern, suggestion}`.
3. **Pluggable Execution:** The view orchestrates evaluators and aggregates criterion scores into `Evaluation.ai_feedback`.
4. **Untouched Components:** Frontend templates, problem models, and database schemas require zero restructuring.

---

## 6. Failure Handling & Scalability Trade-offs

| Scenario | Handled By | Outcome |
|---|---|---|
| AI API timeout / Rate limit | Resilient fallback loop in `AIEvaluator` | Retries active candidate models (`gemini-3.6-flash`, `gemini-3.7-flash`, etc.) and returns structured error fallback without 500 error |
| Code infinite loop | `subprocess.run(timeout=10)` | Execution halted after 10s; marked as timeout in execution logs |
| Malicious code execution | `_check_forbidden` scanner | Blocked before subprocess launch; returns security violation error |
| High submission volume | Monolith + Transaction boundaries | Submissions saved to SQLite before evaluation; state tracked as `EVALUATING` &rarr; `COMPLETED`/`FAILED` |

---

## 7. Verification & Quality Assurance

- **Automated Test Suite:** 36 pytest tests in `tests/test_models.py` and `tests/test_executor.py` covering model constraints, state transitions, scoring properties, timeout detection, and security filters.
- **Coverage:** 100% test pass rate across all modules.
