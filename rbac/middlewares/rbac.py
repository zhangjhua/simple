from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse
import re
from django.conf import settings


class RbacMiddleware(MiddlewareMixin):
    """
    用户权限信息校验
    """

    def process_request(self, request):
        """
        当用户请求刚进入时候触发执行
        :param request:
        :return:
        """
        """
        1.获取当前用户的url
        2.获取当前用户在session中保存的权限列表
        3.权限信息匹配
        http://127.0.0.1:8000/customer/list/  ->/customer/list/
        """
        # 白名单
        # valid_url_list = [
        #     '/login/',
        #     '/admin/.*'
        # ]

        current_url = request.path_info
        for valid_url in settings.VALID_URL_LIST:
            if re.match(valid_url, current_url):
                return None
        # 权限列表
        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)


        if not permission_dict:
            return HttpResponse('未获取到用户权限信息,请登录!')



        url_record = [
            {
                'title': '首页',
                'url': '#'
            }
        ]
        # 此处代码进行判断
        for url in settings.NO_PERMISSION_LIST:
            if re.match(url, request.path_info):
                # 需要登录，但无需权限校验
                request.current_select_permission = 0
                request.breadcrumb = url_record

                return None

        flag = False

        for item in permission_dict.values():
            abc = item['url']
            reg = '^%s$' % abc

            if re.match(reg, current_url):
                flag = True
                request.current_select_permission = item['pid'] or item['id']
                if not item['pid']:
                    url_record.extend([{'title': item['title'], 'url': item['url'], 'class':'active'}])
                else:
                    url_record.extend([
                        {'title': item['p_title'], 'url': item['p_url']},
                        {'title': item['title'], 'url': item['url'], 'class':'active'},
                    ])
                request.breadcrumb = url_record

                break

        if not flag:
            return HttpResponse('无权访问')

