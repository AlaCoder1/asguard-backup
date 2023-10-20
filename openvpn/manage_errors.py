import subprocess


class CommandExecutionError(Exception):
    """a class error when execution a command line"""
    def __init__(self, command, message="Error executing command"):
        self.command = command
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.command}"


def create_error(process:subprocess.CompletedProcess, command):
    """Raise an error if the command line doesn't works"""
    if process.returncode == 0:
        print('Output:', process.stdout)
    else:
        print('Error:', process.stderr)
        raise CommandExecutionError(command=command, message=process.stderr)


