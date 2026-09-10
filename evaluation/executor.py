"""
CodeExecutor: safely runs learner-submitted Python code against
problem-specific hidden test cases using a subprocess with timeout.
"""
import subprocess
import sys
import os
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

# Forbidden imports that could harm the server
FORBIDDEN_IMPORTS = [
    'os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib',
    'requests', 'http', 'ftplib', 'smtplib', 'pickle',
    '__import__', 'eval(', 'exec(', 'compile(',
    'open(', 'file(', 'input(', 'raw_input(',
]

TEST_CASES_DIR = Path(__file__).parent / 'test_cases'


@dataclass
class ExecutionResult:
    passed: int = 0
    total: int = 0
    stdout: str = ''
    stderr: str = ''
    timed_out: bool = False
    blocked: bool = False  # True if forbidden import detected

    @property
    def pass_rate(self):
        if self.total == 0:
            return 0
        return round((self.passed / self.total) * 100)


class CodeExecutor:
    """
    Executes learner code against hidden test cases.
    Strategy: prepend learner code + test harness, run in subprocess.
    """

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def _check_forbidden(self, code: str) -> str | None:
        """Return the first forbidden pattern found, or None."""
        for forbidden in FORBIDDEN_IMPORTS:
            if forbidden in code:
                return forbidden
        return None

    def _load_test_case(self, problem_slug: str) -> str | None:
        """Load the hidden test harness for a problem."""
        slug_clean = problem_slug.replace('-', '_')
        test_file = TEST_CASES_DIR / f'{slug_clean}_tests.py'
        if test_file.exists():
            return test_file.read_text(encoding='utf-8')
        return None

    def run_for_problem(self, problem_slug: str, user_code: str) -> ExecutionResult:
        """Run user_code against the problem's test cases."""
        # Security check
        forbidden = self._check_forbidden(user_code)
        if forbidden:
            return ExecutionResult(
                blocked=True,
                stderr=f'Submission blocked: forbidden usage of "{forbidden}".',
            )

        test_code = self._load_test_case(problem_slug)
        if not test_code:
            # No test cases for this problem — skip code scoring
            return ExecutionResult(total=0, stdout='No test cases available for this problem.')

        return self.run(user_code, test_code)

    def run(self, user_code: str, test_code: str) -> ExecutionResult:
        """
        Combine user_code + test_code and execute in an isolated subprocess.
        The test harness prints results in the format:
            PASS: test_name
            FAIL: test_name — reason
        """
        combined = textwrap.dedent(f"""
# === LEARNER CODE ===
{user_code}

# === TEST HARNESS ===
{test_code}

# === RUN TESTS ===
if __name__ == '__main__' or True:
    _results = run_tests()
    for name, passed, reason in _results:
        if passed:
            print(f'PASS: {{name}}')
        else:
            print(f'FAIL: {{name}} — {{reason}}')
""")

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False, encoding='utf-8'
        ) as tmp:
            tmp.write(combined)
            tmp_path = tmp.name

        try:
            proc = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            stdout = proc.stdout
            stderr = proc.stderr
            timed_out = False
        except subprocess.TimeoutExpired:
            stdout = ''
            stderr = f'Code execution timed out after {self.timeout} seconds.'
            timed_out = True
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        # Parse results
        passed = sum(1 for line in stdout.splitlines() if line.startswith('PASS:'))
        total = sum(1 for line in stdout.splitlines() if line.startswith('PASS:') or line.startswith('FAIL:'))

        return ExecutionResult(
            passed=passed,
            total=total,
            stdout=stdout,
            stderr=stderr,
            timed_out=timed_out,
        )
