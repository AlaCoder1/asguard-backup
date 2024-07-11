from django.core.management.base import BaseCommand, CommandError
from backend.subscription.models  import plan, paymentTransaction, plansSubscription, plansFeatures, planSubsciptionUsage, Features
from django.core.management import call_command
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Deletes all data from specific tables in the database and add another features for subscription and init the database'
    
    def add_arguments(self, parser):
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