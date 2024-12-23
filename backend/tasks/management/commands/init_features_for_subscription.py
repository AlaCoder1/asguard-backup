from backend.subscription.models import Features
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for feature in [("WAF",180), ("SDWAN",180), ("ZTNA",180)]:
            Features.objects.create(features=feature[0],price=feature[1])
