PATH_WAF_CONFIG = "/etc/nginx/modsec/modsecurity.conf"

CONSTANT_WAF_CONFIG = "WAF Config"

CONSTANT_XML_REQUEST = '''SecRule REQUEST_HEADERS:Content-Type "^(?:application(?:/soap\+|/)|text/)xml" \\
     "id:'200000',phase:1,t:none,t:lowercase,pass,nolog,ctl:requestBodyProcessor=XML"'''
CONSTANT_XML_REQUEST_COMMENTED = '''#SecRule REQUEST_HEADERS:Content-Type "^(?:application(?:/soap\+|/)|text/)xml" \\
#     "id:'200000',phase:1,t:none,t:lowercase,pass,nolog,ctl:requestBodyProcessor=XML"'''

CONSTANT_JSON_REQUEST = '''SecRule REQUEST_HEADERS:Content-Type "^application/json" \\
     "id:'200001',phase:1,t:none,t:lowercase,pass,nolog,ctl:requestBodyProcessor=JSON"'''
CONSTANT_JSON_REQUEST_COMMENTED = '''#SecRule REQUEST_HEADERS:Content-Type "^application/json" \\
#     "id:'200001',phase:1,t:none,t:lowercase,pass,nolog,ctl:requestBodyProcessor=JSON"'''
