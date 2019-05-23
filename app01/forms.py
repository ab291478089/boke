from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError
from app01 import models


class RegForm(Form):
    username = fields.CharField(
        max_length=16,
        label="用户名",
        error_messages={
            'max_length': '太长了',
            'required': '用户名不能为空'
        },
        widget=widgets.TextInput(attrs={'class': 'form-control'}, )

    )
    password = fields.CharField(
        min_length=6,
        label="密码",
        widget=widgets.PasswordInput(attrs={'class': 'form-control'}, ),
        error_messages={
            'min_length': '太短了',
            'required': '密码不能为空'
        },
    )
    re_password = fields.CharField(
        min_length=6,
        label='确认密码',
        widget=widgets.PasswordInput(attrs={'class': 'form-control'}, ),
        error_messages={
            'min_length': '太短了',
            'required': '密码不能为空'
        }
    )
    email = fields.EmailField(
        label='邮箱',
        widget=widgets.EmailInput(attrs={'class': 'form-control'}, ),
        error_messages={
            'invalid': '邮箱格式不正确',
            'required': '邮箱不能为空',
        }
    )

    # 重写username字段的局部钩子
    def clean_username(self):
        username = self.cleaned_data.get('username')
        is_exist = models.UserInfo.objects.filter(username=username)
        if is_exist:
            # 表示用户名已注册
            self.add_error('username', ValidationError('用户名已存在'))
        else:
            return username

        # 重写email字段的局部钩子
    def clean_email(self):
        email = self.cleaned_data.get('email')
        is_exist = models.UserInfo.objects.filter(email=email)
        if is_exist:
            # 表示用户名已注册
            self.add_error('email', ValidationError('邮箱已被注册！'))
        else:
            return email


    # 重写全局钩子函数，对确认密码进行校验
    def clean(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')

        if re_password and re_password != password:
            self.add_error('re_password', ValidationError('两次密码不一致'))
        else:
            return self.cleaned_data
