
import re
import subprocess
from django.db.models import Q
from backend.managementLogs.models import LogsData
from backend.managementLogs.serializers import LogsDataSerializer
def get_attributes_logs(text):
    """function to get attributes from each log 

    Args:
        text (_type_): text
    """
    pattern = r"^(?P<date>\w+ \d+ \d+:\d+:\d+) (?P<process>[^\[]+\[\d+\]): (?P<message>.+)$"
    match = re.match(pattern, text)
    if match:
        date = match.group("date")
        process = match.group("process")
        message = match.group("message")
    else:
        date = process = message = None

    return date, process, message

def get_logs_sys():
    """" function to get all logs system"""
    command = "sudo journalctl -n 10000"
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    return output

def save_logs_database(data):
    """
    function to save logs in database 
        """
    logs_erializer = LogsDataSerializer(data=data)
    if logs_erializer.is_valid() and not LogsData.objects.filter(Q(date=data['date'])& Q(date=data['process']) & Q(date=data['message'])) :
        logs_erializer.save()
      