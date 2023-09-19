from django.urls import path
from . import views

urlpatterns = [
    ####### Certificates Authority ######
    path('getAllCertAuth', views.getAllCertAuth, name="getAllCertAuh"),
    path('getCertAuth/<int:id>', views.getCertAuth, name="getCertAuh"),
    path('createCertAuth', views.createCertAuth, name="createCertAuh"),
    path('deleteCertAuth/<int:id>', views.deleteCertAuth, name="deleteCertAuh"),
    
    ####### Certificates ######
    path('getAllCertificates', views.getAllCertificates, name="getAllCertificates"),
    path('getCertificate/<int:id>', views.getCertificate, name="getCertificate"),
    path('createCertificate', views.createCertificate, name="createCertificate"),
    path('deleteCertificate/<int:id>', views.deleteCertificate, name="deleteCertificate"),
]
