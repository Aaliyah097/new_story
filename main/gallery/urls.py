from django.urls import path
from main.gallery import views

urlpatterns = [
    path('', views.gallery, name='gallery'),
]
