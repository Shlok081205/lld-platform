"""
Django model tests for Attempt, Evaluation, and Problem.
Tests state transitions, score properties, and constraints.
"""
import pytest
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lld_platform.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from problems.models import Problem
from attempts.models import Attempt, Evaluation


class TestProblemModel(TestCase):

    def setUp(self):
        self.problem = Problem.objects.create(
            title='Test Splitwise',
            slug='test-splitwise',
            description='Design a Splitwise clone.',
            requirements='1. Add expense\n2. Split equally\n3. Show balances',
            difficulty='Hard',
            tags='Strategy,Observer',
        )

    def test_problem_str(self):
        assert 'Test Splitwise' in str(self.problem)
        assert 'Hard' in str(self.problem)

    def test_get_tags_list(self):
        tags = self.problem.get_tags_list()
        assert 'Strategy' in tags
        assert 'Observer' in tags
        assert len(tags) == 2

    def test_get_tags_list_empty(self):
        self.problem.tags = ''
        self.problem.save()
        assert self.problem.get_tags_list() == []

    def test_default_difficulty(self):
        p = Problem.objects.create(
            title='Easy Problem',
            slug='easy-problem',
            description='Simple',
            requirements='1. Do something',
        )
        assert p.difficulty == 'Medium'

    def test_is_active_default(self):
        assert self.problem.is_active is True

    def test_attempt_count_unauthenticated(self):
        from unittest.mock import MagicMock
        anon_user = MagicMock()
        anon_user.is_authenticated = False
        assert self.problem.attempt_count_for_user(anon_user) == 0


class TestAttemptModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testlearner',
            password='testpass123',
        )
        self.problem = Problem.objects.create(
            title='Parking Lot',
            slug='parking-lot',
            description='Design a parking lot.',
            requirements='1. Park vehicles\n2. Generate ticket\n3. Compute fee',
            difficulty='Medium',
        )
        self.attempt = Attempt.objects.create(
            learner=self.user,
            problem=self.problem,
            text_design='I would design a ParkingLot class...',
            code='class ParkingLot:\n    pass',
            status='SUBMITTED',
        )

    def test_attempt_str(self):
        assert 'testlearner' in str(self.attempt)
        assert 'Parking Lot' in str(self.attempt)

    def test_default_status_submitted(self):
        assert self.attempt.status == 'SUBMITTED'

    def test_score_property_no_evaluation(self):
        assert self.attempt.score is None

    def test_score_property_with_evaluation(self):
        Evaluation.objects.create(
            attempt=self.attempt,
            test_cases_passed=7,
            test_cases_total=8,
            overall_score=82,
        )
        assert self.attempt.score == 82

    def test_status_transition_to_completed(self):
        self.attempt.status = 'COMPLETED'
        self.attempt.save()
        refreshed = Attempt.objects.get(pk=self.attempt.pk)
        assert refreshed.status == 'COMPLETED'

    def test_status_transition_to_failed(self):
        self.attempt.status = 'FAILED'
        self.attempt.save()
        refreshed = Attempt.objects.get(pk=self.attempt.pk)
        assert refreshed.status == 'FAILED'


class TestEvaluationModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='evaluser',
            password='evalpass123',
        )
        self.problem = Problem.objects.create(
            title='Vending Machine',
            slug='vending-machine',
            description='Design a vending machine.',
            requirements='1. Add items\n2. Select item\n3. Pay and dispense',
            difficulty='Easy',
        )
        self.attempt = Attempt.objects.create(
            learner=self.user,
            problem=self.problem,
            text_design='I would use a State pattern...',
            code='class VendingMachine:\n    pass',
        )

    def test_code_score_full_pass(self):
        ev = Evaluation.objects.create(
            attempt=self.attempt,
            test_cases_passed=8,
            test_cases_total=8,
            overall_score=75,
        )
        assert ev.code_score == 40

    def test_code_score_no_tests(self):
        ev = Evaluation.objects.create(
            attempt=self.attempt,
            test_cases_passed=0,
            test_cases_total=0,
            overall_score=50,
        )
        assert ev.code_score == 0

    def test_code_score_partial(self):
        ev = Evaluation.objects.create(
            attempt=self.attempt,
            test_cases_passed=4,
            test_cases_total=8,
            overall_score=50,
        )
        assert ev.code_score == 20

    def test_pass_rate(self):
        ev = Evaluation.objects.create(
            attempt=self.attempt,
            test_cases_passed=6,
            test_cases_total=8,
            overall_score=68,
        )
        assert ev.pass_rate == 75

    def test_ai_score(self):
        ev = Evaluation.objects.create(
            attempt=self.attempt,
            test_cases_passed=8,
            test_cases_total=8,
            overall_score=85,
        )
        # ai_score = overall - code_score = 85 - 40 = 45
        assert ev.ai_score == 45

    def test_overall_score_default_zero(self):
        ev = Evaluation.objects.create(
            attempt=self.attempt,
        )
        assert ev.overall_score == 0

    def test_ai_feedback_default_empty_dict(self):
        ev = Evaluation.objects.create(
            attempt=self.attempt,
        )
        assert ev.ai_feedback == {}

    def test_evaluation_str(self):
        ev = Evaluation.objects.create(
            attempt=self.attempt,
            overall_score=72,
        )
        assert '72' in str(ev)


class TestScoreComputation(TestCase):
    """Tests for the score computation logic used in views."""

    def test_score_full_pass_full_ai(self):
        test_cases_passed = 8
        test_cases_total = 8
        ai_raw = 70  # 7 criteria x 10
        ai_max = 70
        code_score = round((test_cases_passed / test_cases_total) * 40)
        ai_score = round((ai_raw / ai_max) * 60)
        assert code_score == 40
        assert ai_score == 60
        assert code_score + ai_score == 100

    def test_score_zero_code_full_ai(self):
        code_score = 0
        ai_score = round((70 / 70) * 60)
        assert code_score + ai_score == 60

    def test_score_full_code_zero_ai(self):
        code_score = round((8 / 8) * 40)
        ai_score = 0
        assert code_score + ai_score == 40

    def test_score_partial(self):
        code_score = round((4 / 8) * 40)   # 20
        ai_score = round((42 / 70) * 60)   # 36
        assert code_score == 20
        assert ai_score == 36
