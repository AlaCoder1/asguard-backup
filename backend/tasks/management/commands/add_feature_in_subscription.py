import itertools
import re
from django.core.management.base import BaseCommand, CommandError
from backend.subscription.models  import plan, plansFeatures, Features
from django.core.management import call_command
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Add another features for subscription and update the database'
    
    def add_arguments(self, parser):
        parser.add_argument('-f', '--feature', type=str, help='Define a feature')
        parser.add_argument('-p', '--price', type=str, help='Define a feature price')
    
    def initBD_plan(self,slug,price):
        plan_instance = plan()
        plan_instance.slug = slug
        plan_instance.price = price
        plan_instance.currency = "euro"
        plan_instance.save()
        
    def initBD_plansFeatures(self,description,planId):
        plansFeatures_instance = plansFeatures()
        plansFeatures_instance.description = description
        plansFeatures_instance.plan = plan.objects.get(id=planId)
        plansFeatures_instance.save()
        
    def basic(self):
        last_plan = plan.objects.last()
        self.initBD_plansFeatures("Firewall L4",last_plan.pk)
        self.initBD_plansFeatures("Networking L2 L3",last_plan.pk)
        self.initBD_plansFeatures("VPN IPSEC",last_plan.pk)
        self.initBD_plansFeatures("LDAP",last_plan.pk)
        self.initBD_plansFeatures("Double Masque",last_plan.pk)
        self.initBD_plansFeatures("IDS/IPS",last_plan.pk)
        self.initBD_plansFeatures("VPN SSL",last_plan.pk)
        self.initBD_plansFeatures("Proxy",last_plan.pk)

    def filter_original_list(self,original_list, target_values):
        """Filter the original list to get only the values present in target_values."""
        return [value for value in original_list if value in target_values]
    def get_combination_sums(self,numbers):
        if len(numbers) < 2:
            return []
        last_element = numbers[-1]
        remaining_elements = numbers[:-1]
        result = [last_element]
        for r in range(1, len(remaining_elements) + 1):
            for combination in itertools.combinations(remaining_elements, r):
                result.append(last_element + sum(combination))
        return result
    
    def handle(self, *args, **kwargs):
        try:
            feature = kwargs['feature']
            price = kwargs['price']
            if feature and price and not Features.objects.filter(features=feature).exists():
                feature = f'{feature}'
                price = f'{price}'
                Features.objects.create(features=feature, price=price)
                try:
                    list_of_descriptions = []
                    plan_dict = {}
                    plans = plan.objects.all()
                    for p in plans:
                        if p.slug in ['Basic', 'Full']:
                            continue
                        descriptions = plansFeatures.objects.filter(plan=p).values_list('description', flat=True)
                        plan_dict[p.slug]=list(descriptions)
                        list_of_descriptions.append(list(descriptions))
                        plan_dict = {}
                    
                    list_feature_with_combinations = []
                    features_queryset = Features.objects.all()
                    features = [(feature.features, feature.price) for feature in features_queryset]

                    all_combinations_with_details = []
                    full_plan = plan.objects.get(slug="Full")
                    combination_number = 1
                    for r in range(1, len(features) + 1):
                        combinations_object = itertools.combinations(features, r)
                        combinations_list = list(combinations_object)
                        for combo in combinations_list:
                            total_price = sum(feature[1] for feature in combo)
                            feature_names = tuple(feature[0] for feature in combo)
                            all_combinations_with_details.append((combination_number, feature_names, total_price))
                            combination_number += 1
                    price_totals = [price_total for __, __, price_total in all_combinations_with_details]
                    for __, (__, feature_names, price_total) in enumerate(all_combinations_with_details):
                        all_plans = plan.objects.all()
                        features_list = Features.objects.all()
                        prices = [p.price for p in features_list]
                        feature_with_combinations = ["Firewall L4", "Networking L2 L3", "VPN IPSEC", "LDAP", "Double Masque", "IDS/IPS", "VPN SSL", "Proxy"] + list(feature_names)
                        list_feature_with_combinations.append(feature_with_combinations)
                        list_combo = self.get_combination_sums(prices)
                        filtered_values = self.filter_original_list(price_totals, list_combo)
                        if len(all_combinations_with_details) > len(all_plans)-2:
                            last_plan = plan.objects.last()
                            num = re.search(r'\d+', last_plan.slug).group()
                            if price_total in filtered_values:
                                self.initBD_plan(f"Custom{int(num)+1}", float(price_total) + full_plan.price)
                    diff_list = [item for item in list_feature_with_combinations if item not in list_of_descriptions]
                    if len(diff_list) > 0:
                        for element in diff_list:
                            last_plan_features = plansFeatures.objects.last()
                            for name in element:
                                self.initBD_plansFeatures(name,last_plan_features.plan_id+1)
                    self.stdout.write(self.style.SUCCESS('Successfully called init_subscription command.'))
                except CommandError as e:
                    self.stdout.write(self.style.ERROR(f'Error calling init_sub: {e}'))
                return "feature added succesffuly"
            else:
                return "feature already exist"
        except IntegrityError as e:
            return "Error: " + str(e)