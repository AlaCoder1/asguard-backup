from django.urls import path
from . import views
urlpatterns = [
    # Your other URL patterns...
    # path('ws/dashboard' ,consumers.DashboardConsumer.as_asgi()),
    path('data', views.monitoring, name='data'),
]
