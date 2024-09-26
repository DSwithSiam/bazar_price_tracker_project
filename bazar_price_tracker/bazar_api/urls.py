from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('Search_results', views.Search_results, name='search_results'),
    path('profile/', views.profile_view, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('add_product/', views.add_product_to_api_view, name='add_product'),
]
