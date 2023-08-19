from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('topic/<str:slug>/', views.get_topic_via_slug, name='get_topic_via_slug'),
    path('topic/set-learned/<str:slug>/', views.set_topic_learned, name='get_topic_learned'),
    path('topic/set-not-learned/<str:slug>/', views.set_topic_not_learned, name='get_topic_not_learned'),

    path('search/', views.search_content, name='search_content'),

    path('get-tree/', views.get_tree, name='get_tree'),
    path('more-tree/<str:slug>/', views.get_more_tree, name='get_more_tree'),
    path('get-current-topic/<str:slug>/', views.get_current_topic, name='current_topic'),
    path('get-next-topic/<str:current_slug>/', views.get_next_topic, name='get_next_topic'),
    path('get-previous-topic/<str:current_slug>/', views.get_previous_topic, name='get_previous_topic'),

    path('documents/personal-data/', views.personal_data_view, name='personal_data_view'),

    path('profile/', views.profile, name='profile'),

    path('comments/create/<str:topic_slug>/', views.CommentView.as_view(), name='create_comment'),
    path('comments/hide/<int:pk>/', views.hide_comment, name='hide_comment'),
    path('answers/delete/<int:pk>/', views.delete_answer, name='delete_answer'),

    path('gallery', views.gallery, name='gallery'),

    path('bookmarks', views.bookmarks, name='bookmarks'),
    path('bookmarks/add/<str:topic_slug>/', views.add_bookmark, name='add_bookmark'),
    path('bookmarks/remove/<str:topic_slug>/', views.remove_bookmark, name='remove_bookmark'),
]

