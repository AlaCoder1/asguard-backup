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
    plans=plan.objects.all()       
    context = {'form': form,'msg':msg,'plans':plans}
    return render(request, 'add_plan.html', context)


def add_organizations(request):
    msg=''
    form = addorganizationForm()
    if request.method == 'POST':
        form = addorganizationForm(request.POST)
        if form.is_valid():
            form.save()
            msg = "organization addes successfully"
    organizations=organization.objects.all()               
    context = {'form': form,'msg':msg,'organizations':organizations}
    return render(request, 'add_organization.html', context)


def add_paymentTransaction(request):
    msg=''
    form = AddpaymentTransactionForm()
    if request.method == 'POST':
        form = AddpaymentTransactionForm(request.POST)
        if form.is_valid():
            form.save()
            msg = "paymentTransaction addes successfully"
    paymentTransactions=paymentTransaction.objects.all()               
    context = {'form': form,'msg':msg,'paymentTransactions':paymentTransactions}           
    return render(request, 'add_paymentTransaction.html', context)


def add_plansSubscription(request):
    msg=''
    form = AddplansSubscriptionForm()
    if request.method == 'POST':
        form = AddplansSubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            msg = "plansSubscription addes successfully"
    plansSubscriptions=plansSubscription.objects.all()               
    context = {'form': form,'msg':msg,'plansSubscriptions':plansSubscriptions} 
    return render(request, 'add_plansSubscription.html', context)


def add_plansFeatures(request):
    msg=''
    form = AddplansFeaturesForm()
    if request.method == 'POST':
        form = AddplansFeaturesForm(request.POST)
        if form.is_valid():
            form.save()
            msg = "plansFeatures addes successfully"
    plansFeature=plansFeatures.objects.all()               
    context = {'form': form,'msg':msg,'plansFeature':plansFeature} 
    return render(request, 'add_plansFeatures.html', context)