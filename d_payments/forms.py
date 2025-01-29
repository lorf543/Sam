from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from d_store.models import UserProfile,Product
from .models import InvoinceProduct



class UserProfileForm(UserCreationForm):
    # Campos personalizados adicionales del modelo UserProfile
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Número de Teléfono'}),
        required=True
    )
    address = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Dirección'}),
        required=False
    )
    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Ciudad'}),
        required=False
    )
    provincia = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Provincia'}),
        required=False
    )
    country = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'País'}),
        required=False
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        # Guarda el usuario
        user = super().save(commit=False)
        if commit:
            user.save()
            # Guarda el perfil personalizado
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                provincia=self.cleaned_data['provincia'],
                country=self.cleaned_data['country']
            )
        return user
    
    
class SaleForm(forms.ModelForm):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=True
    )
    payment_method = forms.ChoiceField(
        choices=[('Efectivo', 'Efectivo'), ('Tarjeta', 'Tarjeta')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = InvoinceProduct
        fields = ['quantity', 'payment_method']