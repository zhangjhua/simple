from django.conf import settings


# 二级菜单
def init_permission(current_user, request):
    """
    用户权限的初始化
    :param current_user:  当前用户对象
    :param request: 请求相关所有数据
    :return:
    """
    # 权限信息初始化
    # 根据当前用户信息获取此用户所拥有的权限放进session中
    permission_queryset = current_user.roles.filter(permissions__isnull=False).values('permissions__id',
                                                                                      'permissions__title',
                                                                                      'permissions__name',
                                                                                      'permissions__menu_id',
                                                                                      'permissions__menu__title',
                                                                                      'permissions__menu__icon',
                                                                                      'permissions__url',
                                                                                      'permissions__pid_id',
                                                                                      'permissions__pid__url',
                                                                                      'permissions__pid__title', ).distinct()

    # 权限列表
    permission_dict = {}
    # 菜单栏
    menu_dict = {}

    for item in permission_queryset:

        permission_dict[item['permissions__name']] = {
            'id': item['permissions__id'],
            'title': item['permissions__title'],
            'url': item['permissions__url'],
            'pid': item['permissions__pid_id'],
            'p_title': item['permissions__pid__title'],
            'p_url': item['permissions__pid__url']
        }

        menu_id = item['permissions__menu_id']
        if not menu_id:
            continue
        node = {'id': item['permissions__id'], 'title': item['permissions__title'], 'url': item['permissions__url']}
        if menu_id in menu_dict:
            menu_dict[menu_id]['children'].append(node)
        else:
            menu_dict[menu_id] = {
                'title': item['permissions__menu__title'],
                'icon': item['permissions__menu__icon'],
                'children': [node, ]
            }

    # 获取权限中所有的URL
    # 权限放进session中
    """
    PERMISSION_SESSION_KEY,MENU_SESSION_KEY
    在setting里面配置
    """
    request.session[settings.PERMISSION_SESSION_KEY] = permission_dict
    request.session[settings.MENU_SESSION_KEY] = menu_dict


"""
一级菜单
def init_permission(user, request):

    # 用户权限初始化


    # 根据角色获取所有权限
    permission_list = user.roles.filter(permissions__id__isnull=False).values('permissions__id',
                                                                              'permissions__title',
                                                                              'permissions__url',
                                                                              'permissions__is_menu',
                                                                              'permissions__icon'
                                                                              ).distinct()
    menu_list = []
    permission_url_list = []
    for item in permission_list:
        if item['permissions__is_menu']:
            tmp = {
                'title': item['permissions__title'],
                'icon': item['permissions__icon'],
                'url': item['permissions__url']
            }
            menu_list.append(tmp)

        permission_url_list.append(item['permissions__url'])

    # 将权限信息和菜单信息 放入session
    request.session[settings.MENU_SESSION_KEY] = menu_list
    request.session[settings.PERMISSION_SESSION_KEY] = permission_url_list
"""