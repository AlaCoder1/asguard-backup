import subprocess
import yaml

from backend.ids_ips.models import ids_ips_rule 

def execute_cmd(command):
    command="sudo "+command
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

#*********** Fichier de configuration suricata.yaml ****************
    
#Lire le fichier de configuration suricata.yaml//
def read_config():
    suricata_yaml_path = "/etc/suricata/suricata.yaml"
    syslog_enabled = None
    mpm_algo = None
    try:
        output,_ = execute_cmd("cat " + suricata_yaml_path)
        if output:
            lines = output.strip('\n').split('\n')
            home_net = None
            promisc = None
            eve_log_enabled = None
            profile = None
            copy_mode = None
            next_line = False  # Variable pour suivre si la ligne suivante doit être lue
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("#"):
                    continue  # Ignorer les lignes de commentaires
                if "HOME_NET:" in stripped_line:
                    home_net = stripped_line.split(":")[1].strip()
                if "promisc:" in stripped_line:
                    promisc = stripped_line.split(":")[1].strip()
                if "eve-log:" in stripped_line:
                    next_line = True  # Activer la lecture de la ligne suivante
                elif next_line:
                    eve_log_enabled = stripped_line.split(":")[1].strip()
                    next_line = False  
                # Utiliser la fonction pour lire la première occurrence de "syslog" et "enabled"
                if "syslog:" in stripped_line and syslog_enabled is None:
                    syslog_enabled = read_first_syslog_enabled(suricata_yaml_path)
                # Ajout de la lecture de "mpm-algo"
                if "mpm-algo:" in stripped_line:
                    mpm_algo = stripped_line.split(":")[1].strip()
                if "profile:" in stripped_line:
                    profile = stripped_line.split(":")[1].strip()
                if "copy-mode:" in stripped_line:
                    copy_mode= stripped_line.split(":")[1].strip()  
            return {"HOME_NET": home_net, "promisc": promisc, "eve-log-enabled": eve_log_enabled, "syslog-enabled": syslog_enabled, "mpm-algo": mpm_algo, "profile": profile, "copy-mode": copy_mode }
        else:
            return None
    except FileNotFoundError:
        return None
    except yaml.YAMLError :
        return None
   
# Fonction pour lire la première occurrence de "syslog" et "enabled"//
def read_first_syslog_enabled(suricata_yaml_path):
    syslog_enabled = None
    try:
        output,_= execute_cmd("cat "+suricata_yaml_path)
        lines = output.split('\n')
        skip_next_line = False
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("#"):
                continue  # Ignorer les lignes de commentaire
            if "syslog:" in stripped_line and syslog_enabled is None:
                skip_next_line = True  # Activer la lecture de la ligne suivante
            elif skip_next_line:
                # La ligne suivante après "syslog" est "enabled:"
                syslog_enabled = stripped_line.split(":")[1].strip()
                break  # Sortir de la boucle après avoir trouvé la première occurrence de "syslog:"
    except Exception :
        return None
        # print(f"Erreur lors de la lecture du fichier {suricata_yaml_path}: {e}")
    return syslog_enabled  

#Update fichier de configuration suricata.yaml//
def update_suricata_config(suricata_yaml_path,lines,home_net_value_sys,ifname, status_enabled,new_promisc, new_eve_log, new_syslog, new_mpm_algo, new_profile, new_copy_mode):    
    try:
        updated_lines = []
        next_eve_log = False
        next_syslog = False
        syslog_enabled = None
        af_packet=False
        # Ajout de la logique de testa() ici
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("#"):
                updated_lines.append(line + '\n')
            elif "HOME_NET:" in stripped_line:
                updated_lines.append(f'    HOME_NET: "{home_net_value_sys}"' + '\n')
            elif "promisc:" in stripped_line:
                # Met à jour la ligne promisc avec la nouvelle valeur
                updated_lines.append(f'      promisc: {new_promisc}\n')
            elif "af-packet:" in stripped_line:
                af_packet=True
                updated_lines.append(line + '\n')  # Conserve la ligne "af-packet:" telle quelle
            elif af_packet:
                if "interface:" in stripped_line:
                    updated_lines.append(f'  - interface: {ifname}\n')
                    af_packet = False
            elif "eve-log:" in stripped_line:
                next_eve_log = True  # Activer la lecture de la ligne suivante sous "eve-log"
                updated_lines.append(line + '\n')  # Conserve la ligne "eve-log" telle quelle
            elif next_eve_log:
                if "enabled:" in stripped_line:
                    # Met à jour la ligne "enabled" sous "eve-log" avec la nouvelle valeur
                    updated_lines.append(f'      enabled: {new_eve_log}\n')
                    next_eve_log = False
            elif "syslog:" in stripped_line:
               next_syslog = True  # Activer la lecture de la ligne suivante
               updated_lines.append(line + '\n') 
            elif next_syslog:
                if "enabled:" in stripped_line:
                    # Met à jour la ligne "enabled" sous "syslog" avec la nouvelle valeur
                    updated_lines.append(f'      enabled: {new_syslog}\n')
                    next_syslog = False
            elif "mpm-algo:" in stripped_line:
                # Met à jour la ligne mpm-algo avec la nouvelle valeur
                updated_lines.append(f'mpm-algo: {new_mpm_algo}\n')
            elif "profile:" in stripped_line:
                # Met à jour la ligne profile avec la nouvelle valeur
                updated_lines.append(f'  profile: {new_profile}\n')
            elif "copy-mode:" in stripped_line:
            # Met à jour la ligne copy-mode avec la nouvelle valeur
                updated_lines.append(f'      copy-mode: {new_copy_mode}\n')
            else:
                # Conserve les autres lignes telles quelles
                updated_lines.append(line + '\n')
        with open(suricata_yaml_path, 'w') as local_file:
            for string in updated_lines:
                local_file.write(string)

        if status_enabled is True:
            aux_enable="enable"
            aux_action="restart"
        else:
            aux_enable="disable"
            aux_action="stop"
        commands = [
        "sudo systemctl {} --quiet suricata.service && sudo systemctl {} suricata.service ".format(aux_enable,aux_action)
        ]
        for cmd in commands:
            _, error=execute_cmd(cmd)
            if error!="":
                print({"errot":error,"cmd":cmd})
                return error
            
        return True
    except Exception:
        # Capture toute autre exception et affiche un message d'erreur
        return None

