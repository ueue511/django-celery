from django.urls import path
from django.urls import include
from . import views


urlpatterns = [
    # path('loto/', views.loto_data, name='scraping'),
    path('loto/', views.Loto_Choice.as_view(), name='loto_choice'),
    path('ajax/', views.loto_no, name='loto_no'),
    path('ajax2/', views.loto_year, name='loto_year'),
]
