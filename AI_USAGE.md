# AI Collaboration & Engineering Decisions (AI_USAGE.md)

**Project:** LLD Practice Platform  
**Author:** Shlok Patel & Antigravity AI Assistant  
**Assignment:** CipherSchools Engineering Assignment (LLD Practice Platform MVP)  
**AI Integrations:** Google Gemini 1.5 Flash (via `google-generativeai`), AI-assisted pair programming and architectural design

---

## Executive Summary

This document details the collaboration between the engineer (Shlok Patel) and the AI assistant during the conception, design, and implementation of the LLD Practice Platform. Rather than using AI merely for boilerplate generation, the collaboration involved active debate, iterative requirement refinement, trade-off evaluations, and joint technical decisions.

Below are the key collaborative decisions made during the project lifecycle, outlining what was proposed, what was modified or rejected, and why.

---

## Decision 1: Hybrid Submission Model (Text Design + Executable Code)

### Background & Initial Proposal
The AI initially recommended a purely text-based submission model where learners submit only a Markdown/text design document outlining class structures, design patterns, and trade-offs. The rationale was that LLD is fundamentally about high-level object relationships and that compiling/running code could introduce unnecessary complexity for a two-day MVP.

### Engineer Feedback & Intervention
The engineer intervened with a key product enhancement: *"Change Submission format to Text + Code based and run the code for better scoring."*

The reasoning was that pure text evaluation relies entirely on subjective LLM inference, whereas real engineering evaluations benefit from verifying that the code actually instantiates, executes, and satisfies core functional requirements without runtime crashes.

### Collaborative Resolution
We adopted a dual-input submission model:
- **Left Panel:** Text design document capturing architectural rationale, class responsibilities, and pattern choices.
- **Right Panel:** In-browser Python editor (CodeMirror) allowing learners to write runnable object-oriented code.
- **Evaluation:** Combined deterministic test suite execution with qualitative AI rubric review.

---

## Decision 2: Hybrid Scoring Architecture (40% Code / 60% AI Rubric)

### Background & Options Evaluated
With both code and text available, we needed an equitable, transparent scoring mechanism. We evaluated four weighting options:
1. **70% Code / 30% AI:** Heavily biased toward competitive programming. A minor method signature mismatch would severely penalize an otherwise elegant architecture.
2. **50% Code / 50% AI:** Balanced, but did not sufficiently reflect that this is an LLD (design) platform rather than an algorithmic judge like LeetCode.
3. **30% Code / 70% AI:** Overly dependent on non-deterministic LLM output, reducing learner trust in objective scoring.
4. **40% Code / 60% AI (Adopted):** Placed primary emphasis on design quality while anchoring the baseline on deterministic unit tests.

### Implementation Decision
- **Code Score (Max 40 points):** Calculated deterministically as `(passed_tests / total_tests) * 40`.
- **AI Design Score (Max 60 points):** Calculated from 7 rubric criteria evaluated by Gemini, mapped to a 60-point scale: `(sum(criteria_scores) / total_max_scores) * 60`.
- **Overall Score (Max 100 points):** Sum of Code Score + AI Score.
- **Result:** If the LLM is temporarily unavailable or in fallback mode, the deterministic score guarantees immediate objective feedback.

---

## Decision 3: Deterministic Sandbox vs. Full Container Isolation

### Background
Executing untrusted user-submitted Python code on the backend presents security and reliability risks (infinite loops, system calls, resource exhaustion).

### AI Suggestion vs. Practical Constraints
- **AI Initial Suggestion:** Spin up ephemeral Docker containers or invoke an external judge API (such as Judge0).
- **Engineer Consideration:** Adding a Docker daemon dependency complicates local setup, cross-platform execution on Windows developer machines, and adds 2-3 seconds of cold-start latency per submission.
- **Adopted Approach:** We designed an in-process, lightweight `CodeExecutor` using Python's `subprocess` module with:
  1. Strict execution timeout (default 10 seconds) using `subprocess.run(timeout=...)`.
  2. Static security filter blocking dangerous imports and builtins (`os`, `sys`, `subprocess`, `socket`, `open`, `eval`, `exec`).
  3. Isolated temporary files created via `tempfile.NamedTemporaryFile` and deleted immediately in `finally` blocks.
  4. Structured stdout/stderr capture mapping directly to `PASS:` and `FAIL:` test harness lines.

