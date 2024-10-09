
import subprocess


def execute_command(command):
    """function to execute command"""
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

def get_details_directory(file_path):
    """ function to get details about directory
    """
    list_files=[]
    cmd = f"sudo ls {file_path} "
    output,error=execute_command(cmd)
    if error=="":
        list_files=output.split("\n")
    return list_files