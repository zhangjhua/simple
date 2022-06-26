from stark.service.v1 import StarkHandler, get_choice_text
from django.urls import re_path
from web import models
from web.views.base import PermissionHandler


class CheckPaymentRecordHandler(PermissionHandler, StarkHandler):
    order_list = ['-id', 'confirm_status']
    list_display = [StarkHandler.display_checkbox, 'customer', get_choice_text('费用类型', 'pay_type'), 'paid_fee',
                    'class_list',
                    'apply_date', get_choice_text('确认状态', 'confirm_status'), 'consultant']

    def get_list_display(self,request, *args, **kwargs):
        return self.list_display

    def get_add_btn(self, request, *args, **kwargs):
        return None

    def get_urls(self):
        """
        app_label: 得到的是app名称 self.model_class._meta.app_label
        model_name: 得到的是表的名称,小写 self.model_class._meta.model_name
        :return:
        """
        # app_label, model_name, prev = self.model_class._meta.app_label, self.model_class._meta.model_name, self.prev
        patterns = [re_path(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name)]
        patterns.extend(self.extra_urls())
        return patterns

    def action_multi_confirm(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        for pk in pk_list:
            # 获取到当前申请的对象
            payment_object = self.model_class.objects.filter(id=pk, confirm_status=1).first()
            if not payment_object:
                continue
            # 改变状态
            payment_object.confirm_status = 2
            payment_object.save()
            # 通过外键关联去查询Customer表下的状态这个字段,进行赋值更新
            payment_object.customer.status = 1
            payment_object.customer.save()

            payment_object.customer.student.student_status = 2
            payment_object.customer.student.save()

    def action_multi_refund(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        for pk in pk_list:
            # 获取到当前申请的对象
            payment_object = self.model_class.objects.filter(id=pk, confirm_status=1).first()
            if not payment_object:
                continue
            # 改变状态
            payment_object.confirm_status = 2
            payment_object.save()
            # 通过外键关联去查询Customer表下的状态这个字段,进行赋值更新
            payment_object.customer.status = 2
            payment_object.customer.save()

            payment_object.customer.student.student_status = 4
            payment_object.customer.student.save()

    def action_multi_cancel(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list, confirm_status=1).update(confirm_status=3)

    action_multi_confirm.text = '批量确认'
    action_multi_cancel.text = '批量驳回'
    action_multi_refund.text = '批量退费'
    action_list = [action_multi_confirm, action_multi_cancel, action_multi_refund, ]
