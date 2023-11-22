from django.urls import path
from . import views

urlpatterns = [
    ####### Private Key ######
    path('getAllPrivateKey', views.getAllPrivateKey, name="getAllPrivateKey"),
    path('getPrivateKey/<int:id>', views.getPrivateKey, name="getPrivateKey"),
    path('createPrivateKey', views.createPrivateKey, name="createPrivateKey"),
    path('deletePrivateKey/<int:id>', views.deletePrivateKey, name="deletePrivateKey"),
    
    ####### Public Key ######
    path('getAllPublicKey', views.getAllPublicKey, name="getAllPublicKey"),
    path('getPublicKey/<int:id>', views.getPublicKey, name="getPublicKey"),
    # path('createCertificate', views.createCertificate, name="createCertificate"),
    # path('deleteCertificate/<int:id>', views.deleteCertificate, name="deleteCertificate"),
]