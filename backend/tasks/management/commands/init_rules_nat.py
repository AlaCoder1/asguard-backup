from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.nat.contant_variables import INIT_NAT_FILE_CONTENT, PATH_NFTABLES_CONF, PATH_RULESET_NAT_DIRECTORY, PATH_RULESET_NFT

from utils.commands_utils import execute_command_without_arguments


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            execute_command_without_arguments(["mkdir", "-p", PATH_RULESET_NAT_DIRECTORY])
            with open(PATH_NFTABLES_CONF, "a") as nftables_file:
                nftables_file.write(f"include \"{PATH_RULESET_NFT}\";")
            with open(PATH_RULESET_NFT, "w") as ruleset_file:
                ruleset_file.write(INIT_NAT_FILE_CONTENT)
            execute_command_without_arguments(["sudo", "systemctl", "restart", "nftables"])

            return "NAT table added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)