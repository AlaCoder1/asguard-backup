from django.urls import path
from . import views
urlpatterns = [
    # Your other URL patterns...
    path('data', views.monitoring, name='data'),
]
