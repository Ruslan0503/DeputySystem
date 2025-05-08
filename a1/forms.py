from django import forms
from .models import Profile, Role
from django.contrib.auth.models import User

ROLE_CHOICES = [
    ('ishchi guruh rahbari', 'Ishchi guruh rahbari'),
]

class CustomUserForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label='Ism')
    surname = forms.CharField(max_length=100, label='Familya')
    username = forms.CharField(max_length=150, label="Foydalanuvchi nomi")
    password = forms.CharField(widget=forms.PasswordInput, label="Parol")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Parolni tasdiqlash")
    phone_number = forms.CharField(max_length=15, required=False, label = "Telefon no'mer")
    profilePhoto = forms.ImageField(required=False, label = "Foydalanuvchi Rasmi")
    roles = forms.MultipleChoiceField(
    	choices = ROLE_CHOICES,
    	widget = forms.CheckboxSelectMultiple,
    	label = "Roli",
        required = False
    	)
    class Meta:
        model = Profile
        fields = ['name','surname','username','password','confirm_password',
        'phone_number','okrugId','profilePhoto','roles']

        labels = {
            "okrugId":"Okrugni tanlang"
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

