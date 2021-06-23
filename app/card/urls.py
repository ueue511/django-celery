from django.urls import path
from . import views


urlpatterns = [
    path('card/', views.card_data, name='scraping_card'),
    # path('test/', views.test, name='cardtest'),
]