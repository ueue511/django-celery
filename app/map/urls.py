from django.urls import path
from . import views


urlpatterns = [
    path('map/', views.Make_Map.as_view(), name='make_map'),
    path('make_map/', views.make_map_post, name='make_map_post'),
]
