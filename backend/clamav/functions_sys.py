import subprocess

def execute_cmd(command):
    command = "sudo " + command
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

def read_and_extract_clamav_config():
    """Reads the ClamAV config file and extracts commented parameters"""

    clamav_conf_path = "/etc/clamav/clamd.conf"
    
    try:
        output, error = execute_cmd("cat " + clamav_conf_path)
        if output:
            config_content = output.splitlines()
            extracted_data = {}

            for line in config_content:
                # Check if the line matches the form #key value and does not start with '##' or '# '
                if line.startswith('#') and ' ' in line and not line.startswith('##') and not line.startswith('# '):
                    key, value = map(str.strip, line.strip('#').split(maxsplit=1))
                    if key in ['MaxFileSize', 'MaxScanSize']:
                        # Remove the 'M' suffix from the value
                        value = value.rstrip('M')
                    extracted_data[key] = value

            return extracted_data
        else:
            print(f"Command failed: {error}")
            return None

    except FileNotFoundError:
        print(f"The file {clamav_conf_path} was not found.")
        return None
    

def read_and_extract_freshclam_config():
    """Reads the freshclam config file and extracts specific parameters"""

    freshclam_conf_path = "/etc/clamav/freshclam.conf"
    keys_to_extract = ['DatabaseMirror', 'ConnectTimeout', 'HTTPProxyPort']
    try:
        output, error = execute_cmd("cat " + freshclam_conf_path)
        if output:
            config_content = output.splitlines()
            extracted_data = {key: None for key in keys_to_extract}

            for line in config_content:
                # Check if the line starts with the desired keys and extract the value
                for key in keys_to_extract:
                    if line.startswith(f'{key} '):
                        _, value = map(str.strip, line.split(maxsplit=1))
                        extracted_data[key] = value
                        break
                    elif line.startswith(f'#{key} '):
                        _, value = map(str.strip, line.lstrip('#').split(maxsplit=1))
                        extracted_data[key] = value
                        break

            return extracted_data
        else:
            print(f"Command failed: {error}")
            return None

    except FileNotFoundError:
        print(f"The file {freshclam_conf_path} was not found.")
        return None


######################### Function update the configuration data of Clamav #########################


