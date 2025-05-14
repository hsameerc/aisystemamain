from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    company = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.name


class UserTokens(models.Model):
    TOKEN_FOR_CHOICES = (
        ('training', 'Training'),
        ('query', 'Query'),
    )
    TOKEN_CHOICES = (
        ('ada', 'Ada'),
        ('babbage', 'Babbage'),
        ('curie', 'Curie'),
        ('davinci', 'Davinci'), 
        ('gpt-4', 'GPT-4'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token_for = models.CharField(max_length=10, choices=TOKEN_FOR_CHOICES)
    token_type = models.CharField(max_length=10, choices=TOKEN_CHOICES)
    tokens = models.IntegerField(default=0)
    used_tokens = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.tokens} - {self.used_tokens}"
