
import re
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


