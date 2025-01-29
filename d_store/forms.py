from django import forms

from .models import PossibleBuyer
from d_store.models import Comments

class PossibleBuyerForm(forms.Form):
    phone = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    
    
