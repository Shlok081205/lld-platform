"""
AIEvaluator: uses Google Gemini to evaluate LLD design quality
against a fixed rubric, returning structured JSON feedback.
"""
import json
import logging
from django.conf import settings
from .rubric import CRITERIA

logger = logging.getLogger(__name__)

# Preferred fallback models in order of priority
CANDIDATE_MODELS = [
    getattr(settings, 'GEMINI_MODEL', 'gemini-3.6-flash'),
    'gemini-3.6-flash',
    'gemini-3.7-flash',
    'gemini-3.5-flash',
    'gemini-flash-latest',
]


class AIEvaluator:
    """
    Sends learner's text design + code + execution results to Gemini
    with a structured rubric prompt. Returns parsed JSON feedback.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-3.6-flash')

    def _build_prompt(self, problem, attempt, exec_result) -> str:
        criteria_text = '\n'.join(
            f"  {i+1}. {c['name']} (0-{c['max_score']}): {c['description']}"
            for i, c in enumerate(CRITERIA)
        )

        exec_summary = (
            f"Code execution: {exec_result.passed}/{exec_result.total} test cases passed.\n"
            f"Output:\n{exec_result.stdout[:1000]}\n"
            f"Errors:\n{exec_result.stderr[:500]}"
            if exec_result.total > 0
            else 'No automated test cases available for code execution.'
        )

        return f"""You are an expert Low-Level Design (LLD) evaluator. Evaluate the following learner submission for the problem: "{problem.title}".

PROBLEM REQUIREMENTS:
{problem.requirements}

LEARNER'S DESIGN DOCUMENT:
{attempt.text_design}

LEARNER'S PYTHON CODE:
```python
{attempt.code}
```

{exec_summary}

EVALUATION RUBRIC:
Score each criterion from 0 to its max score. Be specific — cite evidence from the submission.
{criteria_text}

Respond ONLY with valid JSON in this exact format (no markdown, no explanation outside JSON):
{{
  "criteria": [
    {{
      "name": "Criterion Name",
      "score": <integer>,
      "max_score": <integer>,
      "evidence": "What you found in the submission that informs this score",
      "concern": "Specific design concern or weakness, or empty string if none",
      "suggestion": "Concrete improvement suggestion, or empty string if none"
    }}
  ],
  "summary": "2-3 sentence overall assessment of the design quality and top recommendation."
}}"""

    def evaluate(self, problem, attempt, exec_result) -> dict:
        """
        Call Gemini API and return structured feedback dict.
        Iterates over candidate models if a 404/deprecation occurs.
        Falls back to a default response if API call fails.
        """
        if not self.api_key:
            logger.warning('GEMINI_API_KEY not set — returning mock feedback')
            return self._mock_feedback()

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            prompt = self._build_prompt(problem, attempt, exec_result)

            # Deduplicate while preserving order
            models_to_try = []
            for m in CANDIDATE_MODELS:
                if m not in models_to_try:
                    models_to_try.append(m)

            last_error = None
            for model_name in models_to_try:
                try:
                    logger.info('Attempting Gemini evaluation with model: %s', model_name)
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    raw = response.text.strip()

                    # Strip markdown code fences if present
                    if raw.startswith('```'):
                        raw = raw.split('```')[1]
                        if raw.startswith('json'):
                            raw = raw[4:]
                    feedback = json.loads(raw)
                    return feedback
                except json.JSONDecodeError as json_err:
                    logger.error('Failed to parse JSON response from %s: %s', model_name, json_err)
                    return self._error_feedback('AI returned malformed JSON.')
                except Exception as call_err:
                    logger.warning('Model %s failed: %s', model_name, call_err)
                    last_error = call_err
                    continue

            return self._error_feedback(f'All candidate models failed: {last_error}')

        except Exception as e:
            logger.error('Gemini API setup failed: %s', e)
            return self._error_feedback(str(e))

    def _mock_feedback(self) -> dict:
        """Returned when no API key is configured (dev mode)."""
        return {
            'criteria': [
                {
                    'name': c['name'],
                    'score': 7,
                    'max_score': c['max_score'],
                    'evidence': 'Mock evaluation — configure GEMINI_API_KEY for real feedback.',
                    'concern': '',
                    'suggestion': 'Set GEMINI_API_KEY in your .env file.',
                }
                for c in CRITERIA
            ],
            'summary': 'This is a mock evaluation. Add your GEMINI_API_KEY to .env to receive real AI feedback.',
        }

    def _error_feedback(self, error_msg: str) -> dict:
        """Returned when evaluation fails."""
        return {
            'criteria': [
                {
                    'name': c['name'],
                    'score': 0,
                    'max_score': c['max_score'],
                    'evidence': 'Evaluation failed.',
                    'concern': error_msg,
                    'suggestion': 'Please try submitting again.',
                }
                for c in CRITERIA
            ],
            'summary': f'Evaluation failed: {error_msg}',
        }
