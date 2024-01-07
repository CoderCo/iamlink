from django.urls import path
from . import views

urlpatterns = [
    path('url/<str:hash>/', views.redirect_original_url),
    path('url/', views.create_short_url),
    path('url/stats/<str:hash>/', views.get_url_stats),
    path('url/list/jdjdjegssh/', views.get_list_url),
    path('url/delete/<str:hash>/', views.delete_url),
]