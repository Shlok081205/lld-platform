# AI Usage Documentation

> **Assignment:** CipherSchools Engineering Assignment — LLD Practice Platform  
> **AI Tools Used:** Google Gemini 1.5 Flash (via `google-generativeai` Python SDK)  
> **Scope:** This document records the five most meaningful AI-assisted design decisions made during development, including what was accepted, what was rejected, and the rationale behind each choice.

---

## Decision 1: Structured Gemini Prompt Design

### Context
The core of the platform is the AI-powered design evaluation. The initial question was: *how do you prompt an LLM to evaluate a student's design document reliably and consistently across many submissions?*

### What AI Suggested
When I asked Gemini to help design the evaluation prompt, it suggested a **free-text chain-of-thought** format: first ask the model to reason through the document, then ask it to summarize concerns, then score. This mirrors how a human reviewer would think.

```
Suggested approach (rejected):
"Read this design document. Think step by step about the quality of the design.
Then provide your overall assessment and a score between 0 and 100."
```

### What Was Accepted
A **single-shot structured JSON prompt** that:
1. Defines the 7 rubric criteria by name with explicit max scores
2. Embeds the design document and problem title inline
3. Instructs the model to return **only valid JSON** — no prose, no markdown wrapper
4. Specifies the exact schema: `{criterion, score, max_score, evidence, concern, suggestion}`

```python
PROMPT_TEMPLATE = """
You are an expert software design reviewer. Evaluate the following LLD design document
for the problem: "{problem_title}".

Rubric criteria (score each out of its max):
{rubric_json}

Design Document:
\"\"\"
{design_document}
\"\"\"

Return ONLY valid JSON as a list of objects with keys:
criterion, score, max_score, evidence, concern, suggestion.
Do not include any other text.
"""
```

### Why Free-Text Was Rejected
Free-text output is non-deterministic in structure and difficult to parse reliably at scale. A student's submission should produce a consistent rubric table every time — not a variable-length essay. Structured JSON output allowed direct deserialization into `RubricResult` model rows without fragile string parsing.

### Trade-off
Structured prompts are slightly less "thoughtful" — the model doesn't reason as deeply. But for a grading rubric, consistency and parseability outweigh nuance.

---

## Decision 2: Rubric Criteria Selection

### Context
The 60-point AI design score needed to be broken into meaningful criteria that reflect real LLD evaluation standards. The question was: what should those criteria be?

### What AI Suggested
Gemini suggested **10 criteria** when asked to generate a design rubric:

1. Class naming and clarity
2. Attribute completeness
3. Method responsibility (SRP)
4. Inheritance vs. composition choice
5. Interface / abstract class usage
6. Design pattern identification
7. SOLID principles adherence
8. Error handling approach
9. Scalability considerations
10. Code readability (from code snippet)

### What Was Accepted (7 of 10)
After analysis, 7 criteria were retained and 3 were dropped:

| Criterion | Kept? | Reason |
|---|---|---|
| Class Design & Relationships | ✅ | Core LLD skill |
| SOLID Principles | ✅ | Explicitly tested in interviews |
| Design Patterns | ✅ | Directly relevant |
| Abstraction Quality | ✅ | Tests interface/abstract class use |
| Encapsulation | ✅ | Measurable from document |
| Extensibility | ✅ | Ties to Open/Closed principle |
| Naming & Clarity | ✅ | Easy to assess objectively |
| Error handling approach | ❌ | Too speculative from document alone |
| Scalability considerations | ❌ | Out of scope for an LLD doc |
| Attribute completeness | ❌ | Redundant with Class Design criterion |

### Rationale for Cuts
**Error handling** and **scalability** are valuable but require implementation-level context that a design document may not provide — scoring them would reward verbosity over quality. **Attribute completeness** was redundant with the Class Design criterion.

---

## Decision 3: Scoring Weight Split (40% Code / 60% AI)

### Context
The platform needed to decide how to weight deterministic code test results versus AI design evaluation.

### Options Considered

| Split | Rationale |
|---|---|
| 50 / 50 | Equal weight; fair but doesn't emphasize design |
| 70 Code / 30 AI | Code-heavy; penalizes good designers who make syntax errors |
| 40 Code / 60 AI | Design-heavy; reflects the "LLD" framing of the platform |
| 30 Code / 70 AI | AI-heavy; risks over-relying on a non-deterministic evaluator |

### What Was Chosen: 40 Code / 60 AI

