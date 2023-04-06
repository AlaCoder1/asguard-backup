from django.shortcuts import render
from managementUsers.views import *
from managementUsers.models import User

def index_page(request):
    usr=getAllUsers(request)
    context = {'users':usr}
    return render(request, 'index_page.html',context)

def index_page_test(request):
    
    tab = "fefef"
    context = {'tab':tab}
    return render(request, 'index_page_test.html' ,context)