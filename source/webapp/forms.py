from django.core.exceptions import ValidationError
from django.forms import ModelForm

from webapp.models import Order, OrderProduct


class BasketOrderCreateForm(ModelForm):
    def __init__(self, user=None, **kwargs):
        self.user = user
        if user and not user.is_authenticated:
            self.user = None
        super().__init__(**kwargs)

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not self.user and not self.cleaned_data.get('first_name'):
            raise ValidationError('Вы должны авторизоваться либо указать ваше имя!')
        return first_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not self.user and not self.cleaned_data.get('email'):
            raise ValidationError('Вы должны авторизоваться либо указать ваш email!')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not self.user and not self.cleaned_data.get('phone'):
            raise ValidationError('Вы должны авторизоваться либо указать ваш телефон!')
        return phone

    def save(self, commit=True):
        self.instance.user = self.user
        return super().save(commit)

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone']


class ManualOrderForm(ModelForm):
    def __init__(self, user=None, **kwargs):
        self.user = user
        if user and not user.is_authenticated:
            self.user = None
        super().__init__(**kwargs)

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not self.user and not self.cleaned_data.get('first_name'):
            raise ValidationError('Вы должны указать пользователя либо его имя!')
        return first_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not self.user and not self.cleaned_data.get('email'):
            raise ValidationError('Вы должны авторизоваться либо указать ваш email!')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not self.user and not self.cleaned_data.get('phone'):
            raise ValidationError('Вы должны авторизоваться либо указать ваш телефон!')
        return phone

    class Meta:
        model = Order
        fields = ['user', 'first_name', 'last_name', 'email', 'phone']


class OrderProductForm(ModelForm):
    class Meta:
        model = OrderProduct
        fields = ['product', 'amount']