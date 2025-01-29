from django import forms
from allauth.account.forms import SignupForm

from d_store.models import PossibleBuyer,Comments,UserProfile
from .models import Pedidos

from django.contrib.auth.models import User


class PossibleBuyerForm(forms.ModelForm):
    
    class Meta:
        model = PossibleBuyer
        fields = "__all__"


from allauth.account.forms import LoginForm

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases Bootstrap a cada campo
        self.fields['login'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Usuario o Email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['login'].label = "Nombre de usuario"
        self.fields['password'].label = "Contraseña"
        

class CommentsForm(forms.ModelForm):
    
    class Meta:
        model = Comments
        fields = ("content",)
            
        widgets = {
            "content": forms.Textarea(attrs={"rows": 5, "cols": 40}),
        }

        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone", "address", "city", "provincia", "country"]



class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Estilizar campos
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Correo electrónico'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})






class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



class PedidosForm(forms.ModelForm):
    
    class Meta:
        model = Pedidos
        fields = "__all__"
