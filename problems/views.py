from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Problem


def problem_list(request):
    difficulty = request.GET.get('difficulty', '')
    problems = Problem.objects.filter(is_active=True)
    if difficulty in ['Easy', 'Medium', 'Hard']:
        problems = problems.filter(difficulty=difficulty)

    problems_with_counts = []
    for problem in problems:
        problems_with_counts.append({
            'problem': problem,
            'attempt_count': problem.attempt_count_for_user(request.user),
        })

    return render(request, 'problems/list.html', {
        'problems': problems_with_counts,
        'selected_difficulty': difficulty,
    })


@login_required
def problem_detail(request, slug):
    problem = get_object_or_404(Problem, slug=slug, is_active=True)
    user_attempts = problem.attempts.filter(learner=request.user).order_by('-submitted_at')[:5]
    return render(request, 'problems/detail.html', {
        'problem': problem,
        'user_attempts': user_attempts,
    })