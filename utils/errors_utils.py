import subprocess


class CommandExecutionError(Exception):
    """a class error when execution a command line"""
    def __init__(self, command="It's is not a known system command", message="Error executing command"):
        self.command = command
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.command}"


def create_error_command(process:subprocess.CompletedProcess, command):
    """Raise an error if the command line doesn't works"""
    if process.returncode == 0:
        print('Output:', process.stdout)
    elif len(process.stderr) == 0:
        print('Error:', process.stderr)
    else:
        raise CommandExecutionError(command=command, message=process.stderr)