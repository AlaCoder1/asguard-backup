from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('getAllUsers', views.get_all_users, name="getAllUsers"),
    path('getUser/<int:id>', views.get_user, name="getUser"),
    path('createUser', views.create_user, name="createUser"),
    path('deleteUser/<int:id>', views.delete_user, name="deleteUser"),
    path('modifyUser/<int:id>', views.modify_user, name="modifyUser"),
    path('addPermission', views.add_permission, name="addPermission"),
    path('userChangePW_ByAdmin/<int:id>',
         views.change_password_by_admin, name="userChangePW"),
    path('userChangePW', views.change_password, name="userChangePW"),
    # path('userChangePW/<int:id>', views.changePassword, name="userChangePW"),
    path('update_profile',views.update_profile, name='update_profile'),
    path('getLanguage/<int:id>',views.get_profile_language, name='getLanguage'),
    path('modifyLanguage/<int:id>',views.change_language, name='modifyLanguage'),
]
