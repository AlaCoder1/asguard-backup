from django.shortcuts import render
from managementUsers.views import *
from managementUsers.models import User
from django.contrib.auth.decorators import login_required


def getUsers(request):
    list_users = []
    if (request.method == 'GET'):
        users = User.objects.all()
        userDict = serializers.serialize("json", users)
        res = json.loads(userDict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields'].pop('password')
            res[i]['fields'].pop('last_login')
            res[i]['fields'].pop('token_last_expired')
            res[i]['fields']['id'] = id
            if len(res[i]['fields']['group'])!=0:
                # print({"gggg":res[i]['fields']['group']})
                group=Group.objects.get(id=res[i]['fields']['group'][0])
                groupDict={"name":group.groupname,"id":group.id}
                # print({"groupppppppp":groupDict})
                res[i]['fields']['group']=groupDict
            list_users.append(res[i]['fields'])
        return list_users
# @login_required(login_url='/')
def index_page(request):
    usr=getUsers(request)
    context = {'users':usr}
    print(context)
    return render(request, 'index_page.html',context)

def login(request):
    usr=getAllUsers(request)
    context = {'users':usr}
    return render(request, 'login.html',context)

def index_page_test(request):
    
    tab = "fefef"
    context = {'tab':tab}
    return render(request, 'index_page_test.html' ,context)