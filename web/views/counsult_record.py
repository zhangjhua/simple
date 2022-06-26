from stark.service.v1 import StarkHandler, BootStrapModelForm
from django.conf.urls import re_path
from web import models
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponse
from web.views.base import PermissionHandler


class CounsultRecordModelForm(BootStrapModelForm):
    class Meta:
        model = models.CounsultRecord
        fields = ['note', ]


class CounsultRecordHandler(StarkHandler):
    model_form_class = CounsultRecordModelForm
    change_list_template = 'consult_record.html'
    list_display = ['consultant', 'note', 'date']

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
            re_path(r'^change/(?P<customer_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.change_view),
                    name=self.get_change_url_name),
            re_path(r'^delete/(?P<customer_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.delete_view),
                    name=self.get_delete_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        current_user_id = self.request.session['user_info']['id']
        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=current_user_id)

    def save(self, request, form, is_update, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        current_user_id = self.request.session['user_info']['id']
        object_exists = models.Customer.objects.filter(id=customer_id, consultant_id=current_user_id).exists()
        if not object_exists:
            return HttpResponse('操作有误,请重新操作')
        if not is_update:
            form.instance.customer_id = customer_id
            form.instance.consultant_id = current_user_id
        form.save()

    def display_edit_del(self, obj=None, is_header=None, *args, **kwargs):
        """
        自定义list_display显示的列,包括表头和内容
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return '操作'
        customer_id = kwargs.get('customer_id')
        tab = '<a href="%s">编辑</a> <a href="%s">删除</a>' % (
            self.reverse_change_url(pk=obj.pk, customer_id=customer_id),
            self.reverse_delete_url(pk=obj.pk, customer_id=customer_id))
        return mark_safe(tab)

    def get_change_object(self, request, pk, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        current_user_id = self.request.session['user_info']['id']
        return self.model_class.objects.filter(id=pk, customer_id=customer_id,
                                               customer__consultant_id=current_user_id).first()

    def get_delete_object(self, request, pk, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        current_user_id = self.request.session['user_info']['id']
        record_queryset = self.model_class.objects.filter(id=pk, customer_id=customer_id,
                                                          customer__consultant_id=current_user_id)
        if not record_queryset:
            return HttpResponse('要删除的记录不存在')
        record_queryset.delete()
