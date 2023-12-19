from django.db import models

class ClamAV(models.Model):
   
    logverbose = models.BooleanField()
    tcpsocket = models.CharField(max_length=200)
    tcpport= models.BooleanField()
    maxthreads = models.CharField(max_length=200)
    maxqueue = models.CharField(max_length=200)
    idletimeout = models.CharField(max_length=20)
    maxdirectoryrecursion = models.CharField(max_length=200)
    followdirectorysymlinks = models.BooleanField()
    followfilesymlinks = models.BooleanField()
    disablecache = models.BooleanField()
    alertbrokenexecutables = models.BooleanField()
    alertencryptedarchive = models.BooleanField()
    alertole2macros = models.BooleanField()
    scanpe = models.BooleanField()
    scanelf = models.BooleanField()
    scanole2 = models.BooleanField()
    scanpdf = models.BooleanField()
    scanxmldocs = models.BooleanField()
    scanhwp3 = models.BooleanField()
    scanmail = models.BooleanField()
    scanhtml = models.BooleanField()
    scanarchive = models.BooleanField()
    maxscansize = models.CharField(max_length=200)
    maxfilesize = models.CharField(max_length=200)
    maxrecursion = models.CharField(max_length=200)
    maxfiles = models.CharField(max_length=200)
    freshclamdatabasemirror = models.CharField(max_length=200)
    frechclamconnectiontimeout = models.CharField(max_length=200)
    proxyport = models.CharField(max_length=200)
    clamd_enabled = models.BooleanField()
    freshclam_enabled = models.BooleanField()


    class Meta:
        db_table = 'clamav'

################################## Class for update Freshclam Database ############################

class FreshclamDatabase(models.Model):
    clamav = models.OneToOneField(ClamAV, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    process_type = models.CharField(max_length=255)
    line = models.TextField()

    class Meta:
        db_table = 'clamav_freshclamDatabase'




