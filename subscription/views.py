from django.shortcuts import render
from .form import *
from .models import *
from datetime import datetime, timedelta
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


def function_paymentTransaction(checkbox_value,select_value):
    payment_instance = paymentTransaction()
    if checkbox_value != None:
        payment_instance.status = "declined"
    else:
        payment_instance.status = "approved"
    payment_instance.organizationId = organization.objects.get(id=1)
    payment_instance.planId = plan.objects.get(slug=select_value)
    payment_instance.save()
        
def function_plansSubscription():
    last_id_paymentTransaction = paymentTransaction.objects.last().id
    payment_transaction=paymentTransaction.objects.get(id=last_id_paymentTransaction)
    payment_transaction_dict=payment_transaction.__dict__
    if payment_transaction.status == "approved":
        payment_subscription_instance = plansSubscription()
        payment_subscription_instance.start_at=datetime.now()
        payment_subscription_instance.end_at=datetime.now()+ timedelta(days=365)
        payment_subscription_instance.planId=plan.objects.get(id=payment_transaction_dict['planId_id'])
        payment_subscription_instance.save()
            

def function_planSubsciptionUsage():
    last_id = paymentTransaction.objects.last().id
    # if(paymentTransaction.objects.last().id is not None):
    #     last_id = paymentTransaction.objects.last().id
    # else:
    #     last_id=1
    payment_transaction=paymentTransaction.objects.get(id=last_id)
    payment_transaction_dict=payment_transaction.__dict__
    payment_features=plansFeatures.objects.filter(planId=payment_transaction_dict['planId_id'])
    last_plansSubscription = plansSubscription.objects.filter(planId=payment_transaction_dict['planId_id']).last()
    # print({"last_plansSubscription":last_plansSubscription.__dict__['end_at']})
    for result in list(payment_features):
        if payment_transaction.status == "approved":
            payment_subscription_usage_instance = planSubsciptionUsage()
            payment_subscription_usage_instance.plans_subscription =plansSubscription.objects.filter(planId=payment_transaction_dict['planId_id']).last()
            payment_subscription_usage_instance.plans_feature =plansFeatures.objects.get(id=result.id)
            payment_subscription_usage_instance.valid_until =last_plansSubscription.__dict__['end_at']
            payment_subscription_usage_instance.save()
        
def payment(request):
    form = MyForm()
    if request.method == 'POST':
        my_checkbox_value = request.POST.get('my_checkbox')
        my_select_value = request.POST.get('my_select')
        function_paymentTransaction(my_checkbox_value,my_select_value)
        function_plansSubscription()
        function_planSubsciptionUsage()
        if is_valid():
            if if_subscribed(2):
                print("he has a subscription")
            else:
                print("he hasn't a subscription")
        else:
            print("your subscription has expired")
    return render(request, 'payment.html', {'form': form})

def initBD_organization():
    organization_instance = organization()
    organization_instance.groupName = "numeryx"
    organization_instance.save()
    
def initBD_plan(slug,price):
    plan_instance = plan()
    plan_instance.slug = slug
    plan_instance.price = price
    plan_instance.currency = "euro"
    plan_instance.save()
    
def initBD_plansFeatures(description,planId):
    plansFeatures_instance = plansFeatures()
    plansFeatures_instance.description = description
    plansFeatures_instance.planId = plan.objects.get(id=planId)
    plansFeatures_instance.save()

def initBD(request):
    initBD_organization()

    initBD_plan("basic",100)
    initBD_plan("gold",500)

    initBD_plansFeatures("management users",1)
    initBD_plansFeatures("management users",2)
    initBD_plansFeatures("network",2)
    return render(request, 'payment.html')


# def if_subscribed(plan_id,index_plans_feature):
#     list_of_plan_feature = []
#     # last_subscription = plansSubscription.objects.order_by('start_at').last()
#     last_subscription = plansSubscription.objects.filter(planId=plan_id).order_by('start_at').last()
#     last_subscription_dict = last_subscription.__dict__
#     date_end=last_subscription_dict['end_at']
#     date_end_datetime = datetime.combine(date_end, datetime.min.time())
#     difference = datetime.now() - date_end_datetime
#     print({"date_now":datetime.now()})
#     print({"date_end":date_end})
#     print({"resultsss":difference.days})
#     #inverse the condition because we are in face of test so all date that we have is >= data.now
#     if (difference.days <= 0):
#         print({"last_subscription_id":last_subscription.id})
#         planSubsciptionUsages = planSubsciptionUsage.objects.filter(plans_subscription=last_subscription.id)
#         print({"list_of_planSubsciptionUsages":planSubsciptionUsages})
#         for k in range(0,len(planSubsciptionUsages)):
#             list_of_plan_feature.append(planSubsciptionUsages[k].plans_feature_id)
#         print({"list_of_plan_feature":list_of_plan_feature})
#     # for i in list:
#     #     print(i)
#         # planSubsciptionUsages = planSubsciptionUsage.objects.filter(plans_feature=i)
#         # print(planSubsciptionUsages[0].plans_subscription)
#         # if list_of_plan_feature.find(index_plans_feature) !=
#         try:
#             list_of_plan_feature.index(index_plans_feature)
#             print(list_of_plan_feature.index(index_plans_feature))
#             return True
#         except ValueError:
#             print("plan_feature not found in plan_subsciption")
#             return False
def is_valid():
    last_subscription = plansSubscription.objects.order_by('start_at').last()
    last_subscription_dict = last_subscription.__dict__
    if ((last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()).days >= 0 ):
        return True
    else:
        return False
def if_subscribed(index_plans_feature):
    list_of_plan_feature = []
    last_subscription = plansSubscription.objects.order_by('start_at').last()
    last_subscription_dict = last_subscription.__dict__
    # date_end_datetime = datetime.combine(last_subscription_dict['end_at'], datetime.min.time())
    print({"date_now":datetime.now()})
    print({"date_end":last_subscription_dict['end_at']})
    print({"resultsss":last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()})
    print({"days":(last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()).days})
    print({"last_subscription":last_subscription_dict})
    # if ((last_subscription_dict['end_at'].replace(tzinfo=None) - datetime.now()).days >= 0 ):
    print({"last_subscription_id":last_subscription.id})
    planSubsciptionUsages = planSubsciptionUsage.objects.filter(plans_subscription=last_subscription.id)
    print({"list_of_planSubsciptionUsages":planSubsciptionUsages})
    for k in range(0,len(planSubsciptionUsages)):
        list_of_plan_feature.append(planSubsciptionUsages[k].plans_feature_id)
    # print({"list_of_plan_feature":list_of_plan_feature})
    try:
        list_of_plan_feature.index(index_plans_feature)
        # print(list_of_plan_feature.index(index_plans_feature))
        return True
    except ValueError:
        # print("plan_feature not found in plan_subsciption")
        return False
    # else:
    #     return "your subscription has expired"