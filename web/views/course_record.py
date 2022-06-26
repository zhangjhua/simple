from stark.service.v1 import StarkHandler, BootStrapModelForm
from django.urls import re_path
from web import models
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponse, render
from django.forms.models import modelformset_factory
from web.views.base import PermissionHandler


class CourseRecordModelForm(BootStrapModelForm):
    class Meta:
        model = models.CourseRecord
        fields = ['day_num', 'teacher']


class StudyRecordModelForm(BootStrapModelForm):
    class Meta:
        model = models.StudyRecord
        fields = ['record', ]


class CourseRecordHandler(StarkHandler):
    model_form_class = CourseRecordModelForm

    def get_urls(self):
        """
        app_label: 得到的是app名称 self.model_class._meta.app_label
        model_name: 得到的是表的名称,小写 self.model_class._meta.model_name
        :return:
        """
        # app_label, model_name, prev = self.model_class._meta.app_label, self.model_class._meta.model_name, self.prev
        patterns = [
            re_path(r'^list/(?P<class_object_id>\d+)/$', self.wrapper(self.changelist_view),
                    name=self.get_list_url_name),
            re_path(r'^add/(?P<class_object_id>\d+)/$', self.wrapper(self.add_view),
                    name=self.get_add_url_name),
            re_path(r'^change/(?P<class_object_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.change_view),
                    name=self.get_change_url_name),
            re_path(r'^delete/(?P<class_object_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.delete_view),
                    name=self.get_delete_url_name),
            re_path(r'^attendance/(?P<course_record_id>\d+)/$', self.wrapper(self.attendance_view),
                    name=self.get_url_name('attendance')),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def display_attendance(self, obj=None, is_header=None, *args, **kwargs):
        """
        自定义list_display显示的列,包括表头和内容
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return '考情记录'
        name = self.get_url_name('attendance')
        attendance_url = self.reverse_commons_url(name, course_record_id=obj.pk)
        print(attendance_url)
        tab = '<a target="_blank" href="%s">考情</a>' % attendance_url
        return mark_safe(tab)

    list_display = [StarkHandler.display_checkbox, 'class_object', 'day_num', 'teacher', 'date', display_attendance]

    def display_edit_del(self, obj=None, is_header=None, *args, **kwargs):
        """
        自定义list_display显示的列,包括表头和内容
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return '操作'
        class_object_id = kwargs.get('class_object_id')
        tab = '<a href="%s">编辑</a> <a href="%s">删除</a>' % (
            self.reverse_change_url(pk=obj.pk, class_object_id=class_object_id),
            self.reverse_delete_url(pk=obj.pk, class_object_id=class_object_id))
        return mark_safe(tab)

    def get_queryset(self, request, *args, **kwargs):
        class_object_id = kwargs.get('class_object_id')
        return self.model_class.objects.filter(class_object_id=class_object_id)

    def save(self, request, form, is_update, *args, **kwargs):
        class_object_id = kwargs.get('class_object_id')
        if not is_update:
            form.instance.class_object_id = class_object_id
            form.save()

    def action_multi_init(self, request, *args, **kwargs):
        class_object_id = kwargs.get('class_object_id')
        course_pk_list = request.POST.getlist('pk')
        class_object = models.ClassList.objects.filter(id=class_object_id).first()
        if not class_object:
            return HttpResponse('班级不存在,请重新选择')
        # 通过班级反向查询到班级内有的学生(ManyToMany)
        student_object_list = class_object.student_set.all()
        for course_record_id in course_pk_list:
            # 判断上课记录是否合法
            course_record_object = models.CourseRecord.objects.filter(id=course_record_id,
                                                                      class_object_id=class_object_id).first()
            if not course_record_object:
                continue

            # 判断上课记录的考情记录是否已经存在
            study_recode_exists = models.StudyRecord.objects.filter(course_record=course_record_object).exists()
            if study_recode_exists:
                continue

            # 批量初始化
            study_record_object_list = [models.StudyRecord(course_record_id=course_record_id, student_id=stu.id) for stu
                                        in student_object_list]
            models.StudyRecord.objects.bulk_create(study_record_object_list, batch_size=50)

    def attendance_view(self, request, course_record_id, *args, **kwargs):
        """
        考情记录批量修改
        :param request:
        :param course_record_id:
        :param args:
        :param kwargs:
        :return:
        """
        study_record_object_list = models.StudyRecord.objects.filter(course_record_id=course_record_id)
        study_model_formset = modelformset_factory(models.StudyRecord, form=StudyRecordModelForm, extra=0)
        if request.method == 'POST':
            formset = study_model_formset(queryset=study_record_object_list, data=request.POST)
            if formset.is_valid():
                formset.save()
                return render(request, 'attendance.html', {'formset': formset})
        formset = study_model_formset(queryset=study_record_object_list)

        return render(request, 'attendance.html', {'formset': formset})

    action_multi_init.text = '批量初始化考情'
    action_list = [action_multi_init, ]
