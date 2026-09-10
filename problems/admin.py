from django.contrib import admin
from .models import Problem


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'tags', 'is_active', 'created_at']
    list_filter = ['difficulty', 'is_active']
    search_fields = ['title', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active']