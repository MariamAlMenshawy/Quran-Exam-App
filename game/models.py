from django.db import models
from accounts.models import User
from quran.models import Ayah
# Create your models here.

class Session(models.Model):
    CHALLENGE_CHOICES = [
        ('random', 'Random challenge'),
        ('specific', 'Specific challenge'),
    ]
    challenge_type = models.CharField(choices=CHALLENGE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Ayah)
    user_answer = models.ForeignKey(Ayah, on_delete=models.CASCADE, related_name='user_answer')
    correct_answer = models.ForeignKey(Ayah, on_delete=models.CASCADE, related_name='correct_answer')
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)