from django.shortcuts import render
from managementUsers.views import *

def index_page(request):
    users = getAllUsers(request)
    print(users)
    context = {'users':users}
    return render(request, 'index_page.html',context)

def index_page_test(request):
    
    tab = "fefef"
    context = {'tab':tab}
    return render(request, 'index_page_test.html' ,context)