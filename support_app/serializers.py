from rest_framework import serializers
from .models import SupportModel, SupportTrainingData


class SupportDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTrainingData
        fields = ('id', 'support_model', 'prompt', 'completion', 'created', 'updated')


class NestedSupportDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTrainingData
        fields = ('id', 'support_model', 'prompt', 'completion', 'created', 'updated')


class SupportModelSerializer(serializers.ModelSerializer):
    # support_training_data = SupportDataSerializer(many=True, read_only=True)

    class Meta:
        model = SupportModel
        fields = (
            'id', 'name', 'description', 'model_type', 'response_type', 'user', 'created', 'updated', 'model_name',
            'engine', 'n_epochs', 'batch_size',
            'learning_rate_multiplier', 'compute_classification_metrics', 'finetune', 'preparation', 'tuned_at')
        read_only_fields = ('user',)

    def create(self, validated_data):
        user = self.context['request'].user
        return SupportModel.objects.create(user=user, **validated_data)
