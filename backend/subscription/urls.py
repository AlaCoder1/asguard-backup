from django.urls import path
from . import views

urlpatterns = [
    path('payment', views.payment, name="payment"),
    path('add_plan', views.add_plan, name="add_plan"),
    path('add_organizations', views.add_organizations, name="add_organizations"),
    path('add_paymentTransaction', views.add_paymentTransaction, name="add_paymentTransaction"),
    path('add_plansSubscription', views.add_plansSubscription, name="add_plansSubscription"),
    path('add_plansFeatures', views.add_plansFeatures, name="add_plansFeatures"),
    path('list_features_about_last_subscription', views.list_features_about_last_subscription, name="list_features_about_last_subscription"),
    path('subscription_info', views.subscription_info, name="subscription_info"),
    
    
    path('features', views.all_feature, name="features"),
    
    
    
    path('getget', views.getget, name="getget"),
]

