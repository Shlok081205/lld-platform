from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from problems.models import Problem
from .models import Attempt, Evaluation
from evaluation.executor import CodeExecutor
from evaluation.evaluator import AIEvaluator
import logging

logger = logging.getLogger(__name__)


def register(request):
    if request.user.is_authenticated:
        return redirect('problems:list')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Start practicing LLD now.')
            return redirect('problems:list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def submit_attempt(request, slug):
    problem = get_object_or_404(Problem, slug=slug, is_active=True)

    if request.method == 'POST':
        text_design = request.POST.get('text_design', '').strip()
        code = request.POST.get('code', '').strip()

        if not text_design or not code:
            messages.error(request, 'Both a design document and code are required.')
            return render(request, 'attempts/submit.html', {
                'problem': problem,
                'text_design': text_design,
                'code': code,
            })

        # Save attempt immediately (so it's not lost if evaluation fails)
        attempt = Attempt.objects.create(
            learner=request.user,
            problem=problem,
            text_design=text_design,
            code=code,
            status='EVALUATING',
        )

        try:
            # Step 1: Run code against test cases
            executor = CodeExecutor()
            exec_result = executor.run_for_problem(problem.slug, code)

            # Step 2: AI evaluation
            ai_evaluator = AIEvaluator()
            ai_feedback = ai_evaluator.evaluate(problem, attempt, exec_result)

            # Step 3: Compute overall score
            total_ai_raw = sum(c['score'] for c in ai_feedback.get('criteria', []))
            total_ai_max = sum(c['max_score'] for c in ai_feedback.get('criteria', []))
            ai_score = round((total_ai_raw / total_ai_max) * 60) if total_ai_max > 0 else 0

            code_score = 0
            if exec_result.total > 0:
                code_score = round((exec_result.passed / exec_result.total) * 40)

            overall_score = ai_score + code_score

            # Step 4: Save evaluation
            Evaluation.objects.create(
                attempt=attempt,
                test_cases_passed=exec_result.passed,
                test_cases_total=exec_result.total,
                execution_output=exec_result.stdout,
                execution_error=exec_result.stderr if exec_result.stderr else '',
                ai_feedback=ai_feedback,
                overall_score=overall_score,
            )

            attempt.status = 'COMPLETED'
            attempt.completed_at = timezone.now()
            attempt.save()

        except Exception as e:
            logger.exception('Evaluation failed for attempt %s', attempt.id)
            attempt.status = 'FAILED'
            attempt.save()
            messages.error(request, f'Evaluation encountered an error: {str(e)}')

        return redirect('attempts:result', pk=attempt.pk)

    return render(request, 'attempts/submit.html', {'problem': problem})


@login_required
def attempt_result(request, pk):
    attempt = get_object_or_404(Attempt, pk=pk, learner=request.user)
    evaluation = getattr(attempt, 'evaluation', None)
    return render(request, 'attempts/result.html', {
        'attempt': attempt,
        'evaluation': evaluation,
    })


@login_required
def attempt_history(request):
    attempts = Attempt.objects.filter(learner=request.user).select_related('problem', 'evaluation')
    problem_slug = request.GET.get('problem', '')
    if problem_slug:
        attempts = attempts.filter(problem__slug=problem_slug)
    problems = Problem.objects.filter(is_active=True)
    return render(request, 'attempts/history.html', {
        'attempts': attempts,
        'problems': problems,
        'selected_problem': problem_slug,
    })