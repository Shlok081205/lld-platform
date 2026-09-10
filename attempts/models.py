from django.db import models
from django.contrib.auth.models import User
from problems.models import Problem


class Attempt(models.Model):
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('EVALUATING', 'Evaluating'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='attempts')
    text_design = models.TextField(help_text='Learner written design document')
    code = models.TextField(help_text='Learner submitted Python code')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    submitted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.learner.username} â€” {self.problem.title} ({self.status})'

    @property
    def score(self):
        if hasattr(self, 'evaluation'):
            return self.evaluation.overall_score
        return None


class Evaluation(models.Model):
    attempt = models.OneToOneField(Attempt, on_delete=models.CASCADE, related_name='evaluation')
    test_cases_passed = models.IntegerField(default=0)
    test_cases_total = models.IntegerField(default=0)
    execution_output = models.TextField(blank=True)
    execution_error = models.TextField(blank=True)
    ai_feedback = models.JSONField(default=dict)
    overall_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Evaluation for {self.attempt} â€” Score: {self.overall_score}'

    @property
    def code_score(self):
        if self.test_cases_total == 0:
            return 0
        return round((self.test_cases_passed / self.test_cases_total) * 40)

    @property
    def ai_score(self):
        return self.overall_score - self.code_score

    @property
    def pass_rate(self):
        if self.test_cases_total == 0:
            return 0
        return round((self.test_cases_passed / self.test_cases_total) * 100)