This provided an optimal balance of developer velocity, zero-dependency setup, and practical safety for an MVP demonstration.

---

## Decision 4: Structured JSON Rubric Output vs. Unconstrained AI Reasoning

### Context
A standard trap in AI evaluation is asking the model open-ended questions like *"Is this a good design? Rate from 1 to 100."* This yields erratic scoring, inconsistent formatting, and hallucinated calculations.

### Collaborative Prompt Engineering
We established a strict contract with Google Gemini:
1. **Fixed Criteria Definition:** 7 core LLD dimensions (Requirement Understanding, Class Responsibilities, Coupling/Cohesion, Encapsulation/Interfaces, Design Patterns, Extensibility, Code Quality).
2. **Required Schema:** The model must output strictly valid JSON conforming to:
   ```json
   {
     "criteria": [
       {
         "name": "Class Responsibilities",
         "score": 8,
         "max_score": 10,
         "evidence": "Concrete quote or observation from submission",
         "concern": "Specific anti-pattern or missing separation",
         "suggestion": "Actionable advice for improvement"
       }
     ],
     "summary": "Overall synthesis and top recommendation"
   }
   ```
3. **Application-Computed Math:** The application calculates total scores and percentages in Python rather than trusting the LLM to perform arithmetic.
4. **Graceful Fallback:** If the API key is missing or the response cannot be parsed, the system gracefully falls back to mock rubric feedback rather than crashing the submission flow.

---

## Decision 5: Rubric Scope & Domain Boundary Selection

### Context
The AI initially proposed 10 evaluation criteria including *"Database indexing strategy"*, *"Distributed caching"*, and *"Error logging frameworks"*.

### Refinement & Alignment with Assignment Scope
The assignment brief explicitly emphasized: *"This is primarily an LLD/domain-design exercise. Do not spend the majority of your time on Kubernetes, microservices, multi-region deployment, sharding, CDN design, or other large-scale HLD concerns."*

In accordance with this guideline, we pruned out-of-scope criteria and retained 7 focused, class-level design dimensions:
1. **Requirement Understanding:** Completeness against stated problem constraints.
2. **Class Responsibilities:** Adherence to Single Responsibility Principle (SRP); absence of God classes.
3. **Coupling and Cohesion:** Loose coupling between modules and tight internal cohesion.
4. **Encapsulation and Interfaces:** Usage of abstract base classes, protocols, and clean visibility boundaries.
5. **Design Patterns:** Appropriate application of Strategy, State, Observer, and Factory patterns where justified.
6. **Extensibility:** Open/Closed Principle adherence when introducing new features (e.g., new split types, payment modes).
7. **Code Quality:** Readability, modularity, idiomatic Python conventions, and clean naming.

---

## Summary of Collaborative Dynamic

| Area | Initial AI Idea | Engineer Intervention / Refinement | Final Implemented Decision |
|---|---|---|---|
| Submission Format | Text design document only | Add runnable Python code execution | Text design + Python code dual submission |
| Evaluation Engine | LLM-only grading | Add automated unit test verification | 40% Deterministic tests + 60% AI rubric |
| Execution Environment | Docker container per run | Avoid heavy local infra dependencies | Subprocess with timeout & forbidden import blocker |
| AI Prompting | Free-text commentary | Enforce strict schema & backend calculation | Structured JSON rubric with evidence citations |
| Problem Scope | Generic system design topics | Focus strictly on object-oriented LLD | 5 curated LLD problems (Splitwise, Parking Lot, etc.) |
