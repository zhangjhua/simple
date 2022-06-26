from stark.service.v1 import StarkHandler, BootStrapModelForm, get_choice_text, get_m2m_text
from web import models
from django.utils.safestring import mark_safe
from django.urls import reverse
from web.views.base import PermissionHandler


class PrivateCustomerModelForm(BootStrapModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant', ]


class PrivateCustomerHandler(PermissionHandler, StarkHandler):

    def display_record(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '跟进记录'
        record_url = reverse('stark:web_counsultrecord_list', kwargs={'customer_id': obj.pk})
        return mark_safe('<a target="_blank" href="%s">跟进记录</a>' % record_url)

    def display_pay_record(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '缴费记录'
        record_url = reverse('stark:web_paymentrecord_list', kwargs={'customer_id': obj.pk})
        return mark_safe('<a target="_blank" href="%s">缴费记录</a>' % record_url)

    model_form_class = PrivateCustomerModelForm
    list_display = [
        StarkHandler.display_checkbox,
        'name',
        'qq',
        get_choice_text('状态', 'status'),
        get_choice_text('性别', 'gender'),
        get_m2m_text('咨询课程', 'course'),
        get_choice_text('客户来源', 'source'),
        get_choice_text('学历', 'education'),
        get_choice_text('工作经验', 'experience'),
        get_choice_text('职业状态', 'work_status'),
        'company',
        display_record,
        display_pay_record,
    ]

    def get_queryset(self, request, *args, **kwargs):
        current_user_id = self.request.session['user_info']['id']
        return self.model_class.objects.filter(consultant_id=current_user_id)

    def save(self, request, form, is_update, *args, **kwargs):
        if not is_update:
            current_user_id = request.session['user_info']['id']
            form.instance.consultant_id = current_user_id
        form.save()

    def action_multi_remove(self, request, *args, **kwargs):
        current_user_id = self.request.session['user_info']['id']
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list, consultant_id=current_user_id).update(consultant=None)

    action_multi_remove.text = '批量移出我的账户'
    action_list = [action_multi_remove, ]
