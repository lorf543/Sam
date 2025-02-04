from django import forms


class PossibleBuyerForm(forms.Form):
    phone = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    comment = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder':'Comenta algo en caso de ser necesario...',
        "rows":"5",
        }), required=False)
    
    
