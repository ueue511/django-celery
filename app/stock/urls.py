from django.urls import path
from . import views


urlpatterns = [
    path('stock/', views.Stock_Dataview.as_view(), name='stock_data'),
    path('ajax3/', views.Stock_Dataview_test, name='stock_data_test'),
    path('plotly', views.Stock_chart_test, name='stock_chart_test'),
]
