# Design Note: LLD Practice Platform MVP

> **Type:** Technical Design Note  
> **Version:** 1.0  
> **Date:** September 2026  
> **Status:** Implemented

---

## 1. MVP Scope

The MVP delivers the minimum set of features needed to validate the core product hypothesis: *"An AI-powered rubric evaluation of design documents provides useful, structured feedback to LLD learners."*

**In scope:**
- User registration and authentication (Django built-in)
- 5 curated LLD problems with difficulty tags
- Dual submission: text design document + Python code
- Code execution against problem-specific pytest tests (deterministic)
- AI rubric evaluation of design document via Gemini 1.5 Flash (7 criteria)
- Score display: overall + per-criterion breakdown with evidence/suggestions
- Attempt history per user with problem filtering

**Out of scope (deferred):**
- Diagram submission (draw.io / PlantUML)
- Leaderboard / social features
- Admin UI for adding new problems
- Async evaluation (Celery)
- Docker-based code sandbox
- Email notifications

---

## 2. User Flow

1. **Landing** → User visits `/problems/` (redirected from `/`)
2. **Browse** → User sees 5 problem cards; can filter by difficulty (All / Easy / Medium / Hard)
3. **Register/Login** → If unauthenticated, clicking "Start Practice" redirects to login
4. **Problem Detail** → User reads description, requirements, sample input; sees their past attempts in sidebar
5. **Submit** → User opens `/attempts/<problem_id>/submit/`, writes design doc (left panel) + Python code (CodeMirror right panel)
6. **Evaluate** → Form POSTs to same URL; pipeline runs synchronously (~10–15s)
7. **Result** → User sees overall score circle, code/design breakdown cards, rubric table, execution output, AI summary
8. **Improve** → "Try Again" button returns to step 5; "View History" shows attempt table
9. **History** → `/attempts/history/` shows all attempts with scores, sortable by problem

---

## 3. Domain Model

```
┌─────────────────────────────────────────────────────────────────────┐
│  Django User (built-in)                                             │
│  ─────────────────────                                              │
│  id, username, email, password                                      │
└─────────────────┬───────────────────────────────────────────────────┘
                  │ 1
                  │ creates many
                  ▼ N
┌─────────────────────────────────────────────────────────────────────┐
│  Attempt                                                            │
│  ───────                                                            │
│  id            : AutoField                                          │
│  user          : FK → User                                          │
│  problem       : FK → Problem                                       │
│  design_doc    : TextField                                          │
│  code          : TextField                                          │
│  code_score    : IntegerField  (0–40)                               │
│  design_score  : IntegerField  (0–60)                               │
│  overall_score : IntegerField  (0–100)                              │
│  tests_passed  : IntegerField                                       │
│  tests_total   : IntegerField                                       │
│  execution_out : TextField                                          │
│  ai_summary    : TextField                                          │
│  status        : CharField  (pending | completed | failed)         │
│  created_at    : DateTimeField                                       │
└──────────┬──────────────────────────────────────┬──────────────────┘
           │ N                                    │ N
           │ evaluated for                        │ belongs to
           ▼ 1                                    ▼ 1
┌──────────────────────────────┐    ┌────────────────────────────────┐
│  RubricResult                │    │  Problem                       │
│  ────────────                │    │  ───────                       │
│  id          : AutoField     │    │  id          : AutoField       │
│  attempt     : FK → Attempt  │    │  title       : CharField       │
│  criterion   : CharField     │    │  description : TextField       │
│  score       : IntegerField  │    │  difficulty  : CharField       │
│  max_score   : IntegerField  │    │  requirements: JSONField       │
│  pct         : FloatField    │    │  sample_input: TextField       │
│  evidence    : TextField     │    │  test_module : CharField       │
│  concern     : TextField     │    │  created_at  : DateTimeField   │
│  suggestion  : TextField     │    └──────────────┬─────────────────┘
└──────────────────────────────┘                   │ M
                                                   │ tagged with
                                                   ▼ N
                                    ┌──────────────────────────────────┐
                                    │  Tag                             │
                                    │  ───                             │
                                    │  id   : AutoField                │
                                    │  name : CharField (unique)       │
                                    └──────────────────────────────────┘
```

---

## 4. Key Design Decisions

### Submission Format Choice

A **two-field submission** (text document + Python code) was chosen over alternatives:

- *Single code field*: Would miss design evaluation entirely
- *Diagram upload*: Requires image processing or specialized parsers; out of MVP scope
- *Structured form*: Pre-filling "Class name:", "Attributes:", etc. was rejected because it biases the structure and doesn't test the learner's ability to communicate design freely — a core interview skill

The text field intentionally has only a placeholder to guide content, not a rigid template.

### Evaluation Pipeline (Deterministic + AI)

The pipeline is **sequential and synchronous** in the MVP:

