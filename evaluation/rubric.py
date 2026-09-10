"""
Rubric definitions for AI-powered LLD evaluation.
To add a new evaluation criterion, simply add it to CRITERIA.
The AIEvaluator reads from this dynamically.
"""

CRITERIA = [
    {
        'name': 'Requirement Understanding',
        'max_score': 10,
        'description': 'Did the learner address all problem requirements and constraints? Are edge cases considered?',
    },
    {
        'name': 'Class Responsibilities',
        'max_score': 10,
        'description': 'Does each class have a single, clear responsibility? Are there god classes or classes with too many duties?',
    },
    {
        'name': 'Coupling and Cohesion',
        'max_score': 10,
        'description': 'Are classes loosely coupled? Is related behaviour grouped together? Do changes in one class ripple unnecessarily?',
    },
    {
        'name': 'Encapsulation and Interfaces',
        'max_score': 10,
        'description': 'Are abstractions used appropriately? Are concrete implementations hidden behind interfaces or abstract base classes?',
    },
    {
        'name': 'Design Patterns',
        'max_score': 10,
        'description': 'Are design patterns (Strategy, Observer, Factory, etc.) used appropriately where they add value — not just to show knowledge?',
    },
    {
        'name': 'Extensibility',
        'max_score': 10,
        'description': 'Can new features (new split types, new evaluators, new roles) be added with minimal changes to existing code? Open/Closed Principle.',
    },
    {
        'name': 'Code Quality',
        'max_score': 10,
        'description': 'Is the submitted code clean, well-named, and testable? Are there obvious code smells, magic numbers, or poor naming?',
    },
]

TOTAL_AI_MAX = sum(c['max_score'] for c in CRITERIA)
