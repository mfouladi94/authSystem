from django import forms


class LoginForm(forms.Form):
    mobile = forms.CharField(max_length=11 , min_length=11)



class RegisterForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    mobile = forms.CharField(max_length=11 , min_length=11)
