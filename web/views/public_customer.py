from django.utils.safestring import mark_safe
from stark.service.v1 import StarkHandler, get_choice_text, get_m2m_text, BootStrapModelForm
from web import models
from django.urls import re_path
from django.shortcuts import HttpResponse, redirect, render
from django.db import transaction
from web.views.base import PermissionHandler


class PublicCustomerModelForm(BootStrapModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant', ]


class PublicCustomerHandler(PermissionHandler, StarkHandler):

    def display_record(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '跟进记录'
        return mark_safe('<a href="%s">查看跟进记录</a>' % self.reverse_record_url(pk=obj.pk))

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
        'date',
        'last_consult_date'
    ]
    model_form_class = PublicCustomerModelForm

    def get_queryset(self, request, *args, **kwargs):
        return self.model_class.objects.filter(consultant__isnull=True)

    @property
    def get_record_url_name(self):
        return self.get_url_name('record_view')

    def reverse_record_url(self, *args, **kwargs):
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
        return self.reverse_commons_url(self.get_record_url_name, *args, **kwargs)

    # 增加URL
    def extra_urls(self):
        patterns = [
            re_path(r'^record/(?P<pk>\d+)/$',
                    self.wrapper(self.recorde_view),
                    name=self.get_record_url_name),
        ]
        return patterns

    def recorde_view(self, request, pk):
        record_list = models.CounsultRecord.objects.filter(customer_id=pk)
        return render(request, 'consult_record.html', {'record_list': record_list})

    def action_multi_apply(self, request, *args, **kwargs):
        current_user_id = self.request.session['user_info']['id']
        max_private_count = models.Customer.MAX_PRIVATE_COUNT  # MAX_PRIVATE_COUNT = 150
        pk_list = request.POST.getlist('pk')
        private_customer_count = models.Customer.objects.filter(consultant_id=current_user_id, status=2).count()
        # 私户个数限制
        if (private_customer_count + len(pk_list)) > max_private_count:
            return HttpResponse(
                '添加失败,您账户上有%s位客户未成交,剩余可申请转私户的名额为: %s' % (
                    private_customer_count, max_private_count - private_customer_count))
        flag = False
        # 数据库中加锁
        # 数据库的事务
        with transaction.atomic():
            # 在数据库中加锁
            origin_queryset = models.Customer.objects.filter(id__in=pk_list, consultant__isnull=True,
                                                             status=2).select_for_update()
            if len(origin_queryset) == len(pk_list):
                models.Customer.objects.filter(id__in=pk_list, consultant__isnull=True, status=2).update(
                    consultant_id=current_user_id)
                flag = True
            if not flag:
                return HttpResponse('选中的客户用已有其他人员已申请')

    action_multi_apply.text = '批量申请到我的账户'
    action_list = [action_multi_apply, ]