```
POST /attempts/<pk>/submit/
  → Validate form
  → Create Attempt (status=pending)
  → run code_runner.run(attempt)      # ← blocks ~2-5s
  → run ai_evaluator.evaluate(attempt) # ← blocks ~5-10s
  → Update Attempt (status=completed)
  → Redirect to result page
```

A **Celery + Redis async pipeline** would be architecturally superior but adds operational complexity beyond MVP scope. The synchronous approach is honest: the user waits ~15 seconds and sees their result. No polling, no WebSockets needed.

The two evaluators are deliberately isolated:
- `code_runner.py` knows nothing about Gemini
- `ai_evaluator.py` knows nothing about test results
- `pipeline.py` orchestrates both and aggregates scores

This makes each evaluator independently testable and swappable (see Change Tests below).

### Extensibility: How to Add a New Problem

1. Create a fixture entry in `problems/fixtures/problems.json` with title, description, difficulty, requirements, and sample input
2. Create a test file at `problems/tests/test_<slug>.py` with pytest functions that accept the user's module
3. Add the `test_module` field in the fixture pointing to the test file path
4. Run `python manage.py loaddata problems/fixtures/problems.json`

No code changes to views, models, or evaluators are needed to add a new problem.

### Extensibility: How to Add a New Evaluator

The pipeline calls evaluators via a common interface:

```python
class BaseEvaluator:
    def evaluate(self, attempt: Attempt) -> EvaluatorResult:
        raise NotImplementedError
```

To add a new evaluator (e.g., a diagram evaluator, a style linter):
1. Create `attempts/evaluator/diagram_evaluator.py` implementing `BaseEvaluator`
2. Add it to `pipeline.py`'s evaluator list
3. Update the score aggregation logic

### Extensibility: How to Change the Score Split

The 40/60 split is not hardcoded in views. It is defined in `rubric.py`:

```python
MAX_CODE_SCORE = 40
MAX_DESIGN_SCORE = 60
```

Changing these constants and the test weights in each problem's test file is all that's needed to adjust the split.

---

## 5. Change Tests

*(From the assignment guide: demonstrate that the design can accommodate these changes)*

### Change Test A: Text → Diagram Submission

**Scenario:** Replace the design document text field with a diagram upload (PlantUML text or draw.io XML).

**Changes required:**
1. Add a `diagram` FileField to the `Attempt` model (migration required)
2. Replace the textarea in `submit.html` with a file input or a PlantUML editor
3. Create `diagram_parser.py` to convert the uploaded diagram format to a class-level description string
4. Pass the parsed description string to `ai_evaluator.py` instead of the raw text — **the AI evaluator itself doesn't change**
5. Update the submission form validation

**Untouched:** `code_runner.py`, result page, history page, rubric criteria, scoring weights. The change is isolated to the input layer and a new parser.

---

### Change Test B: AI Evaluator → Rule-Based Evaluator

**Scenario:** Replace the Gemini-powered design evaluator with a deterministic rule-based system (e.g., keyword detection, regex checks for class definitions, pattern mentions).

**Changes required:**
1. Create `rule_based_evaluator.py` implementing `BaseEvaluator`
2. Define rules: e.g., +3 pts if "abstract" or "interface" appears in doc, +2 pts per named pattern detected, etc.
3. In `pipeline.py`, swap `AIEvaluator()` for `RuleBasedEvaluator()`
4. The rule-based evaluator returns the same `EvaluatorResult` structure with the same fields (criterion, score, max_score, evidence, concern, suggestion)

**Untouched:** Submission form, code runner, result template (rubric table renders any list of `RubricResult` objects), history page, scoring weights.

The result page will render identically — it doesn't know or care whether the rubric results came from AI or rules.

---

## 6. Trade-offs and Limitations

| Trade-off | Decision Made | Alternative |
|---|---|---|
| Synchronous evaluation | Simple, no infra overhead | Async + Celery (adds Redis, worker management) |
| `exec()` sandbox | Simple, MVP-appropriate | Docker container (more secure, more complex) |
| SQLite database | Zero config, easy to set up | PostgreSQL (needed for production concurrency) |
| CodeMirror 5 | Stable, well-documented | CodeMirror 6 (modern but more setup) |
| Gemini 1.5 Flash | Fast, free tier available | GPT-4o (higher quality, paid only) |
| Sequential evaluators | Easy to reason about | Parallel execution (faster but harder to debug) |

**Biggest limitation:** The `exec()` sandbox is not secure for untrusted code in a public deployment. It is sufficient for an assignment context where the user base is controlled and known.

**Second biggest limitation:** Gemini evaluations are non-deterministic — the same design document submitted twice may receive slightly different scores. This is mitigated by the structured prompt and JSON output format, but not eliminated. A production platform would need to run evaluations multiple times and average, or use a more constrained model.
