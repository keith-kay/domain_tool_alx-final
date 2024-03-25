from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import Company, Domain, User

class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    def clean_username(self):
        username = self.cleaned_data['username']
        user_pk = self.instance.pk
        if User.objects.filter(username=username).exclude(pk=user_pk).exists():
            raise forms.ValidationError(_('This username is already in use.'))
        return username

class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserAdminForm
    list_display = ('username', 'email', 'is_admin', 'is_user', 'is_staff', 'is_active')
    list_filter = ('is_admin', 'is_user', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('username',)}),
        (_('Permissions'), {'fields': ('is_admin', 'is_user', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_admin', 'is_user', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

# Register your models here.
class CompanyAdmin(admin.ModelAdmin):
    pass

admin.site.register(Company, CompanyAdmin)
admin.site.register(Domain)
admin.site.register(User, CustomUserAdmin)
