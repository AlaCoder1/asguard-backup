from django.urls import path
from . import views

urlpatterns = [
    ####### Private Key ######
    path('getAllPrivateKey', views.get_all_private_key, name="getAllPrivateKey"),
    path('getPrivateKey/<int:id>', views.get_private_key, name="getPrivateKey"),
    path('createPrivateKey', views.create_private_key, name="createPrivateKey"),
    path('deletePrivateKey/<int:id>', views.delete_private_key, name="deletePrivateKey"),
    
    ####### Public Key ######
    path('getAllPublicKey', views.get_all_public_key, name="getAllPublicKey"),
    path('getPublicKey/<int:id>', views.get_public_key, name="getPublicKey"),
    path('createPublicKey', views.create_public_key, name="createPublicKey"),
    path('deletePublicKey/<int:id>', views.delete_public_key, name="deletePublicKey"),
]