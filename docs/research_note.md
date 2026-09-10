# Research Note: LLD Practice Platform

> **Type:** Product Research Note  
> **Version:** 1.0  
> **Date:** September 2026  
> **Author:** Engineering Assignment Submission

---

## 1. The Learner Problem

### How Learners Currently Practice LLD

Low-Level Design (LLD) is a critical skill evaluated in software engineering interviews at companies like Google, Amazon, Microsoft, and Flipkart. A typical LLD interview asks a candidate to design a system (e.g., "Design a Parking Lot") in 45 minutes, produce class diagrams and class-level code, justify design decisions, and apply patterns like SOLID, Factory, or Observer appropriately.

Current learner behavior for LLD preparation falls into three categories:

1. **Self-study via reference solutions**: Learners read GitHub repositories of LLD solutions, study class diagrams, and try to replicate them. This is passive — reading a solution does not build the skill of arriving at it independently.

2. **Mock interviews with peers**: Learners conduct practice interviews with friends or on platforms like Pramp or Interviewing.io. Feedback quality varies widely depending on the interviewer's LLD expertise. Finding an available, knowledgeable peer is itself a barrier.

3. **Video walkthroughs**: Platforms like YouTube or Educative.io provide video explanations of LLD problems. Again, passive — learners cannot submit their own design and receive feedback on it.

### Pain Points Identified

**No active submission loop.** There is no platform where a learner can write their own design document + code, submit it, and receive structured feedback. The absence of a feedback loop is the single largest gap in LLD preparation tooling.

**Feedback is subjective and delayed.** When a peer reviewer provides LLD feedback in a mock interview, the quality depends on the reviewer's knowledge. Feedback also comes only after scheduling, conducting, and debriefing a session — a high-latency loop.

**No clear evaluation rubric.** Learners don't know what "good" LLD looks like quantitatively. Is using a Factory pattern worth mentioning? Is a missing interface a minor or major issue? Without a rubric, learners cannot self-evaluate or know what to improve.

**No history or progress tracking.** Even learners who practice consistently have no record of how their designs have improved over time. There is no "attempt history" or score trend for LLD.

---

## 2. Existing Tools Surveyed

### LeetCode

**What it is:** The dominant platform for data structures and algorithms (DSA) practice, with a code execution judge, test cases, and discussion forums.

**LLD coverage:** LeetCode has a "Design" problem category (e.g., "Design a HashSet", "LRU Cache") but these are algorithm-level problems — they test implementation speed, not design document quality, class hierarchies, or SOLID principles.

**Gap:** No design document submission. No rubric-based evaluation. No feedback on *how* the code is structured, only whether it passes functional tests. A student who produces a poorly-designed LRU cache but one that passes tests gets full marks.

---

### Educative.io

**What it is:** A subscription-based learning platform with curated text-based courses. Has a popular "Grokking the Object Oriented Design Interview" course.

**LLD coverage:** Covers 10+ LLD problems with detailed written explanations, class diagrams, and reference code in Python/Java.

**Gap:** Purely **theory-heavy** — no submission mechanism. Learners read the reference solution and move on. There is no way to write your own design and get feedback on it. Learning is entirely passive.

---

### GitHub LLD Repositories

**Examples:** `prasadgujar/low-level-design-primer`, `tssovi/grokking-the-object-oriented-design-interview`

**What they are:** Community-maintained reference implementations of common LLD problems.

**Gap:** Reference-only. No interactive practice. No submission. A learner reads the code, thinks "I understand it," and has no way to verify that they can actually design something similar independently. No feedback, no evaluation, no history.

---

### InterviewBit

**What it is:** An engineering interview preparation platform with DSA, system design, and behavioral sections.

**LLD coverage:** Has a "Machine Coding" section with some OOP problems. Primarily **MCQ-style** — select the correct class diagram, identify the pattern, choose the right access modifier.

**Gap:** MCQ format does not evaluate *open-ended design*. A student can guess correctly without understanding the underlying reasoning. No free-form submission or code execution. Evaluates recognition, not creation.

---

## 3. Key Gaps Identified

Synthesizing the survey, three gaps emerge that no existing tool addresses:

| Gap | Description |
|---|---|
| **No submission loop** | No platform accepts a free-form design document + code and provides automated feedback |
| **No structured rubric** | Learners have no quantitative framework for self-assessing LLD quality |
| **No progress tracking** | No tool tracks a learner's LLD improvement over time across multiple problems |

A secondary gap: existing tools treat code and design as separate concerns. In a real LLD interview, the design document *and* the code are both evaluated together. No tool evaluates both in a single submission.

---

## 4. Product Direction

### Why Text + Code Submission?

A real LLD interview involves two deliverables: (1) a verbal/written explanation of the design — classes, relationships, patterns, SOLID reasoning — and (2) actual code. Splitting them into two submission fields mirrors the interview experience exactly.

A pure-code submission misses the design evaluation. A pure-text submission misses functional correctness. Only a dual submission captures the full spectrum of LLD competence.

The text field is intentionally unstructured (not a template with boxes for "Class name", "Attributes", etc.) to encourage learners to think about how to communicate their design, just as they would verbally in an interview.

### Why Rubric-Based AI Evaluation?

AI evaluation (specifically Gemini) was chosen over rule-based evaluation for the design document because:

1. **Design quality is semantic, not syntactic.** A rubric criterion like "applied SOLID principles" cannot be detected by regex or AST parsing of text. It requires language understanding.

2. **AI is available at scale.** A human expert reviewer could provide the best feedback but cannot scale to hundreds of submissions. AI provides "good enough" feedback instantaneously.

3. **Rubric grounds the AI.** Unconstrained AI feedback tends to be verbose and inconsistent. A structured 7-criterion rubric with explicit max scores anchors the evaluation, producing consistent, comparable scores across submissions.

### Why Attempt History Matters?

LLD is a skill — it improves with practice. The attempt history feature serves two purposes:

1. **Motivation**: Seeing a score increase from 45/100 to 72/100 over three attempts on the same problem provides concrete evidence of improvement. This is psychologically motivating in a way that "keep practicing" advice is not.

2. **Skill diagnosis**: A learner who consistently scores 0–5/12 on "Class Design" but high on "SOLID Principles" has a specific gap to address. The history table with per-problem scores makes these patterns visible over time.

Progress tracking transforms the platform from a one-shot grader into a learning tool with longitudinal value.
