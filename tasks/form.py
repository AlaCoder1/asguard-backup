from django import forms
from django.db.models import fields
from django.forms import ModelForm
from .models import *

# form de appel d'offre


class AddUser(ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        exclude = ('uid',)
        
class AddGroup(ModelForm):
    class Meta:
        model = Group
        fields = '__all__'