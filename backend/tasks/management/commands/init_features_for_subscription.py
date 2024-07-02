import itertools
from backend.subscription.models import *
from django.core.management.base import BaseCommand
# features = Features.objects.all()

features = [
    ("Double Masque",50),("WAF",100), ("IPS",150), ("VPN SSL",200),("Proxy",50),("SDWAN",50)
]
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for feature in features:
            Features.objects.create(features=feature[0],price=feature[1])
    