from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Company, Domain
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class UserForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    role = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label='User Roles',
    )

    status = forms.BooleanField(
        initial=True,
        required=False,
        label='Active',
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = get_user_model()  # Use get_user_model to ensure compatibility with custom user models
        fields = ['email', 'username', 'password1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password2')
        self.fields['password1'].help_text = ""
    
    def clean_username(self):
        username = self.cleaned_data['username']
        user_pk = self.instance.pk
        if User.objects.filter(username=username).exclude(pk=user_pk).exists():
            raise forms.ValidationError(_('This username is already in use.'))
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_admin = self.cleaned_data['role'] == 'admin'
        user.is_user = self.cleaned_data['role'] == 'user'
        user.is_active = self.cleaned_data['status']
        if commit:
            user.save()
        return user
        

class CompanyForm(forms.ModelForm):
    
    class Meta:
        model = Company
        fields = '__all__'
        labels = {
            'name': 'Company Name',
            'address': 'Company Address',
            'location': 'Company Location',
        }
        

class DomainForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].error_messages = {'required': 'Please specify the company.'}


    class Meta:
        model = Domain
        fields = '__all__'
        labels = {
            'name': 'Domain Name',
            'registration_date': 'Date of Registration',
            'expiry_date': 'Date of Expiry',
            'company': 'Belongs To(Company):',
            'registrar_name': 'Registrar Name',
        }