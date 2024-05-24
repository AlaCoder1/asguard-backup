PATH_NGINX = "/etc/nginx/"
PATH_MODESC = f"{PATH_NGINX}modsec/"
PATH_ASGUARD_CONFIG = f"{PATH_NGINX}sites-enabled/asguard.conf"
PATH_WAF_CONFIG = f"{PATH_MODESC}modsecurity.conf"
PATH_MAIN_WAF = f"{PATH_MODESC}main.conf"
PATH_RULES_WAF = "/usr/local/modsecurity-crs/rules/{}.conf"

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

LIST_RULES_WAF = [{"id": "900", "name": "REQUEST-900-EXCLUSION-RULES-BEFORE-CRS"},
                  {"id": "901", "name": "REQUEST-901-INITIALIZATION"},
                  {"id": "905", "name": "REQUEST-905-COMMON-EXCEPTIONS"},
                  {"id": "911", "name": "REQUEST-911-METHOD-ENFORCEMENT"},
                  {"id": "913", "name": "REQUEST-913-SCANNER-DETECTION"},
                  {"id": "920", "name": "REQUEST-920-PROTOCOL-ENFORCEMENT"},
                  {"id": "921", "name": "REQUEST-921-PROTOCOL-ATTACK"},
                  {"id": "922", "name": "REQUEST-922-MULTIPART-ATTACK"},
                  {"id": "930", "name": "REQUEST-930-APPLICATION-ATTACK-LFI"},
                  {"id": "931", "name": "REQUEST-931-APPLICATION-ATTACK-RFI"},
                  {"id": "932", "name": "REQUEST-932-APPLICATION-ATTACK-RCE"},
                  {"id": "933", "name": "REQUEST-933-APPLICATION-ATTACK-PHP"},
                  {"id": "934", "name": "REQUEST-934-APPLICATION-ATTACK-GENERIC"},
                  {"id": "941", "name": "REQUEST-941-APPLICATION-ATTACK-XSS"},
                  {"id": "942", "name": "REQUEST-942-APPLICATION-ATTACK-SQLI"},
                  {"id": "943", "name": "REQUEST-943-APPLICATION-ATTACK-SESSION-FIXATION"},
                  {"id": "944", "name": "REQUEST-944-APPLICATION-ATTACK-JAVA"},
                  {"id": "949", "name": "REQUEST-949-BLOCKING-EVALUATION"},
                  {"id": "950", "name": "RESPONSE-950-DATA-LEAKAGES"},
                  {"id": "951", "name": "RESPONSE-951-DATA-LEAKAGES-SQL"},
                  {"id": "952", "name": "RESPONSE-952-DATA-LEAKAGES-JAVA"},
                  {"id": "953", "name": "RESPONSE-953-DATA-LEAKAGES-PHP"},
                  {"id": "954", "name": "RESPONSE-954-DATA-LEAKAGES-IIS"},
                  {"id": "955", "name": "RESPONSE-955-WEB-SHELLS"},
                  {"id": "959", "name": "RESPONSE-959-BLOCKING-EVALUATION"},
                  {"id": "980", "name": "RESPONSE-980-CORRELATION"},
                  {"id": "999", "name": "RESPONSE-999-EXCLUSION-RULES-AFTER-CRS"}]
