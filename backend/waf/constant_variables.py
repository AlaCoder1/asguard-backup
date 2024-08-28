PATH_NGINX = "/etc/nginx/"
PATH_MODESC = f"{PATH_NGINX}modsec/"
PATH_NGINX_SITES_AVAILABLE = f"{PATH_NGINX}sites-available/"
PATH_NGINX_SITES_ENABLED = f"{PATH_NGINX}sites-enabled/"
PATH_ASGUARD_CONFIG = f"{PATH_NGINX_SITES_ENABLED}asguard.conf"
PATH_WAF_CONFIG = f"{PATH_MODESC}modsecurity.conf"
PATH_MAIN_WAF = f"{PATH_MODESC}main.conf"
PATH_CRS_SETUP = "/usr/local/modsecurity-crs/crs-setup.conf"
PATH_RULES_WAF = "/usr/local/modsecurity-crs/rules/{}.conf"
PATH_LOG = "/var/log/"
PATH_LOG_WAF = f"{PATH_LOG}modsec_audit.log"
PATH_LOG_BACKUP = f"{PATH_LOG}modsec_backup/"

CONSTANT_WAF_CONFIG = "WAF Config"
CONSTANT_WAF_RULE = "WAF Rule"

CONSTANT_XML_REQUEST = '''SecRule REQUEST_HEADERS:Content-Type "^(?:application(?:/soap\+|/)|text/)xml" \\
     "id:'200000',phase:1,t:none,t:lowercase,pass,nolog,ctl:requestBodyProcessor=XML"'''
CONSTANT_XML_REQUEST_COMMENTED = '''#SecRule REQUEST_HEADERS:Content-Type "^(?:application(?:/soap\+|/)|text/)xml" \\
#     "id:'200000',phase:1,t:none,t:lowercase,pass,nolog,ctl:requestBodyProcessor=XML"'''

CONSTANT_JSON_REQUEST = '''SecRule REQUEST_HEADERS:Content-Type "^application/json" \\
     "id:'200001',phase:1,t:none,t:lowercase,pass,nolog,ctl:requestBodyProcessor=JSON"'''
CONSTANT_JSON_REQUEST_COMMENTED = '''#SecRule REQUEST_HEADERS:Content-Type "^application/json" \\
#     "id:'200001',phase:1,t:none,t:lowercase,pass,nolog,ctl:requestBodyProcessor=JSON"'''

