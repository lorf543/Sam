from django import forms

from .models import PossibleBuyer


class PossibleBuyerForm(forms.ModelForm):
    
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '000-000-0000'}),
        max_length=50,
    )
    email = forms.EmailField(

    )
    comment = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder':'Comenta algo en caso de ser necesario...',
        "rows":"5",
        }),)
    
    class Meta:
        model = PossibleBuyer
        fields = ("name","last_name","phone","comment")
        labels = {
            "name":"Nombre",
            "last_name":"Apellido",
            "phone":"Telefono",
        }




    
    
