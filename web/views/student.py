from stark.service.v1 import StarkHandler, get_choice_text, get_m2m_text, BootStrapModelForm, Option
from django.urls import re_path
from web import models
from django.utils.safestring import mark_safe
from django.shortcuts import reverse
from web.views.base import PermissionHandler


class StudentModelForm(BootStrapModelForm):
    class Meta:
        model = models.Student
        exclude = ['customer', 'class_list', 'student_status']


class StudentHandler(PermissionHandler,StarkHandler):

    def display_score(self, obj=None, is_header=None, *args, **kwargs):

        if is_header:
            return '积分管理'
        record_url = reverse('stark:web_scorerecord_list', kwargs={'student_id': obj.pk})
        return mark_safe('<a target="_blank" href="%s">%s</a>' % (record_url, obj.score))  # 通过input框拿到当前数据的id值

    model_form_class = StudentModelForm
    list_display = ['customer', 'qq', 'mobile', 'emergency_contract', get_m2m_text('班级', 'class_list'),
                    get_choice_text('学员状态', 'student_status'),
                    display_score, ]

    def get_add_btn(self, request, *args, **kwargs):
        return None

    def get_list_display(self, request, *args, **kwargs):
        value = []
        if self.list_display:
            value.extend(self.list_display)
            value.append(type(self).display_edit)
        return value

    def get_urls(self):
        """
        app_label: 得到的是app名称 self.model_class._meta.app_label
        model_name: 得到的是表的名称,小写 self.model_class._meta.model_name
        :return:
        """
        # app_label, model_name, prev = self.model_class._meta.app_label, self.model_class._meta.model_name, self.prev
        patterns = [
            re_path(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    search_list = ['customer__name', 'qq', 'mobile']
    search_group = [
        Option(field='class_list', text_func=lambda x: '%s-%s' % (x.school.title, str(x))),
        Option(field='student_status'),
    ]
