import os

directory = '/var/services/'

try:
    files = os.listdir(directory)
    print(f"Found {len(files)} items in {directory}")
    print(files)
except FileNotFoundError:
    print(f"Directory {directory} not found")
except PermissionError:
    print(f"Permission denied to access {directory}")
except Exception as e:
    print(f"Error: {e}")