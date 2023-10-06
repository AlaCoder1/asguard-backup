from django.shortcuts import render

def monitoring(request):
    return render(request, 'basedashboard.html',{})
