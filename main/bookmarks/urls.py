from django.urls import path
from . import views


urlpatterns = [
    path('bookmarks', views.bookmarks, name='bookmarks'),
    path('bookmarks/add/<str:topic_slug>/', views.add_bookmark, name='add_bookmark'),
    path('bookmarks/remove/<str:topic_slug>/', views.remove_bookmark, name='remove_bookmark'),
]