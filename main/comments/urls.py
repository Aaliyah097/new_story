from django.urls import path
from . import views

urlpatterns = [
    path('comments/create/<str:topic_slug>/', views.create_comment, name='create_comment'),
    path('comments/hide/<int:pk>/', views.hide_comment, name='hide_comment'),
    path('answers/delete/<int:pk>/', views.delete_answer, name='delete_answer'),
]