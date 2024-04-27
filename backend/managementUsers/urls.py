from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('getAllUsers', views.getAllUsers, name="getAllUsers"),
    path('getUser/<int:id>', views.getUser, name="getUser"),
    path('createUser', views.createUser, name="createUser"),
    path('deleteUser/<int:id>', views.delete_user, name="deleteUser"),
    path('modifyUser/<int:id>', views.modifyUser, name="modifyUser"),
    path('addPermission', views.addPermission, name="addPermission"),
    path('userChangePW_ByAdmin/<int:id>',
         views.changePasswordByAdmin, name="userChangePW"),
    path('userChangePW', views.changePassword, name="userChangePW"),
    # path('userChangePW/<int:id>', views.changePassword, name="userChangePW"),
    path('update_profile',views.update_profile, name='update_profile'),
    path('getLanguage/<int:id>',views.get_profile_language, name='getLanguage'),
    path('modifyLanguage/<int:id>',views.change_language, name='modifyLanguage'),
]
