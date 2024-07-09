import itertools
from backend.subscription.models import *
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        #### init basic
        plan_basic(999)
        #### init basic
        features_queryset = Features.objects.all()
        features = [(feature.features, feature.price) for feature in features_queryset]
        #### init full
        full(features)
        #### init full

        all_combinations_with_details = []

        combination_number = 1
        for r in range(1, len(features) + 1):
            combinations_object = itertools.combinations(features, r)
            combinations_list = list(combinations_object)
            
            for combo in combinations_list:
                total_price = sum(feature[1] for feature in combo)
                feature_names = tuple(feature[0] for feature in combo)
                all_combinations_with_details.append((combination_number, feature_names, total_price))
                combination_number += 1

        for combo_number, feature_names, total_price in all_combinations_with_details:
            # print(f"Combination {combo_number}: {feature_names} with Total Price: {total_price}")
            basic_plan = plan.objects.get(slug="Basic")
            initBD_plan(f"Custom{combo_number}",total_price+basic_plan.price)
            basic(f"Custom{combo_number}")
            last_plan = plan.objects.get(slug=f"Custom{combo_number}")
            for name in feature_names:
                initBD_plansFeatures(name,last_plan.pk)
                
    
def initBD_plan(slug,price):
    plan_instance = plan()
    plan_instance.slug = slug
    plan_instance.price = price
    plan_instance.currency = "euro"
    plan_instance.save()
    
def initBD_plansFeatures(description,planId):
    plansFeatures_instance = plansFeatures()
    plansFeatures_instance.description = description
    plansFeatures_instance.plan = plan.objects.get(id=planId)
    plansFeatures_instance.save()

def plan_basic(price):
    initBD_plan("Basic",price)
    basic_plan = plan.objects.get(slug="Basic")
    initBD_plansFeatures("Firewall L4",basic_plan.pk)
    initBD_plansFeatures("Networking L2 L3",basic_plan.pk)
    initBD_plansFeatures("VPN IPSEC",basic_plan.pk)
    initBD_plansFeatures("LDAP",basic_plan.pk)
    initBD_plansFeatures("Double Masque",basic_plan.pk)
    
    
def basic(slug):
    last_plan = plan.objects.get(slug=slug)
    initBD_plansFeatures("Firewall L4",last_plan.pk)
    initBD_plansFeatures("Networking L2 L3",last_plan.pk)
    initBD_plansFeatures("VPN IPSEC",last_plan.pk)
    initBD_plansFeatures("LDAP",last_plan.pk)
    initBD_plansFeatures("Double Masque",last_plan.pk)

    
def full(features):
    basic_plan = plan.objects.get(slug="Basic")
    total_price = sum(price for name,price in features) + basic_plan.price
    initBD_plan("Full",total_price)
    initBD_plansFeatures("Firewall L4",basic_plan.pk+1)
    initBD_plansFeatures("Networking L2 L3",basic_plan.pk+1)
    initBD_plansFeatures("VPN IPSEC",basic_plan.pk+1)
    initBD_plansFeatures("LDAP",basic_plan.pk+1)
    initBD_plansFeatures("Double Masque",basic_plan.pk+1)
    initBD_plansFeatures("IDS/IPS",basic_plan.pk+1)
    initBD_plansFeatures("VPN SSL",basic_plan.pk+1)
    initBD_plansFeatures("Proxy",basic_plan.pk+1)
    
    for feature in features:
        initBD_plansFeatures(feature[0],basic_plan.pk+1)