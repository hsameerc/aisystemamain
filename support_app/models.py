from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import MinValueValidator

from django.db.models import DateTimeField


class SupportModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=300, null=True, blank=True)
    model_type = models.CharField(max_length=50, default='completion')
    response_type = models.CharField(max_length=50, default='default')
    engine = models.CharField(max_length=50, default='gpt-3.5-turbo')
    n_epochs = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    batch_size = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True,
                                     blank=True)
    learning_rate_multiplier = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
                                                   null=True, blank=True)
    compute_classification_metrics = models.BooleanField(default=False)
    description = models.TextField()
    finetune = models.TextField(null=True, blank=True)
    preparation = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_models')
    created = models.DateTimeField(auto_now_add=True)
    tuned_at = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SupportTrainingData(models.Model):
    prompt = models.TextField()
    completion = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    support_model = models.ForeignKey(SupportModel, on_delete=models.CASCADE, related_name='support_training_data')

    def __str__(self):
        return f"Prompt: {self.prompt[:20]}..."
