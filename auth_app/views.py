from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout

from django.db.models import Count

from .models import UserProfile, UserTokens
from .serializers import UserProfileSerializer, UserTokenSerializer, UserSerializer, \
    UserDetailsAndTokensSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User


class RegisterAPI(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            user_profile_data = {
                'user': user.id,
                'name': request.data.get('name'),
                'phone': request.data.get('phone'),
                'company': request.data.get('company'),
            }
            profile_serializer = UserProfileSerializer(data=user_profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save()

            token, _ = Token.objects.get_or_create(user=user)

            response_data = {
                'token': token.key,
                'user': user_serializer.data,
                'token_expiration': '',
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        if email:
            user = authenticate(request, email=email, password=password)
        else:
            user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)

            user_serializer = UserSerializer(user)

            response_data = {
                'token': token.key,
                'user': user_serializer.data,
                'token_expiration': '',
            }

            return Response(response_data, status=201)
        else:
            return Response({'error': 'Invalid credentials'}, status=401)


class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


class UpdateUserAndProfileAPI(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):
        user = request.user

        user_serializer = UserSerializer(user, data=request.data.get('user', {}), partial=True)
        if user_serializer.is_valid():
            user_serializer.save()

        try:
            user_profile = user.userprofile
            profile_serializer = UserProfileSerializer(user_profile, data=request.data.get('user_profile', {}),
                                                       partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
        except UserProfile.DoesNotExist:
            pass
        response_data = {
            'user': user_serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UserDetailsAndTokensListAPI(generics.ListAPIView):
    serializer_class = UserDetailsAndTokensSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(id=user.id).annotate(
            support_model_count=Count('support_models'),
            # total_training_datas=Count('support_models__support_data'),
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        tokens = UserTokens.objects.all()

        data = {
            'users': serializer.data,
            'tokens': UserTokenSerializer(tokens, many=True).data,
        }

        return Response(data)


class UserTokensAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        data = request.data
        data['user'] = user.id

        serializer = UserTokenSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def put(self, request):
        user = request.user
        data = request.data
        try:
            token_instance = Token.objects.get(user=user)
            serializer = UserTokenSerializer(token_instance, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Token.DoesNotExist:
            data['user'] = user.id
            serializer = UserTokenSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
