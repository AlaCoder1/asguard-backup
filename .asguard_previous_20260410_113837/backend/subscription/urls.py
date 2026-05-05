from django.urls import path
from . import views

urlpatterns = [
    path('payment', views.payment, name="payment"),
    path('list_features_about_last_subscription', views.list_features_about_last_subscription, name="list_features_about_last_subscription"),
    path('subscription_info', views.subscription_info, name="subscription_info"),
    path('license_key', views.license_key, name="license_key"),
    path('features', views.all_feature, name="features"),
    path('getget', views.getget, name="getget"),
]

