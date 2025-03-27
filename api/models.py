from django.db import models
from django.contrib.auth.models import User

class PDFHistory(models.Model):
    ACTION_CHOICES = [
        ('convert', 'Converted Text to PDF'),
        ('merge', 'Merged PDFs'),
        ('edit', 'Edited PDF'),
        ('pdf_to_word', 'Converted PDF to Word'),
        ('word_to_pdf', 'Converted Word to PDF'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file_name} ({self.action})"