#*********** Les régles ****************
#Format des régles    
def format_dict_as_suricata_rules(content):    
    rule_template = "{action} {protocol} {source_ip} {direction} {destination_ip} (msg:\"{msg}\"; rev:{rev};sid:{sid};)"
    rule_str = rule_template.format(
        action=content['action'],
        protocol=content['protocol'],
        source_ip=content['source_ip'],
        direction=content['direction'],
        destination_ip=content['destination_ip'],
        msg=content['msg'],
        rev=content['rev'],
        sid=content['sid']
    )
    return rule_str

# Ajouter une régle
def add_rule_remote(comment, content,file_path):
    formatted_content = format_dict_as_suricata_rules(content)
    if comment:
        formatted_content = "#" + formatted_content
    cmd = """sudo sh -c 'cat <<EOF >> {}
{}
EOF'""".format(file_path,formatted_content)
    output, error = execute_cmd(cmd)
    return output,formatted_content, error

# mise à jour une régle
def update_rule_remote(comment,contenu,line_to_update,file_path):
    rule = line_to_update.strip()  # Supprimez les espaces inutiles
    action=None
    protocol=None
    sid=None
    src_ip=None
    direction=None
    dest_ip=None
    msg=None
    rev=None
    rule=rule.strip()
    action=rule.split(" ")[0].strip()
    protocol=rule.split(" ")[1].strip()
    if rule.find("sid")!=-1:
        rule_inter=rule[rule.find("sid:"):]
        sid=int(rule_inter[rule_inter.find("sid:")+len("sid:"):rule_inter.find(";")])
    if rule[1:].find("->")!=-1:
        src_ip=rule[rule.find(protocol)+len(protocol):rule.find("->")].strip()
        direction="->"
        dest_ip=rule[rule.find("->")+len("->"):rule.find("(msg")].strip()
    if rule.find("msg:")!=-1:
        msg=rule[rule.find("msg:")+len("msg:"): rule.find('";')].strip()
    if rule.find("rev:")!=-1:
        rev=rule[rule.find("rev:")+len("rev:"): rule.find(";sid")].strip(";")
        if rev.isdigit():
            rev=int(rev)
        else:
            rev=None
    action=action if action!="" else None    
    protocol=protocol if protocol!="" else None  
    src_ip=src_ip if src_ip!="" else None    
    direction=direction if direction!="" else None  
    dest_ip=dest_ip if dest_ip!="" else None    
    msg=msg if msg!="" else None   
    protocol=protocol if protocol!="" else None
    if contenu['action'] is not None:
        if contenu["activate_rule"] is False:
            contenu['action']="#"+contenu['action']
        else:
            rule=rule.strip("#")
            contenu['action'].strip().strip("#")
        rule=rule.replace(action,contenu['action'])
    if contenu['protocol'] is not None:
        rule=rule.replace(protocol,contenu['protocol'])
    if  contenu['source_ip'] is not None:
        rule=rule.replace(src_ip,contenu['source_ip'])
        
    if  contenu['direction'] is not None:
        rule=rule.replace(direction,contenu['direction'])      
    
    if  contenu['destination_ip'] is not None:
        rule=rule.replace(dest_ip,contenu['destination_ip'])  

    if  contenu['msg'] is not None and rule.find("msg")!=-1:
        rule=rule.replace(msg,'"'+contenu['msg'])    
    
    if  contenu['rev'] is not None and rule.find("rev")!=-1:
        rule=rule.replace(str(rev),str(contenu['rev']))    
        
    if  contenu['sid'] is not None:
        rule=rule.replace(str(sid),str(contenu['sid']))   
        
    cmd = "sudo sed -i '/sid:{}/ s|{}|{}|' {}".format(sid, line_to_update.strip(), rule.strip(), file_path)
    output, error = execute_cmd(cmd)
    return output,rule, error

