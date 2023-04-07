from django.urls import path
from . import views

urlpatterns = [
    path('add_plan', views.add_plan, name="add_plan"),
    path('add_organizations', views.add_organizations, name="add_organizations"),
    path('add_paymentTransaction', views.add_paymentTransaction, name="add_paymentTransaction"),
    path('add_plansSubscription', views.add_plansSubscription, name="add_plansSubscription"),
    path('add_plansFeatures', views.add_plansFeatures, name="add_plansFeatures"),
]

