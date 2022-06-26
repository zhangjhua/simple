import re
from django.template import Library
from django.conf import settings
from collections import OrderedDict
from django.urls import reverse
from django.http import QueryDict
from rbac.service import urls

register = Library()


# @register.inclusion_tag('rbac/static_menu.html')
# def static_menu(request):
#     """
#     创建一级菜单
#     :return:
#     """
#     """
#     <div class="static-menu">
#        {% for item in request.session.menu_session_key %}
#
#            <a href="{{ item.url }}" class="active">
#                <span class="icon-warp"><i class="fa {{ item.icon }}"></i></span>
#                {{ item.title }}
#            </a>
#
#        {% endfor %}
#
#     /div>
#     """
#     menu_list = request.session.get(settings.MENU_SESSION_KEY)
#     for item in menu_list:
#         regex = "^%s$" % (item['url'],)
#         if re.match(regex, request.path_info):
#             item['class'] = 'active'
#
#     return {
#         'menu_list': request.session.get(settings.MENU_SESSION_KEY)
#     }


@register.inclusion_tag('rbac/multi_menu.html')
def multi_menu(request):
    """
    创建二级菜单
    :param request:
    :return:
    """
    menu_dict = request.session[settings.MENU_SESSION_KEY]
    # 对字典的key进行排序
    # key_list = sorted(menu_dict)
    #
    # #空的有序字典
    # ordered_dict = OrderedDict()
    # print(request.current_select_permission)
    menu1_dict = {}
    for key in menu_dict:
        val = menu_dict[key]
        val['class'] = 'hide'
        for per in val['children']:
            # print(':::::',request)
            if per['id'] == request.current_select_permission:
                per['class'] = 'active'
                val['class'] = ''
        menu1_dict[key] = val

    return {'menu_dict': menu1_dict}


@register.inclusion_tag('rbac/breadcrumb.html')
def breadcrumb(request):
    return {'recode_list': request.breadcrumb}


@register.filter
def has_permission(request, name):
    """
    最多至于两个参数
    """
    if name in request.session[settings.PERMISSION_SESSION_KEY]:
        return True


@register.simple_tag
def memory_url(request, name, *args, **kwargs):
    """
    生成带有原搜索条件的URL
    :param request:
    :param name:
    :return:
    """
    return urls.memory_url(request, name, *args, **kwargs)