LIST_RULES_WAF = [{"id": "900", "name": "REQUEST-900-EXCLUSION-RULES-BEFORE-CRS", 
                   "description_french": "", 
                   "description_english": ""},
                  {"id": "901", "name": "REQUEST-901-INITIALIZATION", 
                   "description_french": "Initialise les règles de base et effectue les actions préparatoires. Il corrige également les erreurs et omissions des définitions de variables dans le fichier crs-setup.conf.", 
                   "description_english": "Initializes the basic rules and performs preparatory actions. It also corrects errors and omissions of variable definitions in the crs-setup.conf file."},
                  {"id": "905", "name": "REQUEST-905-COMMON-EXCEPTIONS", 
                   "description_french": "Définir des exceptions aux règles de sécurité afin de prévenir les faux positifs courants, en excluant certaines requêtes spécifiques de l'application des règles standard. ", 
                   "description_english": "Define exceptions to security rules to prevent common false positives, by excluding certain specific requests from the application of standard rules. "},
                  {"id": "911", "name": "REQUEST-911-METHOD-ENFORCEMENT", 
                   "description_french": "Impose des restrictions sur les méthodes HTTP, permettant uniquement les méthodes autorisées (ex. GET, POST) et bloquant les méthodes potentiellement dangereuses pour renforcer la sécurité de l'application.", 
                   "description_english": "Enforces restrictions on HTTP methods, allowing only approved methods (e.g., GET, POST) and blocking potentially dangerous ones to enhance application security. "},
                  {"id": "913", "name": "REQUEST-913-SCANNER-DETECTION", 
                   "description_french": "Configurer des règles spécifiques pour détecter les activités de scan réseau et protéger les systèmes contre ces menaces. ", 
                   "description_english": "Configure specific rules to detect network scanning activities and protect systems against these threats. "},
                  {"id": "920", "name": "REQUEST-920-PROTOCOL-ENFORCEMENT", 
                   "description_french": "Le but de cette règle est de respecter les exigences HTTP RFC qui indiquent comment le client est censé interagir avec le serveur. ", 
                   "description_english": "The purpose of this rule is to enforce HTTP RFC requirements that state how the client is supposed to interact with the server. "},
                  {"id": "921", "name": "REQUEST-921-PROTOCOL-ATTACK", 
                   "description_french": "Détecte et atténue les attaques exploitant les vulnérabilités des protocoles. Il identifie les motifs de trafic malveillant, bloque les requêtes nuisibles, génère des alertes et enregistre les tentatives d'attaque pour analyse. ", 
                   "description_english": "Configuration file detects and mitigates attacks that exploit protocol vulnerabilities. It identifies malicious traffic patterns, blocks harmful requests, and generates alerts while logging attack attempts for analysis. "},
                  {"id": "922", "name": "REQUEST-922-MULTIPART-ATTACK", 
                   "description_french": "Résoudre la vulnérabilité 3UWMWA6W. Il nécessite la version 2.9.6 ou 3.0.8 de ModSecurity  ou un moteur compatible prenant en charge ces modifications.", 
                   "description_english": "Address the 3UWMWA6W vulnerability. It requires ModSecurity version 2.9.6 or 3.0.8 or a compatible engine supporting these changes."},
                  {"id": "930", "name": "REQUEST-930-APPLICATION-ATTACK-LFI", 
                   "description_french": "Détecter et prévenir les attaques par inclusion de fichiers locaux (LFI). Il identifie les tentatives d'inclusion de fichiers locaux malveillants, bloque ces requêtes et génère des alertes. Les activités suspectes sont enregistrées pour une analyse ultérieure. ", 
                   "description_english": "Detect and prevent Local File Inclusion (LFI) attacks. It identifies attempts to include malicious local files, blocks these requests, and generates alerts. Suspicious activities are logged for further analysis. "},
                  {"id": "931", "name": "REQUEST-931-APPLICATION-ATTACK-RFI", 
                   "description_french": "Détecter et prévenir les attaques de type Remote File Inclusion (RFI). Il identifie les tentatives d'inclusion de fichiers distants malveillants, bloque ces requêtes et génère des alertes. Les activités suspectes sont enregistrées pour une analyse ultérieure. ", 
                   "description_english": "Detect and prevent Remote File Inclusion (RFI) attacks. It identifies attempts to include malicious remote files, blocks these requests, and generates alerts. Suspicious activities are logged for further analysis. "},
                  {"id": "932", "name": "REQUEST-932-APPLICATION-ATTACK-RCE", 
                   "description_french": "Détecter et prévenir les attaques par exécution de code à distance (RCE). Il identifie les tentatives d'exécution de code malveillant à distance, bloque ces requêtes et génère des alertes. Les activités suspectes sont enregistrées pour une révision ultérieure. ", 
                   "description_english": "Configuration file is designed to detect and prevent Remote Code Execution (RCE) attacks. It identifies attempts to execute malicious code remotely, blocks these requests, and generates alerts. Suspicious activities are logged for further review. "},
                  {"id": "933", "name": "REQUEST-933-APPLICATION-ATTACK-PHP", 
                   "description_french": "Détecter et prévenir les attaques ciblant les applications PHP. Il identifie les tentatives d'exploitation de vulnérabilités PHP, bloque les requêtes malveillantes et génère des alertes. Les activités suspectes sont également enregistrées pour analyse. ", 
                   "description_english": "Detect and prevent attacks targeting PHP applications. It identifies attempts to exploit PHP vulnerabilities, blocks malicious requests, and generates alerts. Suspicious activities are also logged for analysis. "},
                  {"id": "934", "name": "REQUEST-934-APPLICATION-ATTACK-GENERIC", 
                   "description_french": "Détecter et prévenir les attaques génériques contre les applications. Il identifie et bloque divers modèles d'attaques courantes, génère des alertes pour les activités suspectes et enregistre ces événements pour une analyse approfondie. ", 
                   "description_english": "Detect and prevent generic application attacks. It identifies and blocks a range of common attack patterns, generates alerts for suspicious activities, and logs these events for further analysis. "},
                  {"id": "941", "name": "REQUEST-941-APPLICATION-ATTACK-XSS", 
                   "description_french": "Détecter et prévenir les attaques par Cross-Site Scripting (XSS). Il identifie les tentatives d'injection de scripts malveillants dans les pages web, bloque ces requêtes et génère des alertes. Les activités suspectes sont également enregistrées pour une révision ultérieure. ", 
                   "description_english": "Detect and prevent Cross-Site Scripting (XSS) attacks. It identifies attempts to inject malicious scripts into web pages, blocks such requests, and generates alerts. Suspicious activities are logged for further review. "},
                  {"id": "942", "name": "REQUEST-942-APPLICATION-ATTACK-SQLI", 
                   "description_french": "Détecter et prévenir les attaques par injection SQL (SQLi). Il identifie les tentatives d'injection de requêtes SQL malveillantes, bloque ces requêtes et génère des alertes. Les activités suspectes sont enregistrées pour une analyse ultérieure. ", 
                   "description_english": "Detect and prevent SQL Injection (SQLi) attacks. It identifies attempts to inject malicious SQL queries, blocks these requests, and generates alerts. Suspicious activities are logged for further analysis. "},
                  {"id": "943", "name": "REQUEST-943-APPLICATION-ATTACK-SESSION-FIXATION", 
                   "description_french": "Détecter et prévenir les attaques par fixation de session. Il identifie les tentatives d'exploiter des identifiants de session pour détourner des sessions utilisateurs, bloque ces requêtes et génère des alertes. Les activités suspectes sont enregistrées pour une analyse ultérieure. ", 
                   "description_english": "Detect and prevent session fixation attacks. It identifies attempts to exploit session IDs to hijack user sessions, blocks such requests, and generates alerts. Suspicious activities are logged for further review. "},
                  {"id": "944", "name": "REQUEST-944-APPLICATION-ATTACK-JAVA", 
                   "description_french": "Détecter et prévenir les attaques ciblant les applications Java. Il identifie les tentatives d'exploitation des vulnérabilités Java, bloque les requêtes malveillantes et génère des alertes. Les activités suspectes sont également enregistrées pour une analyse approfondie ", 
                   "description_english": "Detect and prevent attacks targeting Java applications. It identifies attempts to exploit Java vulnerabilities, blocks malicious requests, and generates alerts. Suspicious activities are also logged for further analysis. "},
                  {"id": "949", "name": "REQUEST-949-BLOCKING-EVALUATION", 
                   "description_french": "Evaluer et appliquer les règles de blocage. Il évalue l'efficacité des mécanismes de blocage, applique les actions de blocage en fonction des résultats d'évaluation et génère des alertes. Les activités suspectes et les résultats d'évaluation sont enregistrés pour analyse. ", 
                   "description_english": "Evaluate and enforce blocking rules. It assesses the effectiveness of blocking mechanisms, applies block actions based on evaluation results, and generates alerts. Suspicious activities and evaluation results are logged for analysis. "},
                  {"id": "950", "name": "RESPONSE-950-DATA-LEAKAGES", 
                   "description_french": "Détecter et prévenir les fuites de données. Il identifie les tentatives d'exfiltration de données sensibles, bloque ces actions et génère des alertes. Les événements de fuite de données sont également enregistrés pour une analyse ultérieure. ", 
                   "description_english": "Detect and prevent data leakages. It identifies attempts to exfiltrate sensitive data, blocks such actions, and generates alerts. Data leakage events are also logged for further analysis "},
                  {"id": "951", "name": "RESPONSE-951-DATA-LEAKAGES-SQL", 
                   "description_french": "Se concentre sur la détection de fuites de données potentielles via des messages d'erreur SQL ou des informations de base de données sensibles dans les réponses HTTP.  ", 
                   "description_english": "Focuses on detecting potential data leakage through SQL error messages or sensitive database information in HTTP responses.  "},
                  {"id": "952", "name": "RESPONSE-952-DATA-LEAKAGES-JAVA", 
                   "description_french": "Détecter et prévenir les fuites de données spécifiques aux applications Java. Il identifie les tentatives d'exfiltration de données sensibles depuis des environnements Java, bloque ces actions et génère des alertes. Les événements de fuite de données sont également enregistrés pour une analyse ultérieure ", 
                   "description_english": "Detect and prevent data leakages specific to Java applications. It identifies attempts to exfiltrate sensitive data from Java environments, blocks such actions, and generates alerts. Data leakage events are logged for further analysis. "},
                  {"id": "953", "name": "RESPONSE-953-DATA-LEAKAGES-PHP", 
                   "description_french": "Détecter et prévenir les fuites de données spécifiques aux applications PHP. Il identifie les tentatives d'exfiltration de données sensibles depuis des environnements PHP, bloque ces actions et génère des alertes. Les événements de fuite de données sont également enregistrés pour une analyse ultérieure. ", 
                   "description_english": "Detect and prevent data leakages specific to PHP applications. It identifies attempts to exfiltrate sensitive data from PHP environments, blocks such actions, and generates alerts. Data leakage events are also logged for further analysis. "},
                  {"id": "954", "name": "RESPONSE-954-DATA-LEAKAGES-IIS", 
                   "description_french": "Conçue pour détecter et empêcher la fuite d'informations sensibles spécifiques à Microsoft IIS (Internet Information Services) dans les réponses HTTP. ", 
                   "description_english": "Conçue pour détecter et empêcher la fuite d'informations sensibles spécifiques à Microsoft IIS (Internet Information Services) dans les réponses HTTP. "},
                  {"id": "955", "name": "RESPONSE-955-WEB-SHELLS", 
                   "description_french": "Détecter et prévenir les attaques par web shells. Il identifie les tentatives de téléchargement ou d'exécution de web shells malveillants, bloque ces actions et génère des alertes. Les activités suspectes liées aux web shells sont également enregistrées pour une analyse ultérieure. ", 
                   "description_english": "Detect and prevent web shell attacks. It identifies attempts to upload or execute malicious web shells, blocks these actions, and generates alerts. Suspicious activities related to web shells are logged for further analysis. "},
                  {"id": "959", "name": "RESPONSE-959-BLOCKING-EVALUATION", 
                   "description_french": "Evaluer et appliquer les règles de blocage. Il analyse l'efficacité des mécanismes de blocage en place, ajuste les actions de blocage si nécessaire et génère des alertes. Les résultats de l'évaluation et les actions de blocage sont enregistrés pour une analyse approfondie. ", 
                   "description_english": "Evaluate and enforce blocking rules. It assesses the effectiveness of existing blocking mechanisms, adjusts blocking actions as needed, and generates alerts. Evaluation results and blocking actions are logged for further analysis. "},
                  {"id": "980", "name": "RESPONSE-980-CORRELATION", 
                   "description_french": "Utilisé en post-traitement après l'envoi de la réponse au client (dans la phase de journalisation). Son objectif est de fournir une corrélation entrante et sortante des événements afin de fournir une désignation plus intelligente du résultat de la transaction. ", 
                   "description_english": "Used in post processing after the response has been sent to the client (in the logging phase).  Its purpose is to provide inbound+outbound correlation of events to provide a more intelligent designation as to the outcome or result of the transaction. "},
                  {"id": "999", "name": "RESPONSE-999-EXCLUSION-RULES-AFTER-CRS", 
                   "description_french": "Définir des règles d'exclusion après l'application du Core Rule Set (CRS). Il spécifie des exceptions aux règles du CRS, permettant à certains trafics de contourner les protections du CRS. Ce fichier est destiné à la personnalisation pour ajuster les exclusions de règles et éviter les faux positifs. ", 
                   "description_english": "Specify exclusion rules after the Core Rule Set (CRS) is applied. It defines exceptions to CRS rules, allowing certain traffic to bypass the CRS protections. This file is intended for customization to fine-tune rule exclusions and avoid false positives."}
                  ]
