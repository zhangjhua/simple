from stark.service.v1 import StarkHandler, get_choice_text, BootStrapModelForm
from django.urls import re_path
from web import models
from django.shortcuts import HttpResponse
from django import forms
from web.views.base import PermissionHandler


class PaymentRecordModelForm(BootStrapModelForm):
    class Meta:
        model = models.PaymentRecord
        fields = ['pay_type', 'paid_fee', 'class_list', 'note']


class StudentPaymentRecordFrom(BootStrapModelForm):
    qq = forms.CharField(max_length=32, label='QQ')
    mobile = forms.CharField(max_length=32, label='手机号')
    emergency_contract = forms.CharField(max_length=32, label='紧急联系方式')

    class Meta:
        model = models.PaymentRecord
        fields = ['pay_type', 'paid_fee', 'class_list', 'qq', 'mobile', 'emergency_contract', 'note']


class PaymentRecordHandler(PermissionHandler, StarkHandler):

    def get_module_form_class(self, is_add, request, pk, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        student_exists = models.Student.objects.filter(customer_id=customer_id).exists()
        if student_exists:
            return PaymentRecordModelForm
        return StudentPaymentRecordFrom

    list_display = [
        get_choice_text('费用类型', 'pay_type'),
        'paid_fee',
        'class_list',
        'consultant',
        get_choice_text('确认状态', 'confirm_status'),
    ]

    def get_urls(self):
        """
        app_label: 得到的是app名称 self.model_class._meta.app_label
        model_name: 得到的是表的名称,小写 self.model_class._meta.model_name
        :return:
        """
        # app_label, model_name, prev = self.model_class._meta.app_label, self.model_class._meta.model_name, self.prev
        patterns = [
            re_path(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        current_user_id = self.request.session['user_info']['id']
        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=current_user_id)

    def get_list_display(self, request, *args, **kwargs):
        return self.list_display

    def save(self, request, form, is_update, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        current_user_id = self.request.session['user_info']['id']
        object_exists = models.Customer.objects.filter(id=customer_id, consultant_id=current_user_id).exists()
        if not object_exists:
            return HttpResponse('操作有误,请重新操作')
        form.instance.customer_id = customer_id
        form.instance.consultant_id = current_user_id
        # 创建缴费记录信息
        form.save()
        # 创建学员信息
        class_list = form.cleaned_data['class_list']
        search_student_object = models.Student.objects.filter(customer_id=customer_id).first()
        if not search_student_object:
            qq = form.cleaned_data['qq']
            mobile = form.cleaned_data['mobile']
            emergency_contract = form.cleaned_data['emergency_contract']
            student_object = models.Student.objects.create(
                customer_id=customer_id,
                qq=qq,
                mobile=mobile,
                emergency_contract=emergency_contract
            )

            student_object.class_list.add(class_list.id)
        else:
            search_student_object.class_list.add(class_list.id)
