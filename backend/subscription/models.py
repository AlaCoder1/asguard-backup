from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
class organization(models.Model):
    groupname = models.CharField(max_length=200, null=True)
    class Meta:
        db_table = 'organization'
    def __str__(self):
        return self.groupName
    
class plan(models.Model):
    slug = models.CharField(max_length=200, null=True)
    price = models.FloatField(null=True)
    currency = models.CharField(max_length=200, null=True)
    class Meta:
        db_table = 'plan'
    def __str__(self):
        return self.slug
    
class paymentTransaction(models.Model):
    uuid = models.CharField(max_length=200, null=True)
    payment_link = models.CharField(max_length=200, null=True)
    amount = models.FloatField(null=True)
    status = models.CharField(max_length=200,null=True)
    subscription_type = models.CharField(max_length=200,null=True)
    organization = models.ForeignKey(organization, on_delete=models.CASCADE)
    plan = models.ForeignKey(plan, on_delete=models.CASCADE)
    class Meta:
        db_table = 'payment_transaction'
    def __str__(self):
        return self.uuid
    
class plansSubscription(models.Model):
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    plan = models.ForeignKey(plan, on_delete=models.CASCADE)
    class Meta:
        db_table = 'plans_subscription'

    
class plansFeatures(models.Model):
    description = models.CharField(max_length=200,null=True )
    plan = models.ForeignKey(plan, on_delete=models.CASCADE)
    class Meta:
        db_table = 'plans_features'

    
class planSubsciptionUsage(models.Model):
    plans_feature = models.ForeignKey(plansFeatures, on_delete=models.CASCADE)
    plans_subscription = models.ForeignKey(plansSubscription, on_delete=models.CASCADE)
    valid_until =models.DateTimeField()
    class Meta:
        db_table = 'plan_subsciption_usage'
