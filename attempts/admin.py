from django.contrib import admin
from .models import Attempt, Evaluation


class EvaluationInline(admin.StackedInline):
    model = Evaluation
    readonly_fields = ['test_cases_passed', 'test_cases_total', 'overall_score', 'ai_feedback']
    extra = 0


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['learner', 'problem', 'status', 'submitted_at']
    list_filter = ['status', 'problem']
    search_fields = ['learner__username', 'problem__title']
    readonly_fields = ['submitted_at', 'completed_at']
    inlines = [EvaluationInline]


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'overall_score', 'test_cases_passed', 'test_cases_total', 'created_at']
    readonly_fields = ['created_at']