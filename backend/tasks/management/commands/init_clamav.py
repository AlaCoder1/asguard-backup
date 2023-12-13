from django.core.management.base import BaseCommand
from backend.clamav.models import *
from backend.authentification.views import *
from backend.clamav.serializers import *
from backend.clamav.functions_sys import *
from django.db import IntegrityError
import hashlib

class Command(BaseCommand):
    """ Reads ClamAV configuration data and saves it to the database """

    def handle(self, *args, **kwargs):
        try:
           
            config_data = read_and_extract_clamav_config()
            freschlam_data = read_and_extract_freshclam_config()

            if config_data:
                MaxThreads=config_data.get("MaxThreads") 
                DatabaseDirectory = config_data.get("DatabaseDirectory")
                TCPSocket = config_data.get("TCPSocket")
                MaxQueue = config_data.get("MaxQueue")
                IdleTimeout = config_data.get("IdleTimeout")
                MaxDirectoryRecursion = config_data.get("MaxDirectoryRecursion")
                MaxScanSize = config_data.get("MaxScanSize")
                MaxFileSize = config_data.get("MaxFileSize")
                MaxRecursion  = config_data.get("MaxRecursion")
                MaxFiles = config_data.get("MaxFiles")
                MaxPartitions = config_data.get("MaxPartitions")
                FreshclamDataBaseMirror = freschlam_data.get("DatabaseMirror")
                FrechclamconnectionTimeout = freschlam_data.get("ConnectTimeout")
                ProxyPort =freschlam_data.get("HTTPProxyPort")
                LogVerbose = config_data.get("LogVerbose")
                TCPPort=config_data.get("TCPPort")
                FollowDirectorySymlinks = config_data.get("FollowDirectorySymlinks")
                FollowFileSymlinks = config_data.get("FollowFileSymlinks")
                DisableCache = config_data.get("DisableCache")
                AlertBrokenExecutables = config_data.get("AlertBrokenExecutables")
                AlertEncryptedArchive = config_data.get("AlertEncryptedArchive")
                AlertOLE2Macros = config_data.get("AlertOLE2Macros")
                ScanPE = config_data.get("ScanPE")
                ScanELF = config_data.get("ScanELF")
                ScanOLE2 = config_data.get("ScanOLE2")
                ScanPDF = config_data.get("ScanPDF")
                ScanXMLDOCS = config_data.get("ScanXMLDOCS")
                ScanHWP3 = config_data.get("ScanHWP3")
                ScanMail = config_data.get("ScanMail")
                ScanHTML = config_data.get("ScanHTML")
                ScanArchive = config_data.get("ScanArchive")


                if LogVerbose is not None:
                    LogVerbose = LogVerbose.lower() == "yes"
                else:
                    LogVerbose = False

                if TCPPort is not None:
                    TCPPort = TCPPort.lower() == "yes"
                else:
                    TCPPort = False

                if FollowDirectorySymlinks is not None:
                    FollowDirectorySymlinks = FollowDirectorySymlinks.lower() == "yes"
                else:
                    FollowDirectorySymlinks = False
  
                if FollowFileSymlinks is not None:
                    FollowFileSymlinks = FollowFileSymlinks.lower() == "yes"
                else:
                    FollowFileSymlinks = False
  
                if DisableCache is not None:
                    DisableCache = DisableCache.lower() == "yes"
                else:
                    DisableCache = False

                if AlertBrokenExecutables is not None:
                    AlertBrokenExecutables = AlertBrokenExecutables.lower() == "yes"
                else:
                    AlertBrokenExecutables = False    
                
                if AlertEncryptedArchive is not None:
                    AlertEncryptedArchive = AlertEncryptedArchive.lower() == "yes"
                else:
                    AlertEncryptedArchive = False

                if AlertOLE2Macros is not None:
                    AlertOLE2Macros = AlertOLE2Macros.lower() == "yes"
                else:
                    AlertOLE2Macros = False    
                
                if ScanPE is not None:
                    ScanPE = ScanPE.lower() == "yes"
                else:
                    ScanPE = False

                if ScanELF is not None:
                    ScanELF = ScanELF.lower() == "yes"
                else:
                    ScanELF = False    
 
                if ScanOLE2 is not None:
                    ScanOLE2 = ScanOLE2.lower() == "yes"
                else:
                    ScanOLE2 = False

                if ScanPDF is not None:
                    ScanPDF = ScanPDF.lower() == "yes"
                else:
                    ScanPDF = False

                if ScanXMLDOCS is not None:
                    ScanXMLDOCS = ScanXMLDOCS.lower() == "yes"
                else:
                    ScanXMLDOCS = False

                if ScanHWP3 is not None:
                    ScanHWP3 = ScanHWP3.lower() == "yes"
                else:
                    ScanHWP3 = False

                if ScanMail is not None:
                    ScanMail = ScanMail.lower() == "yes"
                else:
                    ScanMail = False  

                if ScanHTML is not None:
                    ScanHTML = ScanHTML.lower() == "yes"
                else:
                    ScanHTML = False   

                if ScanArchive is not None:
                    ScanArchive = ScanArchive.lower() == "yes"
                else:
                    ScanArchive = False                         

                # Check the status of ClamAV services
                clamd_status_command = "systemctl is-enabled clamav-daemon.service"
                freshclam_status_command = "systemctl is-enabled clamav-freshclam.service"

                

                clamd_status_output = execute_cmd(clamd_status_command)[0].strip()
                freshclam_status_output = execute_cmd(freshclam_status_command)[0].strip()


                clamd_enabled = clamd_status_output == 'enabled'
                freshclam_enabled = freshclam_status_output == 'enabled'


               

                # Check if the init configuration already exists
                clamav_config = ClamAV.objects.first()
                if not clamav_config:
                    clamav_config = ClamAV(databasedirectory=DatabaseDirectory)

                clamav_config.maxthreads = MaxThreads
                clamav_config.databasedirectory = DatabaseDirectory
                clamav_config.maxqueue = MaxQueue
                clamav_config.idletimeout = IdleTimeout
                clamav_config.tcpsocket = TCPSocket
                clamav_config.maxdirectoryrecursion = MaxDirectoryRecursion
                clamav_config.maxscansize = MaxScanSize
                clamav_config.maxfilesize = MaxFileSize
                clamav_config.maxrecursion = MaxRecursion
                clamav_config.maxfiles = MaxFiles
                clamav_config.maxpartitions = MaxPartitions
                clamav_config.freshclamdatabasemirror = FreshclamDataBaseMirror
                clamav_config.frechclamconnectiontimeout =  FrechclamconnectionTimeout
                clamav_config.proxyport = ProxyPort
                clamav_config.logverbose = LogVerbose
                clamav_config.tcpport = TCPPort
                clamav_config.followdirectorysymlinks = FollowDirectorySymlinks 
                clamav_config.followfilesymlinks = FollowFileSymlinks
                clamav_config.disablecache = DisableCache
                clamav_config.alertbrokenexecutables = AlertBrokenExecutables
                clamav_config.alertencryptedarchive = AlertEncryptedArchive
                clamav_config.alertole2macros = AlertOLE2Macros
                clamav_config.scanpe = ScanPE
                clamav_config.scanelf = ScanELF
                clamav_config.scanole2 = ScanOLE2
                clamav_config.scanpdf = ScanPDF
                clamav_config.scanxmldocs = ScanXMLDOCS
                clamav_config.scanhwp3 = ScanHWP3
                clamav_config.scanmail = ScanMail
                clamav_config.scanhtml = ScanHTML
                clamav_config.scanarchive = ScanArchive
                clamav_config.clamd_enabled  = clamd_enabled
                clamav_config.freshclam_enabled = freshclam_enabled

                clamav_config.save()

                self.stdout.write(self.style.SUCCESS('Data sauvegardé avec succès!!'))
              
            else:
                self.stdout.write(self.style.ERROR('Error in reading configuration!'))
                
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
