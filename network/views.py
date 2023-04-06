from django.http import JsonResponse
from .models import *
from settings.serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
import json
from django.core import serializers

# Create your views here.
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.1.12.34', username='root', password='root')
@csrf_exempt
def testPostNetwork(request):
    msg = ''
    if (request.method == 'POST'):
        # parse the incoming information
        data = JSONParser().parse(request)
        print(data)
        return JsonResponse({"msg": msg}, status=201)


@csrf_exempt
def testGetNetwork(request):
    msg = ''
    if (request.method == 'GET'):
        path="/org/freedesktop/NetworkManager/Settings/1"
        stdin, stdout, stderr = ssh.exec_command('export $(dbus-launch); python3 -c \'import dbus;bus=dbus.SystemBus();proxy = bus.get_object("org.freedesktop.NetworkManager", "{}");prop_iface=dbus.Interface(proxy,"org.freedesktop.DBus.Properties");connection=prop_iface.GetAll("org.freedesktop.NetworkManager.Settings.Connection");print(prop_iface.Get("org.freedesktop.NetworkManager.Settings.Connection","Filename"));print(connection);prop_iface1=dbus.Interface(proxy,"org.freedesktop.NetworkManager.Settings.Connection");c_settings=prop_iface1.GetSettings();print(c_settings)\''.format(path))
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8')
        return JsonResponse({"output": output,"error":error}, status=201)
# ssh.close()