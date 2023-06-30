from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control email-form',
                                                            'placeholder': 'Email'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control user-form',
                                                             'placeholder': 'Username'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control password1-form'
        self.fields['password2'].widget.attrs['class'] = 'form-control password2-form'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class LoginForm(AuthenticationForm):
    username_form = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control user-form',
                                                                  'placeholder': 'Username'}))
    password_form = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control password1-form',
                                                                      'placeholder': 'Password'}))
