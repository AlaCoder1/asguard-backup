from django.urls import path
from . import views

urlpatterns = [
    ####### Certificates Authority ######
    path('getAllCertAuth', views.get_all_cert_auth, name="getAllCertAuh"),
    path('getCertAuth/<int:id>', views.get_cert_auth, name="getCertAuh"),
    path('createCertAuth', views.create_cert_auth, name="createCertAuh"),
    path('deleteCertAuth/<int:id>', views.delete_cert_auth, name="deleteCertAuh"),
    path('exportCertAuth/<int:id>', views.export_cert_auth, name="exportCertAuth"),
    path('exportCertAuthListRev/<int:id>', views.export_cert_auth_list_rev, name="exportCertAuthListRev"),
    
    ####### Certificates ######
    path('getAllCertificates', views.get_all_certificates, name="getAllCertificates"),
    path('getCertificate/<int:id>', views.get_certificate, name="getCertificate"),
    path('createCertificate', views.create_certificate, name="createCertificate"),
    path('deleteCertificate/<int:id>', views.delete_certificate, name="deleteCertificate"),
    path('revokeCertificate/<int:id>', views.revoke_certificate, name="revokeCertificate"),
    path('unrevokeCertificate/<int:id>', views.unrevoke_certificate, name="unrevokeCertificate"),
    path('exportCert/<int:id>', views.export_cert, name="exportCert"),
]
