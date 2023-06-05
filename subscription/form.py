from django.forms import ModelForm
from .models import *

class AddplanForm(ModelForm):
    class Meta:
        model = plan
        fields = '__all__'
class addorganizationForm(ModelForm):
    class Meta:
        model = organization
        fields = '__all__'
class AddpaymentTransactionForm(ModelForm):
    class Meta:
        model = paymentTransaction
        fields = '__all__'
class AddplansSubscriptionForm(ModelForm):
    class Meta:
        model = plansSubscription
        fields = '__all__'
        
class AddplansFeaturesForm(ModelForm):
    class Meta:
        model = plansFeatures
        fields = '__all__'
        
from django import forms

class MyForm(forms.Form):
    my_checkbox = forms.BooleanField(required=False)
    my_select = forms.ChoiceField(choices=[('basic', 'basic'),('gold', 'gold') ])
    # plans = plan.objects.all().values_list('slug', flat=True)
    # my_select = forms.ChoiceField(choices=[('basic', plans[0]),('gold', plans[1]) ])