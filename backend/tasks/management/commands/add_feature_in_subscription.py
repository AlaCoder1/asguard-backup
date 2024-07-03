# import itertools
# from backend.subscription.models import *
# from django.core.management.base import BaseCommand

# class Command(BaseCommand):
#     def handle(self, *args, **kwargs):
        
#         # initBD_organization()
#         #### init basic
#         plan_basic(800)
#         #### init basic
#         features_queryset = Features.objects.all()
#         features = [(feature.features, feature.price) for feature in features_queryset]
#         #### init full
#         full(features)
#         #### init full

#         all_combinations_with_details = []

#         combination_number = 1
#         for r in range(1, len(features) + 1):
#             combinations_object = itertools.combinations(features, r)
#             combinations_list = list(combinations_object)
            
#             for combo in combinations_list:
#                 total_price = sum(feature[1] for feature in combo)
#                 feature_names = tuple(feature[0] for feature in combo)
#                 all_combinations_with_details.append((combination_number, feature_names, total_price))
#                 combination_number += 1

#         for combo_number, feature_names, total_price in all_combinations_with_details:
#             print(f"Combination {combo_number}: {feature_names} with Total Price: {total_price}")
#             basic_plan = plan.objects.get(slug="Basic")
#             initBD_plan(f"Custom{combo_number}",total_price+basic_plan.price)
#             basic(f"Custom{combo_number}")
#             last_plan = plan.objects.get(slug=f"Custom{combo_number}")
#             for name in feature_names:
#                 initBD_plansFeatures(name,last_plan.pk)
                
    
# def initBD_organization():
#     organization_instance = organization()
#     organization_instance.groupname = "numeryx"
#     organization_instance.save()
    
# def initBD_plan(slug,price):
#     plan_instance = plan()
#     plan_instance.slug = slug
#     plan_instance.price = price
#     plan_instance.currency = "euro"
#     plan_instance.save()
    
# def initBD_plansFeatures(description,planId):
#     plansFeatures_instance = plansFeatures()
#     plansFeatures_instance.description = description
#     plansFeatures_instance.plan = plan.objects.get(id=planId)
#     plansFeatures_instance.save()

# def plan_basic(price):
#     initBD_plan("Basic",price)
#     basic_plan = plan.objects.get(slug="Basic")
#     initBD_plansFeatures("Firewall L4",basic_plan.pk)
#     initBD_plansFeatures("Networking L2 L3",basic_plan.pk)
#     initBD_plansFeatures("VPN IPSEC",basic_plan.pk)
#     initBD_plansFeatures("LDAP",basic_plan.pk)
    
# def basic(slug):
#     print({"slug":slug})
#     last_plan = plan.objects.get(slug=slug)
#     initBD_plansFeatures("Firewall L4",last_plan.pk)
#     initBD_plansFeatures("Networking L2 L3",last_plan.pk)
#     initBD_plansFeatures("VPN IPSEC",last_plan.pk)
#     initBD_plansFeatures("LDAP",last_plan.pk)

    
# def full(features):
#     basic_plan = plan.objects.get(slug="Basic")
#     total_price = sum(price for name,price in features) + basic_plan.price
#     initBD_plan("Full",total_price)
#     initBD_plansFeatures("Firewall L4",basic_plan.pk+1)
#     initBD_plansFeatures("Networking L2 L3",basic_plan.pk+1)
#     initBD_plansFeatures("VPN IPSEC",basic_plan.pk+1)
#     initBD_plansFeatures("LDAP",basic_plan.pk+1)
#     for feature in features:
#         initBD_plansFeatures(feature[0],basic_plan.pk+1)





from django.core.management.base import BaseCommand, CommandError
from backend.subscription.models  import plan, paymentTransaction, plansSubscription, plansFeatures, planSubsciptionUsage, Features
from django.core.management import call_command
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Deletes all data from specific tables in the database and add another features for subscription and init the database'
    
    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-f', '--feature', type=str, help='Define a feature')
        parser.add_argument('-p', '--price', type=str, help='Define a feature price')
        
    def handle(self, *args, **kwargs):
        try:
            feature = kwargs['feature']
            price = kwargs['price']
            if feature and price and not Features.objects.filter(features=feature).exists():
                feature = f'{feature}'
                price = f'{price}'
                Features.objects.create(features=feature, price=price)
                try:
                    self.stdout.write(self.style.SUCCESS('Deleting data...'))

                    plan.objects.all().delete()
                    paymentTransaction.objects.all().delete()
                    plansSubscription.objects.all().delete()
                    plansFeatures.objects.all().delete()
                    planSubsciptionUsage.objects.all().delete()

                    self.stdout.write(self.style.SUCCESS('Data deleted successfully!'))
                    self.stdout.write(self.style.SUCCESS('insert data...'))
                    try:
                        call_command('init_subscription')
                        self.stdout.write(self.style.SUCCESS('Successfully called init_subscription command after deleting'))
                    except CommandError as e:
                        self.stdout.write(self.style.ERROR(f'Error calling init_sub: {e}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to delete data: {str(e)}'))
                return "feature added succesffuly"
            else:
                return "feature already exist"
        except IntegrityError as e:
            return "Error: " + str(e)
    # def handle(self, *args, **kwargs):
    #     try:
    #         self.stdout.write(self.style.SUCCESS('Deleting data...'))

    #         plan.objects.all().delete()
    #         paymentTransaction.objects.all().delete()
    #         plansSubscription.objects.all().delete()
    #         plansFeatures.objects.all().delete()
    #         planSubsciptionUsage.objects.all().delete()

    #         self.stdout.write(self.style.SUCCESS('Data deleted successfully!'))
    #         self.stdout.write(self.style.SUCCESS('insert data...'))
    #         try:
    #             call_command('init_subscription')
    #             self.stdout.write(self.style.SUCCESS('Successfully called init_subscription command after deleting'))
    #         except CommandError as e:
    #             self.stdout.write(self.style.ERROR(f'Error calling init_sub: {e}'))
    #     except Exception as e:
    #         self.stdout.write(self.style.ERROR(f'Failed to delete data: {str(e)}'))

