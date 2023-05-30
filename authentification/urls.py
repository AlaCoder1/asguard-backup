from django.urls import path
from . import views

urlpatterns = [
    path('authentification', views.authentification,
         name="authentification"),
    path('logout', views.logout_view, name="logout")
]
