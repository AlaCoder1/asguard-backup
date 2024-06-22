from datetime import datetime
import re

from backend.waf.constant_variables import PATH_LOG_BACKUP, PATH_LOG_WAF
from backend.waf.models import AlertWaf
from utils.commands_utils import execute_command_without_arguments


def rotate_log_alerts_waf():
    """Function that retain only the last 10000 waf alerts and save the rest in backup"""
    with open(PATH_LOG_WAF) as log_waf_file:
        log_waf_content = log_waf_file.read()
    execute_command_without_arguments(["sudo", "mkdir", "-p", PATH_LOG_BACKUP])

    # # Logroutate
    # list_index_start = [match.start() for match in re.finditer("---A--", log_waf_content)]
    # list_index_end = [match.start() for match in re.finditer("---Z--", log_waf_content)]
    # for index in range(len_log // 10000):
    #     backup_content = log_waf_content[list_index_start[index*10000]:list_index_end[index*10000]]
    #     date_now = str(datetime.now())
    #     with open(f"{PATH_LOG_BACKUP}{date_now}", 'w') as backup_file:
    #         backup_file.write(backup_content)
    #     log_waf_content.replace(backup_content, "")

    with open(PATH_LOG_WAF, 'w') as log_waf_file:
        log_waf_file.write(log_waf_content)
    return log_waf_content


def synchronize_database_waf_alert(list_alert_system):
    """Function that synchronize database with system alerts for WAF.
    This method gets a list of the last 10000 logs and update the database"""
    # Add missing system alerts in database
    for alert in list_alert_system:
        if len(AlertWaf.objects.filter(log_system_id=alert["log_system_id"])) == 0:
            alert_instance = AlertWaf(log_system_id=alert["log_system_id"], 
                                      country=alert["country"], 
                                      longitude=alert["longitude"],
                                      latitude=alert["latitude"],
                                      timestamp=alert["timestamp"],
                                      violation_file=alert["violation_file"],
                                      violation_id=alert["violation_id"],
                                      source=alert["source"],
                                      method=alert["method"],
                                      message=alert["message"],
                                      url=alert["url"])
            alert_instance.save()


def create_list_alerts(log_waf_content):
    """Function that get the WAF log content and extract the fields for each log"""
    
    len_log = log_waf_content.count("---A--")

    list_log = []
    # Loop throw the logs number
    for _ in range(len_log):
        # each log start from ---{log_id}---A-- and finish in ---{log_id}---Z--
        end_log = log_waf_content.find("---Z--\n")
        log = log_waf_content[:end_log+8]
        log_id = extract_dynamic_log_id(log)
        log_waf_content = log_waf_content.replace(log, "", 1)
        log_fields = extract_alert_fields(log, log_id)
        list_log.append(log_fields)
    return list_log


def extract_alert_fields(log: str, log_id: str):
    """Function that take the log and it's id as inputs and return an object contains 
    country, timestamp, violation, source, method, message and URL"""
    # Extract longitude, latitude and country. Now it is static
    data_geoip = extract_field_from_h(log, "data")
    try:
        if data_geoip.find("Country") == -1:
            log = log.replace(f"""[data "{data_geoip}"]""", "")
            data_geoip = extract_field_from_h(log, "data")
        data_geoip_list = list(data_geoip.split(','))
        country = data_geoip_list[0].replace("Country: ", "")
        latitude = data_geoip_list[1].replace("Latitude: ", "")
        longitude = data_geoip_list[2].replace("Longitude: ", "")
        longitude = longitude[:-2]
    except IndexError:
        country = None
        latitude = None
        longitude = None

    # Extract Timestamp
    log_a_line = log[log.find(f"---{log_id}---A--\n")+len(f"---{log_id}---A--\n"):log.find(f"---{log_id}---B--\n")]
    timestamp_str = log_a_line[1:log_a_line.find("+")-1]
    # Extract Violation
    violation_file = extract_field_from_h(log, "file")
    violation_file = violation_file.replace("/usr/local/modsecurity-crs/rules/", "")
    violation_id = extract_field_from_h(log, "id")
    # Extract method
    method = log[log.find(f"---{log_id}---B--\n")+len(f"---{log_id}---B--\n"):log.find(" ", log.find(f"---{log_id}---B--\n"))]
    # Extract Source
    source = list(log_a_line.split("]"))
    source = list(source[1].split(" "))
    # Extract message
    message = extract_field_from_h(log, "msg")
    # Extract URL
    url = log[log.find(method) + len(method) + 1:log.find(" ", log.find(method) + len(method) + 1)]
    if log.find("Host: ") > -1:
        host = log[log.find("Host: ") + 6:log.find("\n", log.find("Host: "))]
        url = host + url
    log_fields = {"log_system_id": log_id,
                  "longitude": longitude,
                  "latitude": latitude,
                  "country": country,
                  "timestamp": datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S"),
                  "violation_file": violation_file,
                  "violation_id": violation_id,
                  "source": source[2],
                  "method": method,
                  "message": message,
                  "url": url}
    return log_fields


def extract_dynamic_log_id(log: str):
    """Function that get a one waf log and return the given id by the system"""
    pattern = r"---(.*?)---B--"
    matches = re.findall(pattern, log)
    return matches[0] if matches else None


def extract_field_from_h(log: str, field_name: str):
    try:
        if log.find(f'[{field_name} "') > -1:
            return log[log.find(f'[{field_name} "')+len(f'[{field_name} "'):log.find('"]', log.find(f'[{field_name} "'))]
        return ""
    except Exception:
        return ""
