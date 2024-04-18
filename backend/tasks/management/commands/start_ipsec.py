from django.core.management.base import BaseCommand
from django.db import IntegrityError
from backend.ipsec.server_ipsec import change_status_ipsec_in_system

from utils.constant_variables import SUCCESS_MESSAGES_START


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            change_status_ipsec_in_system("start")

            return SUCCESS_MESSAGES_START.format("IPsec", "")
        except IntegrityError as e:
            return "Error: " + str(e)
