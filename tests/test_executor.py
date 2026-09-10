"""
Tests for CodeExecutor — covers valid code, syntax errors, timeouts,
forbidden imports, and score computation.
"""
import sys
import os
import pytest

# Make sure we can import from evaluation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# We test executor directly without Django, so minimal setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lld_platform.settings')


from evaluation.executor import CodeExecutor, ExecutionResult


SIMPLE_TEST_HARNESS = '''
def run_tests():
    results = []
    # Test 1: basic addition
    try:
        assert add(2, 3) == 5
        results.append(('add_correct', True, ''))
    except Exception as e:
        results.append(('add_correct', False, str(e)))
    # Test 2: zero addition
    try:
        assert add(0, 0) == 0
        results.append(('add_zero', True, ''))
    except Exception as e:
        results.append(('add_zero', False, str(e)))
    return results
'''

INFINITE_LOOP_CODE = '''
def add(a, b):
    while True:
        pass
    return a + b
'''

VALID_CODE = '''
def add(a, b):
    return a + b
'''

BROKEN_CODE = '''
def add(a, b)
    return a + b
'''

FORBIDDEN_CODE = '''
import os
def add(a, b):
    return a + b
'''


class TestCodeExecutor:

    def setup_method(self):
        self.executor = CodeExecutor(timeout=5)

    def test_valid_code_passes_tests(self):
        result = self.executor.run(VALID_CODE, SIMPLE_TEST_HARNESS)
        assert result.passed == 2
        assert result.total == 2
        assert result.timed_out is False
        assert result.blocked is False

    def test_wrong_code_fails_tests(self):
        wrong_code = '''
def add(a, b):
    return a - b  # wrong implementation
'''
        result = self.executor.run(wrong_code, SIMPLE_TEST_HARNESS)
        assert result.passed == 0
        assert result.total == 2

    def test_syntax_error_in_code(self):
        result = self.executor.run(BROKEN_CODE, SIMPLE_TEST_HARNESS)
        assert result.passed == 0
        assert result.total == 0
        assert 'SyntaxError' in result.stderr or result.stderr != ''

    def test_timeout_is_detected(self):
        executor = CodeExecutor(timeout=2)
        result = executor.run(INFINITE_LOOP_CODE, SIMPLE_TEST_HARNESS)
        assert result.timed_out is True

    def test_forbidden_import_blocked(self):
        result = self.executor.run(FORBIDDEN_CODE, SIMPLE_TEST_HARNESS)
        assert result.blocked is True
        assert result.passed == 0

    def test_pass_rate_calculation(self):
        result = ExecutionResult(passed=3, total=5)
        assert result.pass_rate == 60

    def test_pass_rate_zero_total(self):
        result = ExecutionResult(passed=0, total=0)
        assert result.pass_rate == 0

    def test_no_test_cases_returns_zero_total(self):
        result = self.executor.run_for_problem('nonexistent_problem', VALID_CODE)
        assert result.total == 0

    def test_partial_pass(self):
        partial_code = '''
def add(a, b):
    if a == 0 and b == 0:
        return 99  # wrong for zero case
    return a + b
'''
        result = self.executor.run(partial_code, SIMPLE_TEST_HARNESS)
        assert result.passed == 1
        assert result.total == 2


class TestExecutionResult:

    def test_defaults(self):
        r = ExecutionResult()
        assert r.passed == 0
        assert r.total == 0
        assert r.stdout == ''
        assert r.stderr == ''
        assert r.timed_out is False
        assert r.blocked is False

    def test_pass_rate_full(self):
        r = ExecutionResult(passed=5, total=5)
        assert r.pass_rate == 100

    def test_pass_rate_none(self):
        r = ExecutionResult(passed=0, total=5)
        assert r.pass_rate == 0
