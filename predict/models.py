from django.db import models
from django.contrib.auth.models import User

class ImageUpload(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='images',
        null=True,
        blank=True
    )

    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Image {self.id} - {self.user.username}"
        return f"Image {self.id} - Anonymous"
    
class Prediction(models.Model):
    image = models.ForeignKey(
        ImageUpload,
        on_delete=models.CASCADE,
        related_name='predictions'
    )

    label = models.CharField(max_length=100)       
    confidence = models.FloatField()               

    model_name = models.CharField(
        max_length=100,
        default="MobileNetV2"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.label} ({self.confidence})"

class CareGuide(models.Model):
    clothing_type = models.CharField(max_length=100, unique=True)
    washing_instructions = models.TextField()

    temperature = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.clothing_type

class QuestionAnswer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='questions',
        null=True,
        blank=True
    )

    image = models.ForeignKey(
        ImageUpload,
        on_delete=models.CASCADE,
        related_name='qa_pairs',
        null=True,
        blank=True
    )

    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question