# from django.urls import path
# from . import views

# urlpatterns = [
#     path('authentification', views.authentification,
#          name="authentification"),
#     path('logout', views.logout_view, name="logout")
# ]
from django.urls import path
from . import views

urlpatterns = [
    path('authentification', views.authentification,
         name="authentification"),
    path('logout', views.logout_view, name="logout"),
    path('create_checkout_session', views.create_checkout_session,
         name='create_checkout_session'),
]
