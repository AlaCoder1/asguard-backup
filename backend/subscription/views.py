import itertools
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
    organizations=Organization.objects.all()               
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
    payment_instance.organization = Organization.objects.get(id=1)
    payment_instance.plan = plan.objects.get(slug=select_value)
    payment_instance.save()

##paymentTransaction_id
def function_paymentTransaction_id(checkbox_value,select_value):
    payment_instance = paymentTransaction()
    if checkbox_value != None:
        payment_instance.status = "declined"
    else:
        payment_instance.status = "approved"
    payment_instance.organization = Organization.objects.get(id=1)
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
    if request.method == 'POST':
        data = request.data
        status = data['status']
        if status:
            status=None
        
        # list_features = data['features']
        # if "Basic"in list_features:
        #     subscription_plan = plan.objects.get(slug="Basic")
        # elif "Full" in list_features:
        #     subscription_plan = plan.objects.get(slug="Full")
        # else:
        #     features_queryset = Features.objects.all()
        #     features = [(feature.features, feature.price) for feature in features_queryset]

        #     all_combinations_with_details = []

        #     combination_number = 1
        #     for r in range(1, len(features) + 1):
        #         combinations_object = itertools.combinations(features, r)
        #         combinations_list = list(combinations_object)
                
        #         for combo in combinations_list:
        #             total_price = sum(feature[1] for feature in combo)
        #             feature_names = tuple(feature[0] for feature in combo)
        #             all_combinations_with_details.append((combination_number, feature_names, total_price))
        #             combination_number += 1

        #     for combo_number, feature_names, total_price in all_combinations_with_details:
        #         feature_with_combinations = ["Firewall L4","Networking L2 L3","VPN IPSEC","LDAP"] + list(feature_names)
        #         if list_features == feature_with_combinations:
        #             subscription_plan = plan.objects.get(slug=f"Custom{combo_number}")
        subscription_id = data['subscription_id']
        function_paymentTransaction_id(status,subscription_id)
        function_plansSubscription()
        function_planSubsciptionUsage()
        if status == None:
            return JsonResponse({"msg": "you subscribed successfully"}, status=200)
        else:
            return JsonResponse({"msg": "you subscribed declined"}, status=400)

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
        if last_subscription !=None:
            last_subscription_dict = last_subscription.__dict__
            if ((last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()).days >= 0 ):
                plan_features= plansFeatures.objects.filter(plan = last_subscription.plan.pk)
                plan_features_dict = serializers.serialize("json", plan_features)
                res = json.loads(plan_features_dict)
                for i in res:
                    for key, value in i.items():
                        if key == 'fields':
                            list_features.append(i['fields']['description'])
        else:
            list_features = []
        # return list_features
        return JsonResponse({"msg": list_features}, status=200)
    
def subscription_info(request):
    subscription_info = {}
    if request.method == 'GET':
        last_subscription = plansSubscription.objects.order_by('start_at').last()
        if last_subscription != None:
            last_subscription_dict = last_subscription.__dict__
            print({"last_subscription_dict['id']":last_subscription_dict})
            if ((last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()).days >= 0 ):
                plan_info = plan.objects.get(id = last_subscription_dict['plan_id'])
                subscription_info['type_pack'] =plan_info.slug
                subscription_info['date_start'] =last_subscription_dict['start_at'].strftime('%Y-%m-%d %H:%M:%S')
                subscription_info['end_at'] =last_subscription_dict['end_at'].strftime('%Y-%m-%d %H:%M:%S')
                subscription_info['expiration_date'] =last_subscription_dict['end_at'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            subscription_info = {}
        return JsonResponse({"msg": subscription_info}, status=200)
    
    
    
    
def all_feature(request):
    features = []
    feature_element = {}
    if request.method == 'GET':
        features_from_bd = Features.objects.all()
        for feature in features_from_bd:
            feature_element["name"] = feature.features
            feature_element["price"] = feature.price
            feature_element["id"] = feature.pk
            features.append(feature_element)
            feature_element = {}
        return JsonResponse({"features": features}, status=200)
        return features
        # return features
        
def all_plan(request):
    plans = []
    if request.method == 'GET':
        plans_from_bd = plan.objects.all()
        for Plan in plans_from_bd:
            plans.append(Plan.slug)
        return JsonResponse({"plans": plans}, status=200)
    
