import subprocess
import re

from backend.rules.models import FirewallLog
from backend.rules.serializers import FirewallLogsSerializer

pattern = re.compile(
    r"^(?P<timestamp>\w{3} \d{1,2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<hostname>\S+)\s+"
    r"kernel:\s+"
    r"(___nftables_logs_rule___)?(?P<rule>[^\s]+)___\s*"
    r"IN=(?P<IN>\S*)\s*"
    r"OUT= MAC=(?P<OUT>[0-9a-fA-F:]+)?\s*"
    r"SRC=(?P<SRC>\S+)\s*"
    r"DST=(?P<DST>\S+)\s*"
    r"LEN=(?P<LEN>\d+)\s*"
    r"TOS=(?P<TOS>\S+)\s*"
    r"PREC=(?P<PREC>\S+)\s*"
    r"TTL=(?P<TTL>\d+)\s*"
    r"ID=(?P<ID>\d+)\s*"
    r"(DF\s+)?"
    r"PROTO=(?P<PROTO>\w+)\s*"
    r"(SPT=(?P<SPT>\d+)\s*)?"
    r"(DPT=(?P<DPT>\d+)\s*)?"
    r"(WINDOW=(?P<WINDOW>\d+)\s*)?"
    r"(RES=(?P<RES>\S+)\s*)?"
    r"(ACK\s+)?"
    r"((?P<flags>\S+)\s*)?"
    r"(URGP=(?P<URGP>\d+))?"
)
def get_info_log(log_line):
    """ 
    Parse a log line and return a dictionary with the extracted information.
    If the log line doesn't match the pattern, return an empty dictionary.
    """
    match = re.match(pattern, log_line)
    if match:
        data = match.groupdict()

        data['rule'] = " ".join(data['rule'].strip("_").split("_"))

        flags = data.pop('flags', '').split() 
        for flag in flags:
            data[flag] = "Yes"

        data['DF'] = "Yes" if data.get('DF') else "No"
        data['ACK'] = "Yes" if data.get('ACK') else "No"

        for key in match.groupdict().keys():
            if key not in data:
                data[key] = None

        return data 
    else:
        print({"log_line": log_line})
        print("No match.")
        return {}
def run_command(command):
    """function to run commande"""
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

def get_data_system():
    """ 
    Function to get system data
    """
    cmd_redirect='sudo journalctl -f -g "___nftables_logs_rule" | grep -v "COMMAND=/usr/bin/journalctl" >> /var/log/nftables/nftables.log'
    output, error = run_command(cmd_redirect)
    if error:
        return error
    else:
        cmd="sudo cat /var/log/nftables/nftables.log"
        output, error = run_command(cmd)
        if error:
            return error
        else:
            for line in output.splitlines():
                data = get_info_log(line)
                # print(data)
                if data:
                    data_csv={
                        "log":line.strip(),
                        "timestamp":data['timestamp'],
                        "rule": data['rule'],
                        "interfaces":data["IN"],
                        "out_mac":data['OUT'],
                        "src_ip":data['SRC'],
                        "dst_ip":data['DST'],
                        "len_trame":data['LEN'],
                        "TOS":data['TOS'],
                        "PREC":data['PREC'],
                        "TTL":data['TTL'],
                        "ID":data['ID'],
                        "DF":data['DF'],
                        "protocole":data['PROTO'],
                        "src_port":data['SPT'],
                        "dst_port":data['DPT'],
                        "window_size":data['WINDOW'],
                        "RES":data['RES'],
                        "ACK":data['ACK'],
                        "URGP":data['URGP']
                    }
                    yield data_csv
                    

def save_logs_db(data_csv):
    """function to save data in database"""
    all_log_db = FirewallLog.objects.all().values('log')
    for x in all_log_db:
        if x['log'].strip() not in data_csv:
            FirewallLog.objects.filter(log=x['log'].strip()).delete()
            # print("logs deleted ====>",x['log'])
    for data in data_csv:
        if not FirewallLog.objects.filter(log=data['log'].strip()).exists():
            logs_serializer=FirewallLogsSerializer(data=data)
            if logs_serializer.is_valid():
                logs_serializer.save()
                # print("logs added ===>",data)
            else:
                print (logs_serializer.errors)
        # else:
        #     print("log exist=============>",data['log'])
    return True
