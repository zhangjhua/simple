from stark.service.v1 import StarkHandler, get_datetime_text, get_m2m_text, BootStrapModelForm, Option
from stark.forms.widgets import Datetimepicker
from web.models import ClassList
from django.utils.safestring import mark_safe
from django.urls import reverse
from web.views.base import PermissionHandler


class ClassListForm(BootStrapModelForm):
    class Meta:
        model = ClassList
        fields = "__all__"
        widgets = {
            'start_date': Datetimepicker,
            'graduate': Datetimepicker,
        }


class ClassListHandler(PermissionHandler, StarkHandler):

    def display_class(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '班级'
        return '%s %s期' % (obj.course.name, obj.semester)

    def display_course_score(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '上课记录'
        record_url = reverse('stark:web_courserecord_list', kwargs={'class_object_id': obj.pk})
        return mark_safe('<a target="_blank" href="%s">上课记录</a>' % record_url)  # 通过input框拿到当前数据的id值

    model_form_class = ClassListForm

    list_display = ['school',
                    display_class,
                    get_datetime_text('日期', 'start_date'),
                    'class_teacher',
                    get_m2m_text('任课老师', 'tech_teacher'),
                    display_course_score,
                    ]

    search_group = [
        Option('school'),
        Option('course'),
    ]
