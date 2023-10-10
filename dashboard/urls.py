from django.urls import path
from . import views
urlpatterns = [
    # Your other URL patterns...
    path('data', views.monitoring, name='data'),
    path('action/<str:service>/<str:action>',views.set_actions_service,name="action")
]
