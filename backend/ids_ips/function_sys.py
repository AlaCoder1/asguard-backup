import subprocess
import yaml 

def execute_cmd(command):
    command="sudo "+command
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = completed_process.stdout
    error = completed_process.stderr
    return output, error

#*********** Fichier de configuration suricata.yaml ****************

#Lire le fichier de configuration suricata.yaml//
def read_suricata_config():
    # Chemin vers le fichier suricata.yaml
    suricata_yaml_path = "/etc/suricata/suricataTest.yaml"
    try:
        output, error = execute_cmd("cat " + suricata_yaml_path)
        return output
    except FileNotFoundError:
        # print(f"Le fichier {suricata_yaml_path} n'a pas été trouvé.")
        return None

    
#Lire le fichier de configuration suricata.yaml//
def read_config():
    suricata_yaml_path = "/etc/suricata/suricataTest.yaml"
    syslog_enabled = None
    mpm_algo = None
    try:
        output,error = execute_cmd("cat " + suricata_yaml_path)
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
            # print(f"La commande a échoué : {error}")
            return None
    except FileNotFoundError:
        # print(f"Le fichier {suricata_yaml_path} n'a pas été trouvé.")
        return None
    except yaml.YAMLError as e:
        # print(f"Erreur lors de la lecture du fichier {suricata_yaml_path}: {e}")
        return None
   
# Fonction pour lire la première occurrence de "syslog" et "enabled"//
def read_first_syslog_enabled(suricata_yaml_path):
    suricata_yaml_path = "/etc/suricata/suricataTest.yaml" 
    syslog_enabled = None
    try:
        output,error= execute_cmd("cat "+suricata_yaml_path)
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
    except Exception as e:
        return None
        # print(f"Erreur lors de la lecture du fichier {suricata_yaml_path}: {e}")
    return syslog_enabled  

#Update fichier de configuration suricata.yaml//
def update_suricata_config( status_enabled,new_promisc, new_eve_log, new_syslog, new_mpm_algo, new_profile, new_copy_mode):    
    suricata_yaml_path = "/etc/suricata/suricataTest.yaml"
    try:
        cmd_read = f"sudo cat {suricata_yaml_path}"
        output ,error = execute_cmd(cmd_read)
        if not error:
            # Lit les lignes du fichier
            lines = output.split('\n')
            updated_lines = []
            next_eve_log = False
            next_syslog = False
            syslog_enabled = None
            # Ajout de la logique de testa() ici
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("#"):
                    updated_lines.append(line + '\n')
                elif "promisc:" in stripped_line:
                    # Met à jour la ligne promisc avec la nouvelle valeur
                    updated_lines.append(f'      promisc: {new_promisc}\n')
                elif "eve-log:" in stripped_line:
                    next_eve_log = True  # Activer la lecture de la ligne suivante sous "eve-log"
                    updated_lines.append(line + '\n')  # Conserve la ligne "eve-log" telle quelle
                elif next_eve_log:
                    if "enabled:" in stripped_line:
                        # Met à jour la ligne "enabled" sous "eve-log" avec la nouvelle valeur
                        updated_lines.append(f'      enabled: {new_eve_log}\n')
                        next_eve_log = False
                elif "syslog:" in stripped_line and  syslog_enabled is None:
                    syslog_enabled = read_first_syslog_enabled(suricata_yaml_path)
                    next_syslog = True  # Activer la lecture de la ligne suivante sous "syslog"
                    updated_lines.append(line + '\n')  # Conserve la ligne "syslog" telle quelle
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
             # Ouvre le fichier en écriture sur le serveur distant
            with open(suricata_yaml_path, 'w') as local_file:
                for string in updated_lines:
                    local_file.write(string)
                     
            if status_enabled is True:
                aux_enable="enable"
            else:
                aux_enable="disable"
            enable_command = "systemctl {} --quiet suricata.service ".format(aux_enable)
            output, error=execute_cmd(enable_command)
            if error=="":
                return True
        else:    
            return None
    except Exception as e:
        # Capture toute autre exception et affiche un message d'erreur
        # print(f"Erreur lors de la mise à jour du fichier {suricata_yaml_path}: {e}")
        return None

#*********** Les régles ****************


def return_rule(sid,action,protocol,source_ip,direction,destination_ip,msg,content,flowbit,rev):
   rule={sid:{"action":action,"protocol":protocol,"source_ip":source_ip,"direction":direction,"destination_ip":destination_ip,"msg":msg,"content":content,"flowbit":flowbit,"rev":rev,"sid":sid}}
   return rule

