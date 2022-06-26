from django.urls import path, re_path
import functools
from django.shortcuts import render, HttpResponse, redirect
from types import FunctionType
from django.utils.safestring import mark_safe
from django.urls import reverse
from stark.utils.pagination import Pagination
from django.http import QueryDict
from django import forms
from django.db.models import Q, ForeignKey, ManyToManyField
import datetime


def get_choice_text(title, field):
    """
    对于stark组件 中 定义列时,choice如果想要显示中文信息,调用此方法即可
    :param title:希望页面显示的表头
    :param field:字段名称
    :return:
    """

    def inner(self, obj=None, is_header=None,*args,**kwargs):
        if is_header:
            return title
        method = "get_%s_display" % field
        return getattr(obj, method)

    return inner


def get_datetime_text(title, field, time_format='%Y-%m-%d'):
    def inner(self, obj=None, is_header=None,*args,**kwargs):
        if is_header:
            return title
        datetime_value = getattr(obj, field)
        return datetime_value.strftime(time_format)

    return inner


def get_m2m_text(title, field):
    def inner(self, obj=None, is_header=None,*args,**kwargs):
        if is_header:
            return title
        queryset = getattr(obj, field).all()
        text_list = [str(row) for row in queryset]
        return ','.join(text_list)

    return inner


class SearchGroupRow(object):
    def __init__(self, title, queryset_or_tuple, option, query_dict):
        """

        :param title: 组合搜索的列名称
        :param queryset_or_tuple: 组合搜索的数据
        :param option: 配置
        :param query_dict: request.GET
        """
        self.queryset_or_tuple = queryset_or_tuple
        self.option = option
        self.title = title
        self.query_dict = query_dict

    # 返回一个可迭代对象
    def __iter__(self):
        yield '<div class="whole">'
        yield self.title
        yield '</div>'
        yield '<div class="other">'
        total_query_dict = self.query_dict.copy()
        total_query_dict._mutable = True
        origin_value_list = self.query_dict.getlist(self.option.field)
        if not origin_value_list:
            yield '<a class="active" href="?%s">全部</a>' % total_query_dict.urlencode()
        else:
            total_query_dict.pop(self.option.field)
            yield '<a href="?%s">全部</a>' % total_query_dict.urlencode()
        for item in self.queryset_or_tuple:
            text = self.option.get_text(item)
            value = str(self.option.get_value(item))
            # 需要request.GET
            query_dict = self.query_dict.copy()
            query_dict._mutable = True
            if not self.option.is_multi:
                query_dict[self.option.field] = value
                if value in origin_value_list:
                    query_dict.pop(self.option.field)
                    yield '<a class="active" href="?%s">%s</a>' % (query_dict.urlencode(), text)
                else:
                    yield '<a href="?%s">%s</a>' % (query_dict.urlencode(), text)
            else:
                #
                multi_value_list = query_dict.getlist(self.option.field)
                if value in multi_value_list:
                    multi_value_list.remove(value)
                    query_dict.setlist(self.option.field, multi_value_list)
                    yield '<a class="active" href="?%s">%s</a>' % (query_dict.urlencode(), text)
                else:
                    multi_value_list.append(value)
                    query_dict.setlist(self.option.field, multi_value_list)
                    yield "<a href='?%s'>%s</a>" % (query_dict.urlencode(), text)
        yield '</div>'


# SearchOption
class Option(object):
    def __init__(self, field, is_multi=False, db_condition=None, text_func=None, value_func=None, ):
        """
        :param field: 组合搜索关联的字段
        :param db_condition: 数据库关联查询时的条件
        :param text_func: 此函数用于显示组合搜索按钮页面文本
        :param value_func: 此函数用于显示组合搜索按钮值
        :param is_multi: 是否支持多选
        """
        self.field = field
        self.is_multi = is_multi
        if not db_condition:
            db_condition = {}
        self.db_condition = db_condition
        self.text_func = text_func
        self.is_choice = False
        self.value_func = value_func

    def get_db_condition(self, request, *args, **kwargs):
        return self.db_condition

    def get_queryset_or_tuple(self, model_class, request, *args, **kwargs):
        # 根据gender或depart字符串,去自己对应的Model类中找到对象
        field_object = model_class._meta.get_field(self.field)
        title = field_object.verbose_name
        # print(self.model_class._meta.get_field(item))
        if isinstance(field_object, ForeignKey) or isinstance(field_object, ManyToManyField):
            # 返回的是queryset

            db_condition = self.get_db_condition(request, *args, **kwargs)
            return SearchGroupRow(title, field_object.related_model.objects.filter(**db_condition), self, request.GET)
        else:
            # 返回的是元祖
            self.is_choice = True
            return SearchGroupRow(title, field_object.choices, self, request.GET)

    def get_text(self, field_object):
        """
        获取文本的函数
        :param field_object:
        :return:
        """
        if self.text_func:
            return self.text_func(field_object)
        if self.is_choice:
            return field_object[1]
        return str(field_object)

    def get_value(self, field_object):
        """
        获取值的函数
        :param field_object:
        :return:
        """
        if self.value_func:
            return self.value_func(field_object)
        if self.is_choice:
            return field_object[0]
        return field_object.pk


class BootStrapModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BootStrapModelForm, self).__init__(*args, **kwargs)
        # 统一给ModelForm生成字段添加样式
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StarkForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StarkForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StarkHandler(object):
    change_list_template = None
    add_template = None
    change_template = None
    delete_template = None

    list_display = []
    # 每页显示多少数据
    per_page = 10

    def display_checkbox(self, obj=None, is_header=None,*args,**kwargs):
        """
        选择checkbox
        :param obj:
        :param is_header:
        :return:
        """
        if is_header == True:
            return '选择'
        return mark_safe('<input type="checkbox" name="pk" value="%s">' % obj.pk)  # 通过input框拿到当前数据的id值

    def display_edit(self, obj=None, is_header=None,*args,**kwargs):
        """
        自定义list_display显示的列,包括表头和内容
        :param obj:
        :param is_header:
        :return:
        """
        if is_header == True:
            return '编辑'
        return mark_safe('<a href="%s">编辑</a>' % self.reverse_change_url(pk=obj.pk))

    def display_del(self, obj=None, is_header=None,*args,**kwargs):
        if is_header == True:
            return '删除'
        return mark_safe('<a href="%s">删除</a>' % self.reverse_delete_url(pk=obj.pk))

    def display_edit_del(self, obj=None, is_header=None,*args,**kwargs):
        """
        自定义list_display显示的列,包括表头和内容
        :param obj:
        :param is_header:
        :return:
        """
        if is_header == True:
            return '操作'
        tab = '<a href="%s">编辑</a> <a href="%s">删除</a>' % (
            self.reverse_change_url(pk=obj.pk), self.reverse_delete_url(pk=obj.pk))
        return mark_safe(tab)

    def get_list_display(self,request, *args, **kwargs):
        value = []
        if self.list_display:
            value.extend(self.list_display)
            value.append(type(self).display_edit_del)
        return value

    def __init__(self, site, model_class, prev):
        self.site = site
        self.model_class = model_class
        self.prev = prev
        self.request = None

    has_add_btn = True

    def get_add_btn(self,request,*args,**kwargs):
        if self.has_add_btn:
            return '<a class="btn btn-primary" href="%s">添加</a>' % self.reverse_add_url(*args,**kwargs)
        return None

    # 重写modelForm  显示
    model_form_class = None

    def get_module_form_class(self, is_add, request, pk, *args, **kwargs):
        if self.model_form_class:
            return self.model_form_class

        class DynamicModelForm(BootStrapModelForm):
            class Meta:
                model = self.model_class
                fields = '__all__'

        return DynamicModelForm

    order_list = ['id']

    # 排序规则
    def get_order_list(self):
        return self.order_list or ['id']

    search_list = []

    # 搜索框
    def get_search_list(self):
        return self.search_list

    # 组合搜索
    search_group = []

    def get_search_group(self):
        return self.search_group

    def get_search_group_condition(self, request):
        """
        获取组合搜索的条件
        :param request:
        :return:
        """
        condition = {}
        for option in self.get_search_group():
            if option.is_multi:
                value_list = request.GET.getlist(option.field)
                if not value_list:
                    continue
                condition['%s__in' % option.field] = value_list
            else:
                value = request.GET.get(option.field)
                if not value:
                    continue
                condition[option.field] = value
        return condition

    # 批量操作
    action_list = []
    def action_multi_delete(self, request, *args, **kwargs):
        pk_list = request.POST.get('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()

    action_multi_delete.text = '批量删除'

    def get_action_list(self):
        return self.action_list

    def get_queryset(self, request, *args, **kwargs):
        return self.model_class.objects

    def changelist_view(self, request, *args, **kwargs):
        """
        列表页面
        """
        # 批量操作
        action_list = self.action_list
        action_dict = {func.__name__: func.text for func in action_list}
        if request.method == 'POST':
            action_func_name = request.POST.get('action')
            if action_func_name and action_func_name in action_dict:
                getattr(self, action_func_name)(request, *args, **kwargs)

        # 查询条件
        search_list = self.get_search_list()
        search_value = request.GET.get('q')
        conn = Q()
        conn.connector = 'OR'
        if search_value:
            for item in search_list:
                conn.children.append((item, search_value))
        # 排序
        order_list = self.get_order_list()
        search_group_condition = self.get_search_group_condition(request)
        # 获取组合搜索的条件
        prev_queryset = self.get_queryset(self, request, *args, **kwargs)
        queryset = prev_queryset.filter(conn).filter(**search_group_condition).order_by(*order_list)
        all_count = queryset.count()
        query_params = request.GET.copy()
        # 每页显示多少的内容
        # 默认是不可以修改,如果想要修改page的值,需要加这个参数
        query_params._mutable = True
        pager = Pagination(
            current_page=request.GET.get('page'),
            all_count=all_count,
            base_url=request.path_info,
            query_params=query_params,
            per_page=self.per_page,
        )
        # 表头
        list_display = self.get_list_display(request, *args, **kwargs)
        header_list = []
        if list_display:
            for key_or_func in list_display:
                # 检测是否为函数
                if isinstance(key_or_func, FunctionType):
                    verbose_name = key_or_func(self, obj=None, is_header=True)
                else:
                    # 根据gender或depart字符串,去自己对应的Model类中找到对象的展示名字
                    verbose_name = self.model_class._meta.get_field(key_or_func).verbose_name
                header_list.append(verbose_name)
        else:
            header_list.append(self.model_class._meta.model_name)

        # 表的内容

        data_list = queryset[pager.start:pager.end]
        body_list = []
        for row in data_list:
            tr_list = []
            if list_display:
                for key_or_func in list_display:
                    if isinstance(key_or_func, FunctionType):
                        tr_list.append(key_or_func(self, row, False,*args,**kwargs))
                    else:
                        tr_list.append(getattr(row, key_or_func))
            else:
                tr_list.append(row)
            body_list.append(tr_list)
        # ##################### 添加按钮#############
        add_btn = self.get_add_btn(request,*args,**kwargs)

        # ########## 组合搜索 ##############
        search_group_row_list = []
        search_group = self.get_search_group()
        for option_object in search_group:
            row = option_object.get_queryset_or_tuple(self.model_class, request, *args, **kwargs)
            search_group_row_list.append(row)
        return render(request,
                      self.change_list_template or 'stark/changelist.html',
                      {
                          'header_list': header_list,
                          'body_list': body_list,
                          'pager': pager,
                          'add_btn': add_btn,
                          'search_list': search_list,
                          'search_value': search_value,
                          'action_dict': action_dict,
                          "search_group_row_list": search_group_row_list,
                      })

    # 可以重写
    def save(self, request, form, is_update, *args, **kwargs):
        """
        在使用ModelForm保存数据之前预留的钩子方法
        :param form:
        :param is_update:
        :return:
        """
        form.save()

    def add_view(self, request, *args, **kwargs):
        """
        添加页面
        :param request:
        :return:
        """
        model_form_class = self.get_module_form_class(True, request, None, *args, **kwargs)
        # print('123123',model_form_class)
        if request.method == 'GET':
            form = model_form_class()
            return render(request, self.add_template or 'stark/change.html', {'form': form})
        form = model_form_class(data=request.POST)
        if form.is_valid():
            response = self.save(request, form, False, *args, **kwargs)
            return response or redirect(self.reverse_list_url(*args, **kwargs))
        return render(request, self.add_template or 'stark/change.html', {'form': form})

    def get_change_object(self, request, pk, *args, **kwargs):
        return self.model_class.objects.filter(id=pk).first()

    def change_view(self, request, pk, *args, **kwargs):
        """
        编辑页面
        :param request:
        :param pk:
        :return:
        """

        model_form_class = self.get_module_form_class(False, request, pk, *args, **kwargs)
        # print('234234',model_form_class)
        current_change_object = self.get_change_object(request, pk, *args, **kwargs)
        if not current_change_object:
            return HttpResponse('不存在该ID')
        if request.method == 'GET':
            form = model_form_class(instance=current_change_object)
            return render(request, self.change_template or 'stark/change.html', {'form': form})
        form = model_form_class(data=request.POST, instance=current_change_object)
        if form.is_valid():
            response = self.save(request, form, True, *args, **kwargs)
            return response or redirect(self.reverse_list_url(*args, **kwargs))
        return render(request, self.change_template or 'stark/change.html', {'form': form})

    def get_delete_object(self, request, pk, *args, **kwargs):
        return self.model_class.objects.filter(id=pk).delete()

    def delete_view(self, request, pk, *args, **kwargs):
        """
        删除页面
        :param request:
        :return:
        """
        url = self.reverse_list_url(*args, **kwargs)
        if request.method == 'GET':
            return render(request, self.delete_template or 'stark/delete.html', {'cancel': url})
        response = self.get_delete_object(request, pk, *args, **kwargs)
        print(response)
        return response or redirect(url)

    def get_url_name(self, param):
        app_label, model_name, prev = self.model_class._meta.app_label, self.model_class._meta.model_name, self.prev
        if self.prev:
            return '%s_%s_%s_%s' % (app_label, model_name, self.prev, param,)
        return '%s_%s_%s' % (app_label, model_name, param,)

    @property
    def get_list_url_name(self):
        return self.get_url_name('list')

    @property
    def get_add_url_name(self):
        return self.get_url_name('add')

    @property
    def get_change_url_name(self):
        return self.get_url_name('change')

    @property
    def get_delete_url_name(self):
        return self.get_url_name('delete')

    # 公共的反向生成URL
    def reverse_commons_url(self, name_1, *args, **kwargs):
        name = '%s:%s' % (self.site.namespace, name_1)
        base_url = reverse(name, args=args, kwargs=kwargs)
        if not self.request.GET:
            add_url = base_url
        else:
            param = self.request.GET.urlencode()  # 后面的参数
            new_query_dict = QueryDict(mutable=True)
            new_query_dict['_filter'] = param
            add_url = '%s?%s' % (base_url, new_query_dict.urlencode())
        return add_url

    def reverse_add_url(self, *args, **kwargs):
        # 根据别名反向生成url
        return self.reverse_commons_url(self.get_add_url_name, *args, **kwargs)

    def reverse_list_url(self, *args, **kwargs):
        # 根据别名反向生成url

        return self.reverse_commons_url(self.get_list_url_name, *args, **kwargs)

    def reverse_change_url(self, *args, **kwargs):
        # 根据别名反向生成url
        return self.reverse_commons_url(self.get_change_url_name, *args, **kwargs)

    def reverse_delete_url(self, *args, **kwargs):
        # 根据别名反向生成url
        return self.reverse_commons_url(self.get_delete_url_name, *args, **kwargs)

    def wrapper(self, func):
        @functools.wraps(func)
        def inner(request, *args, **kwargs):
            self.request = request

            return func(request, *args, **kwargs)

        return inner

    def get_urls(self):
        """
        app_label: 得到的是app名称 self.model_class._meta.app_label
        model_name: 得到的是表的名称,小写 self.model_class._meta.model_name
        :return:
        """
        # app_label, model_name, prev = self.model_class._meta.app_label, self.model_class._meta.model_name, self.prev
        patterns = [
            re_path(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            re_path(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view),
                    name=self.get_change_url_name),
            re_path(r'^delete/(?P<pk>\d+)/$', self.wrapper(self.delete_view),
                    name=self.get_delete_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def extra_urls(self):
        return []


class StarkSite(object):
    def __init__(self):
        self._registry = []
        self.app_name = 'stark'
        self.namespace = 'stark'

    def register(self, model_class, handler_class=None, prev=None):
        """
        model_class:是models中相关的类
        :param handler_class:处理请求的视图函数所在的类
        :param prev:url的前缀
        :return:
        """
        if not handler_class:
            handler_class = StarkHandler
        self._registry.append(
            {'model_class': model_class, 'handler': handler_class(self, model_class, prev), 'prev': prev})

    def get_urls(self):
        patterns = []
        for item in self._registry:
            model_class = item['model_class']
            prev = item['prev']
            handler = item['handler']
            app_label, model_name = model_class._meta.app_label, model_class._meta.model_name
            if prev:
                patterns.append(
                    re_path(r'^%s/%s/%s/' % (app_label, model_name, prev,), (handler.get_urls(), None, None)), )
            else:
                patterns.append(re_path(r'%s/%s/' % (app_label, model_name,), (handler.get_urls(), None, None)))
        return patterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace


site = StarkSite()
