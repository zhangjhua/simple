from stark.service.v1 import StarkHandler, BootStrapModelForm
from django.urls import re_path
from web import models
from django.shortcuts import HttpResponse
from web.views.base import PermissionHandler


class ScoreRecordModelForm(BootStrapModelForm):
    class Meta:
        model = models.ScoreRecord
        fields = ['content', 'score']


class ScoreRecordHandler(PermissionHandler, StarkHandler):
    list_display = ['student', 'content', 'score', 'user']
    model_form_class = ScoreRecordModelForm

    def get_urls(self):
        """
        app_label: 得到的是app名称 self.model_class._meta.app_label
        model_name: 得到的是表的名称,小写 self.model_class._meta.model_name
        :return:
        """
        # app_label, model_name, prev = self.model_class._meta.app_label, self.model_class._meta.model_name, self.prev
        patterns = [
            re_path(r'^list/(?P<student_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^add/(?P<student_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            # re_path(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view),
            #         name=self.get_change_url_name),
            # re_path(r'^delete/(?P<pk>\d+)/$', self.wrapper(self.delete_view),
            #         name=self.get_delete_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        return self.model_class.objects.filter(student_id=student_id)

    def get_list_display(self, request, *args, **kwargs):
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value

    def save(self, request, form, is_update, *args, **kwargs):
        student_id = kwargs.get('student_id')
        current_user_id = self.request.session['user_info']['id']
        object_exists = models.ScoreRecord.objects.filter(id=student_id, user_id=current_user_id).exists()
        print(object_exists)
        if not object_exists:
            return HttpResponse('操作有误,请重新输入')
        # 赋值默认值(不能去选择学生和,操作者,默认为跳转的学生,和当前登陆的用户)
        form.instance.student_id = student_id
        form.instance.user_id = current_user_id
        form.save()
        if form.instance.score > 0:
            form.instance.student.score += abs(form.instance.score)
        else:
            form.instance.student.score -= abs(form.instance.score)
        form.instance.student.save()
