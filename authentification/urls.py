from django.urls import path
from . import views

urlpatterns = [
    path('authentification_JWT',views.authentification_JWT,name="authentification_JWT"),
    path('logout',views.logout_view,name="logout")
]