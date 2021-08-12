from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.Search_data.as_view(), name='search_data'),
    path('zip/', views.download_zip, name='zip_data')
]
