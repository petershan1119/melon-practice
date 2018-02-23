from django import forms

__all__ = (
    'SignupForm',
)


class SignupForm(forms.Form):
    username = forms.CharField(
        label='아이디',
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='비밀번호 확인',
        widget=forms.PasswordInput
    )