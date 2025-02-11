from django.core.management.base import BaseCommand
from django.db import IntegrityError

from backend.waf.constant_variables import LIST_RULES_WAF, PATH_MAIN_WAF, PATH_RULES_WAF
from backend.waf.models import ConfigWaf, RulesWaf
from utils.commands_utils import execute_command_without_arguments, read_file_from_system
from utils.errors_utils import CommandExecutionError


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            # Initialization of WAF Configuration
            config_waf = ConfigWaf()
            config_waf.save()

            # Initialization of WAF Rules
            command = ["sudo", "cp", f"{PATH_RULES_WAF.format('RESPONSE-999-EXCLUSION-RULES-AFTER-CRS')}.example", 
                       f"{PATH_RULES_WAF.format('RESPONSE-999-EXCLUSION-RULES-AFTER-CRS')}"]
            execute_command_without_arguments(command)
            # Remove line that include all conf file (using *.conf) and set each line individually
            main_content = read_file_from_system(PATH_MAIN_WAF)
            with open(PATH_MAIN_WAF, 'w') as main_file:
                main_file.write(main_content.replace(f"\nInclude {PATH_RULES_WAF.format('*')}", ""))
            with open(PATH_MAIN_WAF, 'a') as main_file:
                # Create an empty file for created rules and add it to the main file
                with open(PATH_RULES_WAF.format('custom_rules'), 'w') as rule_file:
                    rule_file.write('')
                main_file.write(f"Include {PATH_RULES_WAF.format('custom_rules')}")

                # Add modsecrity rules to the main file and database
                for rule in LIST_RULES_WAF:
                    # Add modsecrity rules to the main file
                    main_file.write(f"\nInclude {PATH_RULES_WAF.format(rule['name'])}")
                    # Add modsecrity rules to the database with it's description in two languages
                    rule_waf = RulesWaf(name=rule['name'],
                                        description=rule['description_english'], 
                                        description_english=rule['description_english'], 
                                        description_french=rule['description_french'], 
                                        created=False, 
                                        rule_id=rule['id'])
                    rule_waf.save()
                
                # Add GEOIP rule to the main file
                main_file.write("""\nSecRule REMOTE_ADDR "@geoLookup" "phase:1,id:900001,log,pass,logdata:'Country: %{{GEO:COUNTRY_CODE}}, Latitude: %{{GEO:LATITUDE}}, Longitude: %{{GEO:LONGITUDE}}'" """)
            
            # Restart nginx service
            execute_command_without_arguments(["sudo", "systemctl", "restart", "nginx"])

            return "WAF Config added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)
        except CommandExecutionError:
            return "Error in initializing WAF modsecurity"
