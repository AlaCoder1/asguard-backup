from datetime import datetime
import re

from backend.waf.constant_variables import PATH_LOG_WAF
from backend.waf.models import AlertWaf
from utils.commands_utils import read_file_from_system


def synchronize_database_waf_alert():
    """Function that synchronize database with system alerts for WAF.
    This method gets the WAF modsecurity logs, extract the fields for each log and update the database"""
    log_waf_content = read_file_from_system(PATH_LOG_WAF)
    
    len_log = log_waf_content.count("---A--")

    # Loop throw the logs number
    for _ in range(len_log):
        # each log start from ---{log_id}---A-- and finish in ---{log_id}---Z--
        end_log = log_waf_content.find("---Z--\n")
        log = log_waf_content[:end_log+8]
        log_id = extract_dynamic_log_id(log)
        log_waf_content = log_waf_content.replace(log, "", 1)
        if len(AlertWaf.objects.filter(log_system_id=log_id)) == 0:
            log_fields = extract_alert_fields(log, log_id)
            alert_instance = AlertWaf(log_system_id=log_fields["log_system_id"], 
                                      country=log_fields["country"], 
                                      longitude=log_fields["longitude"],
                                      latitude=log_fields["latitude"],
                                      timestamp=log_fields["timestamp"],
                                      violation_file=log_fields["violation_file"],
                                      violation_id=log_fields["violation_id"],
                                      source=log_fields["source"],
                                      method=log_fields["method"],
                                      message=log_fields["message"],
                                      url=log_fields["url"])
            alert_instance.save()


def extract_alert_fields(log: str, log_id: str):
    """Function that take the log and it's id as inputs and return an object contains 
    country, timestamp, violation, source, method, message and URL"""
    # Extract A, B and H bloc from log
    a_bloc = extract_bloc(log, log_id, 'A')
    b_bloc = extract_bloc(log, log_id, 'B')
    h_bloc = extract_bloc(log, log_id, 'H')

    # Extract list of modsecurity part from H bloc
    list_modsecurity = extract_modsecurity_from_h_bloc(h_bloc)
    # Initialize params
    country = None
    latitude = None
    longitude = None
    violation_file_list = ""
    violation_id_list = ""
    message_list = ""
    # Extract GEOIP params, violation and message from each modsecurity in log
    for modsecurity in list_modsecurity:
        # Extract longitude, latitude and country
        try:
            # Search for GEOIP params in data
            data_geoip = extract_field_from_modsecurity(modsecurity, "data")
            data_geoip_list = list(data_geoip.split(','))
            if data_geoip.find("Country") > -1:
                country = data_geoip_list.pop(0)
                country = country.replace("Country: ", "")
            if data_geoip.find("Latitude") > -1:
                latitude = data_geoip_list.pop(0)
                latitude = float(latitude.replace("Latitude: ", ""))
            if data_geoip.find("Longitude") > -1:
                longitude = data_geoip_list.pop(0)
                longitude = longitude.replace("Longitude: ", "")
                longitude = float(longitude[:-2])
        except IndexError:
            pass
        # Extract Violation
        violation_file = extract_field_from_modsecurity(modsecurity, "file")
        # Remove the path of the Core rules file
        violation_file_list += violation_file.replace("/usr/local/modsecurity-crs/rules/", "") + "\n"
        violation_id_list += extract_field_from_modsecurity(modsecurity, "id") + "\n"
        # Extract message
        message_list += extract_field_from_modsecurity(modsecurity, "msg") + "\n"
    violation_file_list = violation_file_list[:-1]
    violation_id_list = violation_id_list[:-1]
    message_list = message_list[:-1]
    
    # Extract Timestamp from A bloc which contains the datetime in format like [28/Jun/2024:08:54:59 +0100]
    try:
        a_bloc = a_bloc.replace(f"---{log_id}---A--\n[", "")
        # print("a_bloc= ", a_bloc)
        timestamp_str = a_bloc[:a_bloc.find("+")-1]
        timestamp = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S")
    except ValueError:
        timestamp = None

    # Extract Source
    try:
        source = list(a_bloc.split("] "))
        source = list(source[1].split(" "))
        source = source[1]
    except IndexError:
        source = None

    # Extract method
    b_bloc = b_bloc.replace(f"---{log_id}---B--\n", "")
    method = list(b_bloc.split(" "))
    method = method[0]

    # Extract URL
    try:
        url = list(b_bloc.split(" "))
        url = url[1]
    except IndexError:
        url = ""
    # Add the Host to the url if exists    
    if log.find("Host: ") > -1:
        host = log[log.find("Host: ") + 6:log.find("\n", log.find("Host: "))]
        url = host + url
    
    # Create an object contains the log fields
    log_fields = {"log_system_id": log_id,
                  "longitude": longitude,
                  "latitude": latitude,
                  "country": country,
                  "timestamp": timestamp,
                  "violation_file": violation_file_list,
                  "violation_id": violation_id_list,
                  "source": source,
                  "method": method,
                  "message": message_list,
                  "url": url}
    return log_fields


def extract_dynamic_log_id(log: str):
    """Function that get a one waf log and return the given id by the system"""
    pattern = r"---(.*?)---B--"
    matches = re.findall(pattern, log)
    return matches[0] if matches else None


def extract_field_from_modsecurity(modsecurity: str, field_name: str):
    """Extract a field from ModSecurity in H bloc"""
    try:
        if modsecurity.find(f'[{field_name} "') > -1:
            return modsecurity[modsecurity.find(f'[{field_name} "')+len(f'[{field_name} "'):modsecurity.find('"]', modsecurity.find(f'[{field_name} "'))]
        return ""
    except Exception:
        return ""


def extract_modsecurity_from_h_bloc(h_bloc: str):
    """Extract all ModSecrutiy parts in H bloc"""
    list_modsecurity = []
    modsecurity_index = h_bloc.find("ModSecurity: ")
    next_modsecurity_index = h_bloc.find("ModSecurity: ", modsecurity_index+11)
    for _ in range(h_bloc.count("ModSecurity: ")):
        modsecurity = h_bloc[modsecurity_index: next_modsecurity_index]
        list_modsecurity.append(modsecurity)
        modsecurity_index = next_modsecurity_index
        next_modsecurity_index = h_bloc.find("ModSecurity: ", modsecurity_index+11)
    return list_modsecurity


def extract_bloc(log: str, log_id: str, bloc: str):
    """Extract bloc from a WAF log"""
    start_bloc = f"---{log_id}---{bloc}--"
    if log.find(start_bloc) > -1:
        return log[log.find(start_bloc):log.find(f"---{log_id}---", log.find(start_bloc)+len(start_bloc))]
    return ""
