from django.urls import path
from .views import TopView
from django.urls import include


urlpatterns = [
    path('top/', TopView.as_view(), name='top'),
    path('accounts/', include('django.contrib.auth.urls'), name='login'),
    path('top/', include('loto.urls'), name='loto'),
    path('top/', include('card.urls'), name='card'),
    path('top/', include('yahoo_test.urls'), name='yahoo'),
    path('top/', include('stock.urls'), name='stock'),
    path('top/', include('search.urls'), name='search'),
    path('top/', include('map.urls'), name='map'),
]
