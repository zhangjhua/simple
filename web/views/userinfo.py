from stark.service.v1 import StarkHandler, get_choice_text, BootStrapModelForm, StarkForm, Option
from web import models
from django import forms
from django.core.exceptions import ValidationError
from web.utils.md5 import gen_md5
from django.utils.safestring import mark_safe
from django.urls import re_path
from django.shortcuts import HttpResponse, render, redirect
from web.views.base import PermissionHandler


class ResetPasswordForm(PermissionHandler, StarkForm):
    # 密文不可见
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    def clean_confirm_password(self):
        """
        验证密码是否一致
        :return:
        """
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise ValidationError('两次密码不一致')
        else:
            return confirm_password

    def clean(self):
        # 进行md5的加密
        self.cleaned_data['password'] = gen_md5(self.cleaned_data['password'])
        return self.cleaned_data


class UserInfoAddModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(label='确认密码')

    class Meta:
        model = models.UserInfo
        fields = ['name', 'password', 'confirm_password', 'nickname', 'gender', 'phone', 'email', 'depart', 'roles']

    def clean_confirm_password(self):
        """
        验证密码是否一致
        :return:
        """
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise ValidationError('两次密码不一致')
        else:
            return confirm_password

    # 重写Form父类clean 方法进行md5的加密
    """
    父类里面的clean方法
        def clean(self):
        '''
        Hook for doing any extra form-wide cleaning after Field.clean() has been
        called on every field. Any ValidationError raised by this method will
        not be associated with a particular field; it will have a special-case
        association with the field named '__all__'.
        '''
        return self.cleaned_data
    """

    def clean(self):
        password = self.cleaned_data['password']
        self.cleaned_data['password'] = gen_md5(password)
        return self.cleaned_data


class UserInfoChangeModelForm(BootStrapModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['name', 'nickname', 'gender', 'phone', 'email', 'depart', 'roles']


class UserInfoHandler(StarkHandler):
    def display_reset_pwd(self, obj=None, is_header=None):
        if is_header:
            return '重置密码'
        return mark_safe('<a href="%s">重置密码</a>' % self.reverse_reset_pwd_url(pk=obj.pk))

    list_display = ['name', get_choice_text('性别', 'gender'), 'phone', 'email', 'depart', display_reset_pwd]

    # 重写了modelFrom
    # 编辑和删除都用这个modelForm
    # model_form_class = UserInfoAddModelForm

    def get_module_form_class(self, is_add, request, pk, *args, **kwargs):
        if is_add:
            return UserInfoAddModelForm
        return UserInfoChangeModelForm

    def reset_password_view(self, request, pk):

        userinfo_object = models.UserInfo.objects.filter(id=pk).first()
        if not userinfo_object:
            return HttpResponse('不存在该ID')
        if request.method == 'GET':
            form = ResetPasswordForm()
            return render(request, 'stark/change.html', {'form': form})
        form = ResetPasswordForm(data=request.POST)
        if form.is_valid():
            userinfo_object.password = form.cleaned_data['password']
            userinfo_object.save()
            return redirect(self.reverse_list_url())
        return render(request, 'stark/change.html', {'form': form})

    @property
    def get_reset_pwd_url_name(self):
        return self.get_url_name('reset_pwd')

    def reverse_reset_pwd_url(self, *args, **kwargs):
        """
        # 根据别名反向生成url
        # name = '%s:%s' % (self.site.namespace, self.get_reset_pwd_url_name)
        # base_url = reverse(name, args=args, kwargs=kwargs)
        # if not self.request.GET:
        #     reset_pwd_url = base_url
        # else:
        #     param = self.request.GET.urlencode()  # 后面的参数
        #     new_query_dict = QueryDict(mutable=True)
        #     new_query_dict['_filter'] = param
        #     reset_pwd_url = '%s?%s' % (base_url, new_query_dict.urlencode())
        # return reset_pwd_url
        """
        return self.reverse_commons_url(self.get_reset_pwd_url_name, *args, **kwargs)

    search_group = [
        Option(field='gender'),
        Option(field='depart'),
    ]
    search_list = ['nickname__contains', 'phone__contains']

    # 增加URL
    def extra_urls(self):
        return [
            re_path(r'^reset/password/(?P<pk>\d+)/$', self.wrapper(self.reset_password_view),
                    name=self.get_reset_pwd_url_name),
        ]
