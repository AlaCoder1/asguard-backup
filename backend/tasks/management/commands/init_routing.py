from django.core.management.base import BaseCommand
from django.db import IntegrityError

from backend.routing.constant_variables import PATH_ROUTING
from utils.commands_utils import execute_list_commands_without_arguments, get_current_directory


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            current_dir = get_current_directory()
            with open(PATH_ROUTING.format(current_dir)) as routing_file:
                routing_lines = routing_file.readlines()
            # Remove empty lines
            routing_lines = [x.replace('\n', '').split() for x in routing_lines if x != '\n']
            execute_list_commands_without_arguments(routing_lines)

            return "Routing added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)
