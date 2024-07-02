import subprocess
from django.core.management.base import BaseCommand
from django.db import IntegrityError
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            output=[
            "[Unit]",
            "Description=Asguard Config interfaces",
            "[Service]",
            "Type=oneshot",
            "ExecStart=/usr/bin/true",
            "",
            "[Install]",
            "WantedBy=multi-user.target",
            ]

            command ="""sudo cat <<EOF > /etc/systemd/system/Asguard-Networking.service
{}
EOF""".format('\n'.join(output))
            completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = completed_process.stdout
            error = completed_process.stderr
            if error=="":
                return "Asguard service initialized successfully!"
            else:
                return error
        except IntegrityError as e:
            return "Error: " + str(e)