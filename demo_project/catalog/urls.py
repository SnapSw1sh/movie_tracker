from django.urls import path
from . import views
from .views import work_detail_view, toggle_list_entry, edit_review_view, delete_review_view, works_list_view, vote_review, add_comment, edit_list_entry, activity_feed
from users.views import toggle_follow

urlpatterns = [
    path('', views.index_view, name='index'),
    path('works/', works_list_view, name='works_list'),
    path('work/<int:pk>/', work_detail_view, name='work_detail'),
    path('work/<int:pk>/toggle-list/', toggle_list_entry, name='toggle_list'),
    path('review/<int:pk>/edit/',   edit_review_view,   name='edit_review'),
    path('review/<int:pk>/delete/', delete_review_view, name='delete_review'),
    path('review/vote/', vote_review, name='vote_review'),
    path('comment/add/<int:review_pk>/', add_comment, name='add_comment'),
    path('mylist/<int:pk>/edit/', edit_list_entry, name='edit_list_entry'),
    path('activity/', views.activity_feed, name='activity_feed'),
    path('profile/<str:username>/follow/', toggle_follow, name='toggle_follow'),
    path('api/search/', views.external_search, name='api_search'),
    path('api/import-movie/', views.api_import_movie, name='api_import_movie'),
    path('api/import-book/', views.api_import_book, name='api_import_book'),
]
