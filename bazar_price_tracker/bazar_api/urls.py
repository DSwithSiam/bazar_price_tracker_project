from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('Search_results', views.Search_results, name='search_results'),
    path('profile/', views.profile_view, name='profile'),
]
