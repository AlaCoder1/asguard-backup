import time
from utils.errors_utils import create_error_command

import subprocess


def execute_command_str(command):
    """function to execute command"""
    command="sudo "+command
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    create_error_command(process, command)
    return process.stdout


def execute_command_without_arguments(command:list, decode=True, shell=False):
    """Function that execute a command line without arguments"""
    print(f'command: {" ".join(command)}')
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=decode, shell=shell)
    create_error_command(process, command)
    return process


def execute_list_commands_without_arguments(commands_list):
    """Function that execute a list of commands line without arguments"""
    for command in commands_list:
        execute_command_without_arguments(command)


def execute_command_with_arguments(command:list, arguments:str, time_sleep=0.5):
    """Function that execute a command line with arguments"""
    try:
        with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            print("Command: ", " ".join(command))
            list_arg = list(arguments.split("\n"))
            for arg in range(len(list_arg)):
                print(f"argument {arg}: {list_arg[arg]}")
            time.sleep(time_sleep)
            stdout, stderr = process.communicate(input=arguments)

            create_error_command(process, command)
            return process, stdout, stderr

    except subprocess.CalledProcessError as e:
        create_error_command(process, command)
        return None, None, None
    except Exception as e:
        create_error_command(process, command)
        return None, None, None


def execute_list_commands_with_arguments(list_commands, time_sleep=0.5):
    """Function that execute a list of commands line with arguments"""
    for command in list_commands:
        execute_command_with_arguments(command=command['command'], arguments=command['arguments'],
                                       time_sleep=time_sleep)


def get_current_directory():
    """A function to get the current directory"""
    process = execute_command_without_arguments(['pwd'])
    current_directory = process.stdout
    current_directory = current_directory[:len(current_directory)-1]
    return current_directory


def read_file_from_system(path_file):
    """A function to read content from system using command line"""
    file_content = execute_command_without_arguments(["sudo", "cat", path_file])
    return file_content.stdout


def write_file_from_system(path_file, content_file):
    """A function to create a file if it doesn't exist and write on it using command lines"""
    execute_command_without_arguments(["sudo", "touch", path_file])
    execute_command_str(f"""echo '{content_file}' | cat >> {path_file}""")
