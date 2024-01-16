import json
from django.shortcuts import render
from .form import *
from .models import *
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from django.core import serializers
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

##paymentTransaction_name
def function_paymentTransaction(checkbox_value,select_value):
    payment_instance = paymentTransaction()
    if checkbox_value != None:
        payment_instance.status = "declined"
    else:
        payment_instance.status = "approved"
    payment_instance.organization = organization.objects.get(id=1)
    payment_instance.plan = plan.objects.get(slug=select_value)
    payment_instance.save()

##paymentTransaction_id
def function_paymentTransaction_id(checkbox_value,select_value):
    payment_instance = paymentTransaction()
    if checkbox_value != None:
        payment_instance.status = "declined"
    else:
        payment_instance.status = "approved"
    payment_instance.organization = organization.objects.get(id=1)
    payment_instance.plan = plan.objects.get(id=select_value)
    payment_instance.save()
        
def function_plansSubscription():
    last_id_paymentTransaction = paymentTransaction.objects.last().id
    payment_transaction=paymentTransaction.objects.get(id=last_id_paymentTransaction)
    payment_transaction_dict=payment_transaction.__dict__
    if payment_transaction.status == "approved":
        payment_subscription_instance = plansSubscription()
        payment_subscription_instance.start_at=datetime.now()
        payment_subscription_instance.end_at=datetime.now()+ timedelta(days=365)
        payment_subscription_instance.plan=plan.objects.get(id=payment_transaction_dict['plan_id'])
        payment_subscription_instance.save()
            

def function_planSubsciptionUsage():
    last_id = paymentTransaction.objects.last().id
    payment_transaction=paymentTransaction.objects.get(id=last_id)
    payment_transaction_dict=payment_transaction.__dict__
    payment_features=plansFeatures.objects.filter(plan=payment_transaction_dict['plan_id'])
    last_plansSubscription = plansSubscription.objects.filter(plan=payment_transaction_dict['plan_id']).last()
    # print({"last_plansSubscription":last_plansSubscription.__dict__['end_at']})
    for result in list(payment_features):
        if payment_transaction.status == "approved":
            payment_subscription_usage_instance = planSubsciptionUsage()
            payment_subscription_usage_instance.plans_subscription =plansSubscription.objects.filter(plan=payment_transaction_dict['plan_id']).last()
            payment_subscription_usage_instance.plans_feature =plansFeatures.objects.get(id=result.id)
            payment_subscription_usage_instance.valid_until =last_plansSubscription.__dict__['end_at']
            payment_subscription_usage_instance.save()

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])   
def payment(request):
    form = MyForm()
    if request.method == 'POST':
        # parse the incoming information
        data = request.data
        status = data['status']
        if status:
            status=None
        # subscription_name = data['subscription_name']
        subscription_id = data['subscription_id']
        # function_paymentTransaction(status,subscription_name)
        function_paymentTransaction_id(status,subscription_id)
        function_plansSubscription()
        function_planSubsciptionUsage()
        if status == None:
            return JsonResponse({"msg": "you subscribed successfully"}, status=200)
        else:
            return JsonResponse({"msg": "you subscribed declined"}, status=400)
    # return render(request, 'payment.html', {'form': form})
    



def is_valid():
    last_subscription = plansSubscription.objects.order_by('start_at').last()
    last_subscription_dict = last_subscription.__dict__
    if ((last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()).days >= 0 ):
        return True
    else:
        return False
    
def has_subscription():
    last_subscription = plansSubscription.objects.order_by('start_at').last()
    if last_subscription is None:
        return False
    else:
        return True

def if_subscribed(indexs_plans_feature):
    list_of_plan_feature = []
    last_subscription = plansSubscription.objects.order_by('start_at').last()
    last_subscription_dict = last_subscription.__dict__
    # print({"date_end":last_subscription_dict['end_at']})
    # print({"resultsss":last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()})
    # print({"days":(last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()).days})
    # print({"last_subscription":last_subscription_dict})
    # print({"last_subscription_id":last_subscription.id})
    planSubsciptionUsages = planSubsciptionUsage.objects.filter(plans_subscription=last_subscription.id)
    # print({"list_of_planSubsciptionUsages":planSubsciptionUsages})
    for k in range(0,len(planSubsciptionUsages)):
        list_of_plan_feature.append(planSubsciptionUsages[k].plans_feature_id)
    # print({"indexs_plans_feature":indexs_plans_feature})
    # print({"list_of_plan_feature":list_of_plan_feature})
    common_elements = set(indexs_plans_feature) & set(list_of_plan_feature)
    # print({"type":type(common_elements)})
    # print({"tttttttttttttttttttttttttttttttt":common_elements})
    # print({"bbbbbbbbbb":bool(common_elements)})
    try:
        common_elements = set(indexs_plans_feature) & set(list_of_plan_feature)        
        if bool(common_elements):
            return True
        else:
            return False
    except ValueError:
        return False
    

def list_features_about_last_subscription(request):
    list_features = []
    if request.method == 'GET':
        last_subscription = plansSubscription.objects.order_by('start_at').last()
        last_subscription_dict = last_subscription.__dict__
        if ((last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()).days >= 0 ):
            print({"plan_id_from_last_subscription":last_subscription.plan.pk})
            plan_features= plansFeatures.objects.filter(plan = last_subscription.plan.pk)
            plan_features_dict = serializers.serialize("json", plan_features)
            res = json.loads(plan_features_dict)
            print({"plan_features":res[0]})
            for i in res:
                for key, value in i.items():
                    print(f"Key: {key}, Value: {value}")
                    if key == 'fields':
                        list_features.append(i['fields']['description'])
            print({"list_features":list_features})
        
        return JsonResponse({"msg": "you subscribed declined"}, status=400)