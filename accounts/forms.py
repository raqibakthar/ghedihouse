from dataclasses import fields
from logging import PlaceHolder
from pyexpat import model
from django import forms
from .models import Account, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': '',
       

    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': ''
    }))
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "password does not match"
            )


    def __init__(self, *args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs ['class'] = 'form-control'

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name','last_name','phone_number')

    def __init__(self, *args,**kwargs):
         super(UserForm,self).__init__(*args,**kwargs)
         for field in self.fields:
            self.fields[field].widget.attrs ['class'] = 'form-control'
 
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('address_line_1','address_line_2','city','state','country')
    
    def __init__(self, *args,**kwargs):
         super(UserProfileForm,self).__init__(*args,**kwargs)
         for field in self.fields:
            self.fields[field].widget.attrs ['class'] = 'form-control'