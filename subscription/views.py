from django.shortcuts import render
from .form import *
from .models import *
# Create your views here.


def add_plan(request):
    msg=''
    form = AddplanForm()
    if request.method == 'POST':
        form = AddplanForm(request.POST)
        
        if form.is_valid():
            form.save()
            msg = "plan addes successfully"
                    
    context = {'form': form,'msg':msg}
    return render(request, 'add_plan.html', context)


def add_organizations(request):
    msg=''
    form = addorganizationForm()
    if request.method == 'POST':
        form = addorganizationForm(request.POST)
        
        if form.is_valid():
            form.save()
            msg = "organization addes successfully"
                    
    context = {'form': form,'msg':msg}
    return render(request, 'add_organization.html', context)


def add_paymentTransaction(request):
    msg=''
    form = AddpaymentTransactionForm()
    if request.method == 'POST':
        form = AddpaymentTransactionForm(request.POST)
        
        if form.is_valid():
            form.save()
            msg = "paymentTransaction addes successfully"
                    
    context = {'form': form,'msg':msg}
    return render(request, 'add_paymentTransaction.html', context)


def add_plansSubscription(request):
    msg=''
    form = AddplansSubscriptionForm()
    if request.method == 'POST':
        form = AddplansSubscriptionForm(request.POST)
        
        if form.is_valid():
            form.save()
            msg = "plansSubscription addes successfully"
            
    context = {'form': form,'msg':msg}
    return render(request, 'add_plansSubscription.html', context)


def add_plansFeatures(request):
    msg=''
    form = AddplansFeaturesForm()
    if request.method == 'POST':
        form = AddplansFeaturesForm(request.POST)
        
        if form.is_valid():
            form.save()
            msg = "plansFeatures addes successfully"
                    
    context = {'form': form,'msg':msg}
    return render(request, 'add_plansFeatures.html', context)