The **40/60 split** was chosen for the following reasons:

1. **Platform identity**: The platform is called "LLD Practice" — design thinking is the primary skill being evaluated. A 50/50 or 70/30 split would make it indistinguishable from a code judge.

2. **Accessibility**: A learner who writes excellent design documentation but has syntax issues (e.g., a Python beginner) should still be able to score reasonably. A 60-point ceiling for design means a student who scores 50/60 on design and 10/40 on code still passes with 60%.

3. **AI reliability**: 60% for AI is high enough to matter but not so high that a single bad Gemini response tanks a student's score. The deterministic 40% provides a stable floor.

4. **Interview reality**: In real LLD interviews, the discussion (equivalent to the design document) typically weighs more than live-coding correctness.

---

## Decision 4: JSON Output Format for AI Feedback

### Context
Once the decision to use structured AI output was made, the next question was the *exact schema* of the JSON response.

### What AI Suggested Initially
```json
{
  "overall_score": 45,
  "summary": "The design lacks...",
  "criteria": [...]
}
```
A nested object with an `overall_score` at the top level.

### What Was Adopted
A **flat array** of criterion objects, with the overall score computed by the application (not the AI):

```json
[
  {
    "criterion": "Class Design & Relationships",
    "score": 9,
    "max_score": 12,
    "evidence": "ParkingLot references Floor which references Spot — clean hierarchy",
    "concern": "No interface defined for payment processing",
    "suggestion": "Define a PaymentProcessor interface to allow strategy swapping"
  },
  ...
]
```

### Why This Schema
1. **No computed fields from AI**: The overall design score is `sum(row.score)` — computed in Python. Trusting the AI to compute totals introduces arithmetic errors.
2. **Evidence is mandatory**: Each criterion must cite a specific phrase from the document. This prevents hallucinated scores and forces the AI to ground its assessment.
3. **Separated concern/suggestion**: A `concern` is a factual observation about what's missing; a `suggestion` is an actionable improvement. Conflating them produces vague feedback. Separating them yields more useful output.
4. **Flat list**: Easier to iterate and render in the Django template rubric table without complex nested access.

---

## Decision 5: Security Sandbox for Code Execution

### Context
Allowing arbitrary Python code execution on a server is inherently dangerous. A student could submit code that reads files, makes network requests, or runs infinite loops.

### What AI Recommended
Gemini recommended a **Docker-based sandbox**: wrap each code execution in a fresh, isolated container with resource limits, no network access, and a strict timeout.

```
Recommended (not implemented):
docker run --rm --network=none --memory=128m --cpus=0.5 \
  --timeout=10 python:3.11-slim python /tmp/submission.py
```

### What Was Implemented (Simplified)
For the MVP, a **restricted `exec()` environment** was used instead:

```python
SAFE_BUILTINS = {
    '__builtins__': {
        'print': print, 'len': len, 'range': range,
        'int': int, 'str': str, 'list': list, 'dict': dict,
        'set': set, 'tuple': tuple, 'bool': bool, 'float': float,
        'isinstance': isinstance, 'issubclass': issubclass,
        'hasattr': hasattr, 'getattr': getattr,
        'enumerate': enumerate, 'zip': zip, 'map': map,
        'filter': filter, 'sorted': sorted, 'min': min, 'max': max,
        'abs': abs, 'sum': sum, 'round': round,
        'Exception': Exception, 'ValueError': ValueError,
        'TypeError': TypeError, 'KeyError': KeyError,
        'AttributeError': AttributeError, 'StopIteration': StopIteration,
        'NotImplementedError': NotImplementedError,
    }
}

import signal
signal.alarm(10)  # 10-second timeout (Unix only)
exec(user_code, SAFE_BUILTINS)
```

### Why Docker Was Not Used
1. **Complexity**: Docker requires the host to have Docker installed and adds ~2s cold-start latency per submission — unacceptable for interactive feedback
2. **Assignment scope**: This is an MVP for an engineering assignment, not a production code judge. The restricted exec + timeout is "good enough" for the assignment context
3. **Platform limitation**: `signal.alarm()` is Unix-only. A production version would need platform-agnostic solution (e.g., `multiprocessing` with timeout)

### Acknowledged Risk
The restricted exec approach is **not production-safe**. A sophisticated user could escape the sandbox via `__class__.__mro__` traversal. The production roadmap includes Docker isolation with gVisor.
