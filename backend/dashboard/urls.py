from django.urls import path
from . import views
urlpatterns = [
    # Your other URL patterns...
    path('action',views.set_actions_service,name="action")
]
