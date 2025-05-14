from django.urls import path
from .views import (
    SupportDataListCreateAPIView,
    SupportDataRetrieveUpdateDeleteAPIView,
    SupportModelListCreateAPIView,
    SupportModelRetrieveUpdateDestroyAPIView, SupportModelValidateAPIView, SupportModelCompletionAPIView,
    SupportModelFineTuneAPIView,
)

urlpatterns = [
    path('model/', SupportModelListCreateAPIView.as_view(), name='support-model-list-create'),
    path('model/<uuid:pk>/', SupportModelRetrieveUpdateDestroyAPIView.as_view(), name='support-model-retrieve-update-delete'),
    path('model/<uuid:pk>/validate/',  SupportModelValidateAPIView.as_view(), name='support-model-validate'),
    path('model/<uuid:pk>/finetune/', SupportModelFineTuneAPIView.as_view(), name='support-model-fine-tune'),
    path('model/<uuid:pk>/test/', SupportModelCompletionAPIView.as_view(), name='support-model-test'),

    path('model/<uuid:support_model_id>/supportdata/', SupportDataListCreateAPIView.as_view(), name='supportdata-list-create'),
    path('model/supportdata/<int:pk>/', SupportDataRetrieveUpdateDeleteAPIView.as_view(), name='supportdata-update-delete'),
]
