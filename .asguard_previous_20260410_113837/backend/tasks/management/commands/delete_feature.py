from django.core.management.base import BaseCommand, CommandError
from backend.subscription.models  import plan, plansFeatures, Features
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'delete features from the database'
    
    def add_arguments(self, parser):
        parser.add_argument('-f', '--feature', type=str, help='Define a feature')
    
    def handle(self, *args, **kwargs):
        try:
            feature = kwargs['feature']
            if feature and Features.objects.filter(features=feature).exists():
                feature = f'{feature}'
                Features.objects.get(features=feature).delete()
                plan_features = plansFeatures.objects.filter(description=feature)
                for plan_feature in plan_features:
                    plan.objects.get(id=plan_feature.plan_id).delete()
                self.stdout.write(self.style.SUCCESS('feature deleted succesffuly'))
            else:
                self.stdout.write(self.style.ERROR("feature dosn't exist"))
        except IntegrityError as e:
            return "Error: " + str(e)