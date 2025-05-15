from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from .models import Profile

class RegisterForm(UserCreationForm):
    username = forms.CharField(label="Имя пользователя", widget=forms.TextInput(attrs={
        'placeholder': 'Введите имя пользователя'
    }))
    email = forms.EmailField(label="Электронная почта", widget=forms.EmailInput(attrs={
        'placeholder': 'Введите вашу почту'
    }))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={
        'placeholder': 'Введите пароль'
    }))
    password2 = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput(attrs={
        'placeholder': 'Повторите пароль'
    }))

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)


class LoginForm(AuthenticationForm):
    username = UsernameField(label="Имя пользователя",widget=forms.TextInput(attrs={'autofocus': True,
            'placeholder': 'Введите имя пользователя'
        })
    )
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={
        'placeholder': 'Введите пароль'
    }))


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'placeholder': 'Имя пользователя'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Ваш email'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(
        label="Аватар",
        required=False,
    )
    description = forms.CharField(
        label="Описание",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Расскажите о себе'
        })
    )

    class Meta:
        model = Profile
        fields = ['avatar', 'description']