# //
def get_line_by_sid( sid):
    if ids_ips_rule.objects.filter(sid=sid):
        obj=ids_ips_rule.objects.get(sid=sid)
        rule=obj.rule
        return rule
    else:
        return None

        

def delete_line_in_remote_file(file_path, line_to_delete):
    try:
        # Read the contents of the file
        cmd_read = f"grep -v '{line_to_delete}' {file_path} > {file_path}.tmp && mv {file_path}.tmp {file_path}"
        output,error =execute_cmd(cmd_read)
        # Print the command output
        return output,error
    except Exception as e:
        return "Error:"+ str(e)

#Afficher les rules par défaut //
def get_suricata_default_rules():
    file_path = '/var/lib/suricata/rules/suricata.rules'
    try:
        # Utilisez la commande 'cat' pour lire le contenu du fichier
        cmd_read = f"cat {file_path}"
        output, error = execute_cmd(cmd_read)
        if not error:
            # La sortie de la commande contient le contenu du fichier
            rules = output.splitlines()
            return rules
        else:
            return None
            # print(f"Erreur lors de la lecture des règles : {error}")
    except Exception :
        # print(f"Erreur : {str(e)}")
        return []

###prepare rules attributs
def prepare_rule_attribut(rules):
    list_attributs_rules=[]
    for rule in rules:
        rule = rule.strip()  # Supprimez les espaces inutiles
        if len(rule)!=0:
            action=None
            protocol=None
            sid=None
            src_ip=None
            direction=None
            dest_ip=None
            msg=None
            rev=None
            rule=rule.strip(" ")
            # Vérifiez si la règle n'est pas vide
            if rule.startswith("#") is True:
                active=False
                action=rule.split(" ")[0].strip()+rule.split(" ")[1]
                protocol=rule.split(" ")[2].strip()
            else:
                active=True
                action=rule.split(" ")[0].strip()
                protocol=rule.split(" ")[1].strip()
            if rule.find("sid")!=-1:
                rule_inter=rule[rule.find("sid:"):]
                sid=int(rule_inter[rule_inter.find("sid:")+len("sid:"):rule_inter.find(";")])
            if rule[1:].find("->")!=-1:
                src_ip=rule[rule.find(protocol)+len(protocol):rule.find("->")].strip()
                direction="->"
                dest_ip=rule[rule.find("->")+len("->"):rule.find("(msg")].strip()
            if rule.find("msg:")!=-1:
                msg=rule[rule.find('msg:"')+len('msg:"'): rule.find('";')].strip()
            if rule.find("rev:")!=-1:
                rev=rule[rule.find("rev:")+len("rev:"): rule.find(";sid")].strip(";")
                if rev.isdigit():
                    rev=int(rev)
                else:
                    rev=None
            action=action if action!="" else None    
            protocol=protocol if protocol!="" else None  
            src_ip=src_ip if src_ip!="" else None    
            direction=direction if direction!="" else None  
            dest_ip=dest_ip if dest_ip!="" else None    
            msg=msg if msg!="" else None  
            protocol=protocol if protocol!="" else None  
            data = {
               "sid":sid,
                "action":action.strip().strip("#"),
                "protocol":protocol,
                "source_ip":src_ip,
                "direction":direction,
                "destination_ip":dest_ip,
                "msg":msg.strip().strip('"'),
                "rev":rev,
                "rule": rule,
                "suricatafile":id,
                "activate_rule":active,
                    "default_rule":True
                }
            list_attributs_rules.append(data)
    return list_attributs_rules
                    
#*********** Les alertes ****************//
def read_suricata_log():
    suricata_log_path = "/var/log/suricata/fast.log"
    logs = []
    try:
        cmd_read = f"sudo cat {suricata_log_path}"
        output, error = execute_cmd(cmd_read)
        if not error:
            lines = output.split('\n')
            logs=lines
        # Utilisation d'une expression régulière pour extraire le protocole
    except Exception as e:
        # print("Une exception s'est produite:", str(e))
        return None
    return logs

# function to split informations
def prepare_alert_attribut(lines):
    logs = []
    for line in lines:
        # Votre code de traitement ici
        attributes = line.split()
        if len(attributes)!=0:
            if  attributes[1]!="[**]" and attributes[1].startswith("["):
                attributes.remove(attributes[1])
            timestamp = attributes[0] + ' ' + attributes[1].replace("[**]", "",2)
            priority=attributes[-5][:1]
            protocol = attributes[-4][1:-1]
            src_addr=attributes[-3].split(":")[0]
            src_port=attributes[-3].split(":")[1]
            dst_addr=attributes[-1].split(":")[0]
            dst_port=attributes[-1].split(":")[1]
            sid=attributes[2].split(":")[1]
            attributes2=attributes[3:]
            message = ' '.join(attributes2[:attributes2.index("[**]")]).strip()
            # Afficher les attributs
            logs.append({
                "timestamp": timestamp,
                "sid":sid,
                "message": message,
                "priority": int(priority),
                "protocol": protocol,
                "src_addr": src_addr,
                "src_port": int(src_port),
                "dst_addr": dst_addr,
                "dst_port": int(dst_port),
                "alert":line.strip(),
                    })  
    return logs