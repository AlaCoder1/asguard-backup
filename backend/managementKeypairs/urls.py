from django.urls import path
from . import views

urlpatterns = [
    ####### Private Key ######
    path('getAllPrivateKey', views.getAllPrivateKey, name="getAllPrivateKey"),
    path('getPrivateKey/<int:id>', views.getPrivateKey, name="getPrivateKey"),
    # path('createCertAuth', views.createCertAuth, name="createCertAuh"),
    # path('deleteCertAuth/<int:id>', views.deleteCertAuth, name="deleteCertAuh"),
    
    ####### Public Key ######
    # path('getAllCertificates', views.getAllCertificates, name="getAllCertificates"),
    # path('getCertificate/<int:id>', views.getCertificate, name="getCertificate"),
    # path('createCertificate', views.createCertificate, name="createCertificate"),
    # path('deleteCertificate/<int:id>', views.deleteCertificate, name="deleteCertificate"),
]