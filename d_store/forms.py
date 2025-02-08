from django import forms



class PossibleBuyerForm(forms.Form):
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
    
    