#Format des régles    
def format_dict_as_suricata_rules(content):    
    rule_template = "{action} {protocol} {source_ip} {direction} {destination_ip} (msg:\"{msg}\"; content:\"{content}\"; flowbit:\"{flowbit}\"; rev:{rev};sid:{sid};)"
    rule_str = rule_template.format(
        action=content['action'],
        protocol=content['protocol'],
        source_ip=content['source_ip'],
        direction=content['direction'],
        destination_ip=content['destination_ip'],
        msg=content['msg'],
        content=content['content'],
        flowbit=content['flowbit'],
        rev=content['rev'],
        sid=content['sid']
    )
    # if content['msg'] is None:
    #     rule_str=rule_str[:rule_str.find('msg:"None";')]+rule_str[rule_str.find('msg:"None";')+len('msg:"None";'):]
    # if content['content'] is None:
    #     rule_str=rule_str[:rule_str.find('content:"None";')]+rule_str[rule_str.find('content:"None";')+len('content:"None";'):]
    # if content['rev'] is None:
    #     rule_str=rule_str[:rule_str.find('rev:"None";')]+rule_str[rule_str.find('rev:"None";')+len('rev:"None";'):]
    # if content['flowbit'] is None:
    #     rule_str=rule_str[:rule_str.find('flowbit:"None";')]+rule_str[rule_str.find('flowbit:"None";')+len('flowbit:"None";'):]
    # print({"rule_str":rule_str})
    return rule_str

# Ajouter une régle
def add_rule_remote10(comment, content,file_path):
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
    content=None
    flowbit=None
    rev=None
    if rule.startswith("#") is True:
        action=rule.split(" ")[0].strip()
        protocol=rule.split(" ")[1].strip()
    else:
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
    if rule.find("content:")!=-1:
        rule_content=rule[rule.find("content:")+len("content:"):].strip()
        content=rule_content[:rule_content.find('";')]
    if rule.find("flowbit:")!=-1:
        rule_flowbit=rule[rule.find("flowbit:")+len("flowbit:"):]
        flowbit=rule_flowbit[:rule_flowbit.find(";")].strip()
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
    content=content if content!="" else None    
    protocol=protocol if protocol!="" else None
    flowbit=flowbit if flowbit!="" else None  
    if contenu['action'] is not None:
        if contenu["activate_rule"] is False:
            contenu['action']="#"+contenu['action']
        else:
            contenu['action'].strip("#")
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
        rule=rule.replace(msg,contenu['msg'])   
    
    if  contenu['content'] is not None and rule.find("msg")!=-1:
        rule=rule.replace(content,contenu['content'])   
            
    if  contenu['flowbit'] is not None:
        if rule.find("flowbit")!=-1:
            rule=rule.replace(flowbit,contenu['flowbit'])   
        # elif rule.find("msg")!=-1:
        #     rule=rule[:rule.find(contenu['msg'])+len(contenu['msg']+";")+1]+'content: '+content+";"+rule[rule.find(contenu['msg'])+len(contenu['msg']+";"):]
            
    
    if  contenu['rev'] is not None and rule.find("rev")!=-1:
        rule=rule.replace(str(rev),str(contenu['rev']))    
        
    if  contenu['sid'] is not None:
        rule=rule.replace(str(sid),str(contenu['sid']))   
        
    # cmd = "sed -i '/sid:{}/ s/{}/{}/' {}".format(sid,line_to_update,formatted_content,file_path)
    cmd = "sed -i '/sid:{}/ s/{}/{}/' {}".format(sid, line_to_update.strip(), rule.strip(), file_path)
    output, error = execute_cmd(cmd)
    
    return output,rule, error
# //
def get_line_by_sid(file_path, sid):
    try:
        # Utilisez la commande grep pour rechercher la ligne avec le SID dans le fichier
        cmd = f'grep -E "sid:{sid};" {file_path}'
        output, error = execute_cmd(cmd)
        if not error:
            # La sortie de la commande contient la ligne avec le SID
            return output
        else:
            return None
    except Exception as e:
        # print(f"Erreur : {str(e)}")
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
    file_path = '/var/lib/suricata/rules/suricataTest.rules'
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
    except Exception as e:
        # print(f"Erreur : {str(e)}")
        return []

#*********** Les alertes ****************//
def read_suricata_log():
    suricata_log_path = "/var/log/suricata/fast.log"
    logs = []
    try:
        cmd_read = f"cat {suricata_log_path}"
        output, error = execute_cmd(cmd_read)
        # print (stderr.read().decode())
        if not error:
            lines = output.split('\n')
            for line in lines:
                # Votre code de traitement ici
                attributes = line.split()
                if len(attributes)!=0:
                    timestamp = attributes[0] + ' ' + attributes[1].replace("[**]", "",2)
                    priority=attributes[-5][:1]
                    protocol = attributes[-4][1:-1]
                    src_addr=attributes[-3].split(":")[0]
                    src_port=attributes[-3].split(":")[1]
                    dst_addr=attributes[-1].split(":")[0]
                    dst_port=attributes[-1].split(":")[1]
                    sid=attributes[2].split(":")[1]
                    # Afficher les attributs
                    logs.append({
                        "timestamp": timestamp,
                        "sid":sid,
                        "priority": int(priority),
                        "protocol": protocol,
                        "src_addr": src_addr,
                        "src_port": int(src_port),
                        "dst_addr": dst_addr,
                        "dst_port": int(dst_port),
                        "alert":line.strip(),
                          })      
        # Utilisation d'une expression régulière pour extraire le protocole
    except Exception as e:
        # print("Une exception s'est produite:", str(e))
        return None
    return logs