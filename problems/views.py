from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Problem


def problem_list(request):
    difficulty = request.GET.get('difficulty', '').strip()
    problems = Problem.objects.filter(is_active=True)
    
    if difficulty:
        diff_cap = difficulty.capitalize()
        if diff_cap in ['Easy', 'Medium', 'Hard']:
            problems = problems.filter(difficulty=diff_cap)
            difficulty = diff_cap

    problem_items = []
    for p in problems:
        p.user_attempt_count = p.attempt_count_for_user(request.user)
        problem_items.append(p)

    return render(request, 'problems/list.html', {
        'problems': problem_items,
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