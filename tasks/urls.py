from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('add_user', views.add_user, name="add_user"),
    path('add_group', views.add_group, name="add_group"),
    path('all_users', views.all_users, name="all_users"),
    path('all_users_by_directory', views.all_users_by_directory, name="all_users_by_directory"),
    # path('update_appeloffre/<str:pk>', views.update, name="update_appeloffre"),
    # path('supp_appeloffre/<str:pk>', views.supp, name="supp_appeloffre"),
    # path('postulation/<str:pk>', views.add_postule, name="postulation"),
    # path('une_offre/<str:pk>', views.aff_une_offre, name="aff_une_offre"),
    # path('postes', views.aff_postule, name="aff_postule"),
    # path('supp_appeloffre/<str:pk>', views.supp_postule, name="supp_poste"),
    # path('update_postule/<str:pk>', views.update_postule, name="update_postule"),
    # path('registre', views.register, name="registre"),
    # path('login', views.loginPage, name="login"),
    # path('logout', views.logoutUser, name="logout"),
    # path('profile', views.profile, name="profile"),
    # path('all_user', views.aff_user, name='aff_user'),
    # path('un_user', views.aff_un_user, name='aff_un_user'),
    # path('update_user/<str:pk>', views.updateUser, name='update_user'),
    # path('une_poste/<str:pk>', views.aff_une_postule, name='aff_une_postule'),
    # path('about', views.about, name='about'),
    # path('contact', views.contact, name='contact'),
]