def update_clamav_config(databasedirectory=None,maxfiles=None,maxfilesize=None,scanhtml=None,scanarchive=None,scanxmldocs=None,scanmail=None,scanhwp3=None,scanpdf=None,scanole2=None,disablecache=None,scanelf=None,scanpe=None,alertole2macros=None,alertencryptedarchive=None,alertbrokenexecutables=None,followdirectorysymlinks=None,followfilesymlinks=None,freshclamdatabasemirror=None,freshclamconnectiontimeout=None,tcpport=None,maxpartitions=None,tcpsocket=None,maxqueue=None,maxrecursion=None,proxyport=None,maxscansize=None,maxdirectoryrecursion=None,idletimeout=None,clamd_enabled=None,freshclam_enabled=None,logverbose=None, maxthreads=None):
    
    Clamav_path = "/etc/clamav/clamd.conf"
    freshclam_path= "/etc/clamav/freshclam.conf"
    try:
        ################################## Update the clamav config file ###################################################
    
        cmd_read = f"sudo cat {Clamav_path}"
        output, error = execute_cmd(cmd_read)

        if not error:
            # Read the lines from the file
            lines = output.split('\n')
            updated_lines = []

            # Update the lines based on the parameters
            for line in lines:
                stripped_line = line.strip()

                # Test and update DatabaseDirectory
                if stripped_line.startswith('#DatabaseDirectory ') or stripped_line.startswith('DatabaseDirectory '):
                    if databasedirectory:
                        line = f'DatabaseDirectory {databasedirectory}'

                # Test and update LogVerbose
                elif stripped_line.startswith('#LogVerbose ') or stripped_line.startswith('LogVerbose '):
                    if logverbose is not None:
                        line = f'LogVerbose {"yes" if logverbose else "no"}'

                elif stripped_line.startswith('#TCPSocket ') or stripped_line.startswith('TCPSocket ') and tcpport:
                        line = f'TCPSocket {tcpsocket}'
                         
                elif stripped_line.startswith('#MaxQueue ') or stripped_line.startswith('MaxQueue '):
                    if maxqueue is not None:
                         line = f'MaxQueue {maxqueue}'

                elif stripped_line.startswith('#MaxThreads ') or stripped_line.startswith('MaxThreads '):
                    if maxthreads is not None:
                        line = f'MaxThreads {maxthreads}'

                elif stripped_line.startswith('#IdleTimeout ') or stripped_line.startswith('IdleTimeout '):
                    if idletimeout is not None:
                        line = f'IdleTimeout {idletimeout}'

                elif stripped_line.startswith('#MaxDirectoryRecursion ') or stripped_line.startswith('MaxDirectoryRecursion '):
                    if maxdirectoryrecursion is not None:
                        line = f'MaxDirectoryRecursion {maxdirectoryrecursion}'

                elif stripped_line.startswith('#MaxScanSize ') or stripped_line.startswith('MaxScanSize '):
                    if maxscansize is not None:
                        line = f'MaxScanSize {maxscansize}M'

                elif stripped_line.startswith('#MaxFileSize ') or stripped_line.startswith('MaxFileSize '):
                    if maxfilesize is not None:
                        line = f'MaxFileSize {maxfilesize}M'

                elif stripped_line.startswith('#MaxRecursion ') or stripped_line.startswith('MaxRecursion '):
                    if maxrecursion is not None:
                        line = f'MaxRecursion {maxrecursion}'

                elif stripped_line.startswith('#MaxFiles ') or stripped_line.startswith('MaxFiles '):
                    if maxfiles is not None:
                        line = f'MaxFiles {maxfiles}'

                elif stripped_line.startswith('#MaxPartitions ') or stripped_line.startswith('MaxPartitions '):
                    if maxpartitions is not None:
                        line = f'MaxPartitions {maxpartitions}'


                elif stripped_line.startswith('#FollowDirectorySymlinks ') or stripped_line.startswith('FollowDirectorySymlinks '):
                    if followdirectorysymlinks is not None:
                         line = f'FollowDirectorySymlinks {"yes" if followdirectorysymlinks else "no"}'

                elif stripped_line.startswith('#FollowFileSymlinks ') or stripped_line.startswith('FollowFileSymlinks '):
                    if followfilesymlinks is not None:
                         line = f'FollowFileSymlinks {"yes" if followfilesymlinks else "no"}'

                elif stripped_line.startswith('#DisableCache ') or stripped_line.startswith('DisableCache '):
                    if disablecache is not None:
                         line = f'DisableCache {"yes" if disablecache else "no"}'

                elif stripped_line.startswith('#AlertBrokenExecutables ') or stripped_line.startswith('AlertBrokenExecutables '):
                    if alertbrokenexecutables is not None:
                         line = f'AlertBrokenExecutables {"yes" if alertbrokenexecutables else "no"}'

                elif stripped_line.startswith('#AlertEncryptedArchive ') or stripped_line.startswith('AlertEncryptedArchive '):
                    if alertencryptedarchive is not None:
                         line = f'AlertEncryptedArchive {"yes" if alertencryptedarchive else "no"}'

                elif stripped_line.startswith('#AlertOLE2Macros ') or stripped_line.startswith('AlertOLE2Macros '):
                    if alertole2macros is not None:
                         line = f'AlertOLE2Macros {"yes" if alertole2macros else "no"}'

                elif stripped_line.startswith('#ScanPE ') or stripped_line.startswith('ScanPE '):
                    if scanpe is not None:
                          line = f'ScanPE {"yes" if scanpe else "no"}'

                elif stripped_line.startswith('#ScanELF ') or stripped_line.startswith('ScanELF '):
                    if scanelf is not None:
                         line = f'ScanELF {"yes" if scanelf else "no"}'

                elif stripped_line.startswith('#ScanOLE2 ') or stripped_line.startswith('ScanOLE2 '):
                    if scanole2 is not None:
                        line = f'ScanOLE2 {"yes" if scanole2 else "no"}'

                elif stripped_line.startswith('#ScanPDF ') or stripped_line.startswith('ScanPDF '):
                    if scanpdf is not None:
                        line = f'ScanPDF {"yes" if scanpdf else "no"}'

                elif stripped_line.startswith('#ScanXMLDOCS ') or stripped_line.startswith('ScanXMLDOCS '):
                    if scanxmldocs is not None:
                        line = f'ScanXMLDOCS {"yes" if scanxmldocs else "no"}'

                elif stripped_line.startswith('#ScanHWP3 ') or stripped_line.startswith('ScanHWP3 '):
                    if scanhwp3 is not None:
                        line = f'ScanHWP3 {"yes" if scanhwp3 else "no"}'

                elif stripped_line.startswith('#ScanMail ') or stripped_line.startswith('ScanMail '):
                    if scanmail is not None:
                        line = f'ScanMail {"yes" if scanmail else "no"}'

                elif stripped_line.startswith('#ScanHTML ') or stripped_line.startswith('ScanHTML '):
                    if scanhtml is not None:
                        line = f'ScanHTML {"yes" if scanhtml else "no"}'

                elif stripped_line.startswith('#ScanArchive ') or stripped_line.startswith('ScanArchive '):
                    if scanarchive is not None:
                        line = f'ScanArchive {"yes" if scanarchive else "no"}'
                                                                      

                # Append the updated line to the list
                updated_lines.append(line)

            # Write the updated config back to the file
            with open(Clamav_path, 'w') as file:
                file.write('\n'.join(updated_lines))

            print("ClamAV config updated successfully!")

            # Enable or disable clamav-daemon service based on clamd_enabled
            aux_enable = "enable" if clamd_enabled else "disable"
            enable_command = f"sudo systemctl {aux_enable} --quiet clamav-daemon"
            execute_cmd(enable_command)

            # Enable or disable clamav-freshclam service based on freshclam_enabled
            aux_enable_freshclam = "enable" if freshclam_enabled else "disable"
            enable_command_freshclam = f"sudo systemctl {aux_enable_freshclam} --quiet clamav-freshclam"
            execute_cmd(enable_command_freshclam)

            
             
             ##################### Update the Freshclam config file ######################################
            cmd_read_freshclam = f"sudo cat {freshclam_path}"
            output_freshclam, error_freshclam = execute_cmd(cmd_read_freshclam)

            if not error_freshclam:
                # Read the lines from the Freshclam config file
                lines_freshclam = output_freshclam.split('\n')
                updated_lines_freshclam = []

                # Update the lines based on the parameters
                for line_freshclam in lines_freshclam:
                    stripped_line_freshclam = line_freshclam.strip()

                    
                    if stripped_line_freshclam.startswith('DatabaseMirror '): 
                        if freshclamdatabasemirror:
                            line_freshclam = f'DatabaseMirror {freshclamdatabasemirror}'
                 
                    elif stripped_line_freshclam.startswith('#ConnectTimeout ') or stripped_line_freshclam.startswith('ConnectTimeout '):
                        if freshclamconnectiontimeout:
                            line_freshclam = f'ConnectTimeout {freshclamconnectiontimeout}'

                    elif stripped_line_freshclam.startswith('#HTTPProxyPort ') or stripped_line_freshclam.startswith('HTTPProxyPort  '):
                        if proxyport:
                            line_freshclam = f'HTTPProxyPort {proxyport}'
                   
                    updated_lines_freshclam.append(line_freshclam)

               
                with open(freshclam_path, 'w') as file_freshclam:
                    file_freshclam.write('\n'.join(updated_lines_freshclam))
   

                print("Freshclam config updated successfully!")
               

            else:
                print(f"Error reading Freshclam config: {error_freshclam}")
              
            return True 


        else:
            print(f"Error reading ClamAV config: {error}")
      
 
    except Exception as e:
        
        print(f"Erreur lors de la mise à jour du fichier {freshclam_path}: {e}")
        print(f"Erreur lors de la mise à jour du fichier {Clamav_path}: {e}")

        return False

