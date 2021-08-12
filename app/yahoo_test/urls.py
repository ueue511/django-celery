from django.urls import path
from . import views
from django.urls import re_path, include

urlpatterns = [
    path('auction/', views.Auction_Dataview.as_view(), name='auction_data'),
    # re_path(r'^(?P<task_id>[\w-]+)/$', views.get_progress, name='get_progress'),# プログレスバーのjavascriptに渡すpath
]
