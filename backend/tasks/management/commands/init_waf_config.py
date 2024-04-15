from django.core.management.base import BaseCommand
from django.db import IntegrityError

from backend.waf.models import ConfigWaf
from backend.waf.utils import change_waf_config_file
from utils.commands_utils import execute_command_without_arguments


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            config_waf = ConfigWaf()
            config_waf.save()
            return "WAF Config added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)
