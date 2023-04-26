from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
class organization(models.Model):
    groupName = models.CharField(max_length=200, null=True)
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
    paymentLink = models.CharField(max_length=200, null=True)
    amount = models.FloatField(null=True)
    status = models.CharField(max_length=200,null=True)
    subscriptionType = models.CharField(max_length=200,null=True)
    organizationId = models.ForeignKey(organization, on_delete=models.CASCADE)
    planId = models.ForeignKey(plan, on_delete=models.CASCADE)
    class Meta:
        db_table = 'payment_transaction'
    def __str__(self):
        return self.uuid
    
class plansSubscription(models.Model):
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    planId = models.ForeignKey(plan, on_delete=models.CASCADE)
    class Meta:
        db_table = 'plans_subscription'

    
class plansFeatures(models.Model):
    description = models.CharField(max_length=200,null=True )
    planId = models.ForeignKey(plan, on_delete=models.CASCADE)
    plan_subsciption_usage=models.ManyToManyField('plansSubscription', through='planSubsciptionUsage')
    class Meta:
        db_table = 'plans_features'
    def __str__(self):
        return self.description
    
class planSubsciptionUsage(models.Model):
    plans_feature = models.ForeignKey(plansFeatures, on_delete=models.CASCADE)
    plans_subscription = models.ForeignKey(plansSubscription, on_delete=models.CASCADE)
    valid_until =models.DateTimeField()
    class Meta:
        db_table = 'plan_subsciption_usage'
