from network.models import *
from django.core.management.base import BaseCommand


    def handle(self, *args, **kwargs):
        # Your code to add data to the database here
        try:
            User.objects.create(username='root', password=make_password("root"))
            return "root added succesffuly"
        except IntegrityError as e:
            return "Error: " + str(e)

cmd = "timedatectl list-timezones"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        error_str = stderr.read().decode('utf-8')
        listesOfTimezone = stdout.read().decode('utf-8').split('\n')
        listesOfTimezone.pop()
        print({"error_str":error_str})
        if error_str =='':
            for time_data in listesOfTimezone:
                timezone = Timezone(name=time_data)
                timezone.save()