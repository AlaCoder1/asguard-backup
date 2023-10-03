from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
import json

def real_time_data(request):
    return render(request, 'basedashboard.html',{})