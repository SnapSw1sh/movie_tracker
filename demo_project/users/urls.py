from django.urls import path
from . import views
from .views import profile_view

urlpatterns = [
    path('register/',views.register_view, name='register'),
    path('login/',   views.login_view,    name='login'),
    path('logout/',  views.logout_view,   name='logout'),
    path('mylist/',  views.mylist_view,   name='mylist'),
    path('profile/', views.profile_view,  name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile_by_username'),
    path('profile/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('search/',  views.search_view,   name='search'),
]

