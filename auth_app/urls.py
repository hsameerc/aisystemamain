from django.urls import path
from .views import RegisterAPI, LoginAPI, LogoutAPI, UpdateUserAndProfileAPI, UserTokensAPI, UserDetailsAndTokensListAPI

urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', LogoutAPI.as_view(), name='logout'),
    path('user/update/', UpdateUserAndProfileAPI.as_view(), name='user-update'),

    path('user/get-tokens/', UserDetailsAndTokensListAPI.as_view(), name='user-tokens'),
    path('user/tokens/update/', UserTokensAPI.as_view(), name='user-tokens-update'),

]
