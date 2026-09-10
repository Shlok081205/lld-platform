from django.db import models


class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(help_text='Full problem description shown to the learner')
    requirements = models.TextField(help_text='Bullet-point requirements / constraints')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='Medium')
    tags = models.CharField(max_length=300, blank=True, help_text='Comma-separated tags, e.g. Strategy,State Machine')
    sample_input = models.TextField(blank=True, help_text='Optional: sample usage code shown as hint')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['difficulty', 'title']

    def __str__(self):
        return f'{self.title} ({self.difficulty})'

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def attempt_count_for_user(self, user):
        if user.is_authenticated:
            return self.attempts.filter(learner=user).count()
        return 0