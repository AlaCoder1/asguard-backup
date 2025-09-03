from django.urls import path
from . import views

urlpatterns = [
    path('authentification', views.authentication,
         name="authentification"),
    path('logout', views.logout_view, name="logout"),
#     path('create_checkout_session', views.create_checkout_session,
#          name='create_checkout_session'),
    path('send_verification_code', views.send_verification_code),
    path('verify_code/<int:id>', views.verify_code),
    path('resend_verification_code/<int:id>', views.resend_verification_code),
]
