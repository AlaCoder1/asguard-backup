from django.shortcuts import render
from managementUsers.views import *
from managementUsers.models import User
from django.contrib.auth.decorators import login_required

# @login_required(login_url='/')
def index_page(request):
    usr=getAllUsers(request)
    context = {'users':usr}
    print(context)
    return render(request, 'index_page.html',context)

# @login_required(login_url='/')
def lan_page(request):
    return render(request, 'lan_page.html')

# @login_required(login_url='/')
def settings_page(request):
    return render(request, 'settings_page.html')

def login(request):
    usr=getAllUsers(request)
    context = {'users':usr}
    return render(request, 'login.html',context)

def index_page_test(request):
    
    tab = "fefef"
    context = {'tab':tab}
    return render(request, 'index_page_test.html' ,context)