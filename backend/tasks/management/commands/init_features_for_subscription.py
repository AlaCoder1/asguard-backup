from backend.subscription.models import *
from django.core.management.base import BaseCommand
# features = Features.objects.all()

features = [
    ("WAF",180),("SDWAN",180)
]
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for feature in features:
            Features.objects.create(features=feature[0],price=feature[1])
    