from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.rules.models import Rule 
from backend.rules.views import * 
from backend.network.models import Interface

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--id', '--id', type=str, help='Define a id rule')
        parser.add_argument('-r', '--rule', type=str, help='Define a rule')
        parser.add_argument('-tp', '--type_rule', type=str, help='Define a type rule')
        parser.add_argument('-i', '--interface', type=str, help='Define a interface')
    def handle(self, *args, **options):
        try:
            id_rule = options.get('id')
            rule = options.get('rule')
            rule = rule.replace('-',' ')
            type_rule = options.get('type_rule')
            interface = options.get('interface')
            if rule.find("log prefix")!=-1:
                rule_mod=rule.split("log prefix")[0]
                rule_mod=rule_mod.replace(interface,'"'+interface+'"')
                rule_log=rule.split("log prefix")[1].strip()
                rule_log_msg='"'+'___'.join(rule_log.split("___")[:-1])+'___"'
                rule=rule_mod.strip()+' log prefix '+rule_log_msg+rule_log.split("___")[-1]
            else:
                rule = rule.replace(interface,'"'+interface+'"')
            
            try:
                handle=get_handle_rule(interface,type_rule,rule)
                if handle is not None:
                    return_delete_rule_remote=delete_rule_remote(interface,type_rule,handle)
                    if return_delete_rule_remote is True:
                        Rule.objects.filter(id=id_rule).delete()
                        return "rule deleted succesffuly"
                    else:
                        return return_delete_rule_remote
                else:
                    msg="Rule not exist in system!!"
                    return msg
            except IntegrityError as e:
                print("Error occurred:", e)
        except IntegrityError as e:
            return "Error: " + str(e)