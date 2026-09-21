from django.db import models
from accounts.models import User
from quran.models import Ayah
# Create your models here.

class Session(models.Model):
    CHALLENGE_CHOICES = [
        ('random', 'Random challenge'),
        ('specific', 'Specific challenge'),
    ]
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Ayah)
    user_answer = models.ForeignKey(Ayah, on_delete=models.CASCADE,null=True, related_name='user_answer')
    correct_answer = models.ForeignKey(Ayah, on_delete=models.CASCADE, related_name='correct_answer')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_correct(self):
        return self.user_answer == self.correct_answer
            
    class Meta:
        indexes = [
            models.Index(fields=["challenge_type"]),
            models.Index(fields=["user", "-created_at"]),
        ]
