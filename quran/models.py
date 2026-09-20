from django.db import models

# Create your models here.

class Surah(models.Model):
    surah_number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=50)

class Ayah(models.Model):
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE)
    numberInSurah = models.PositiveIntegerField()
    text = models.TextField()
    juz = models.PositiveIntegerField()