from django.contrib.auth.models import User
from rest_framework import serializers

from support_app.models import SupportModel, SupportTrainingData
from .models import UserProfile, UserTokens


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTokens
        fields = ('id', 'token_for', 'token_type', 'tokens', 'used_tokens')


class SupportDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTrainingData
        fields = '__all__'


class SupportModelSerializer(serializers.ModelSerializer):
    support_data = SupportDataSerializer(many=True, read_only=True)

    class Meta:
        model = SupportModel
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'userprofile')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserDetailsAndTokensSerializer(serializers.ModelSerializer):
    support_model_count = serializers.IntegerField()
    # total_training_datas = serializers.IntegerField()
    tokens = UserTokenSerializer(many=True)

    class Meta:
        model = User
        fields = ('support_model_count', 'tokens')
