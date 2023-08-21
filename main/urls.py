from django.urls import path
from . import views

from main.comments.urls import urlpatterns as comments_urls
from main.gallery.urls import urlpatterns as gallery_urls
from main.bookmarks.urls import urlpatterns as bookmarks_urls


urlpatterns = [
    path('', views.index, name='index'),

    # topics
    path('topic/<str:slug>/', views.get_topic_via_slug, name='get_topic_via_slug'),
    path('topic/set-learned/<str:slug>/', views.set_topic_learned, name='get_topic_learned'),
    path('topic/set-not-learned/<str:slug>/', views.set_topic_not_learned, name='get_topic_not_learned'),

    # search topics
    path('search/', views.search_content, name='search_content'),

    # navigation=tree
    path('get-tree/', views.get_tree, name='get_tree'),
    path('more-tree/<str:slug>/', views.get_more_tree, name='get_more_tree'),
    path('get-current-topic/<str:slug>/', views.get_current_topic, name='current_topic'),
    path('get-next-topic/<str:current_slug>/', views.get_next_topic, name='get_next_topic'),
    path('get-previous-topic/<str:current_slug>/', views.get_previous_topic, name='get_previous_topic'),

    # policies
    path('documents/personal-data/', views.personal_data_view, name='personal_data_view'),
    # user
    path('profile/', views.profile, name='profile'),
] + comments_urls + gallery_urls + bookmarks_urls

