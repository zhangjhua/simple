
from web.models import UserInfo
from rbac import models

from django.shortcuts import render, redirect, HttpResponse
from rbac.forms.menu import MenuModelForm, SecondMenuModelForm, PermissionModelForm
from rbac.forms.menu import MultiEditPermissionForm, MultiAddPermissionForm
from django.urls import reverse
from rbac.service.urls import memory_reverse
from rbac.service.routes import get_all_url_dict
from collections import OrderedDict
from django.forms import formset_factory
from django.utils.module_loading import import_string
from django.conf import settings


def menu_list(request):
    """
    菜单的权限列表
    :param request:
    :return:
    """
    menus = models.Menu.objects.all()
    # 用户选择的一级菜单
    menu_id = request.GET.get('mid')
    # 用户选择的二级菜单
    second_menu_id = request.GET.get('sid')
    # 用户选择的三级菜单
    thirst_menu_id = request.GET.get('tid')
    menu_exists = models.Menu.objects.filter(id=menu_id).exists()
    second_menu_exists = models.Permission.objects.filter(pid_id=second_menu_id).exists()
    # if not menu_exists:
    #     menu_id = None
    if menu_id:
        second_menus = models.Permission.objects.filter(menu_id=menu_id)
    else:
        second_menus = []
    # if not second_menu_exists:
    #     second_menu_id = None
    if second_menu_id:
        thirst_menus = models.Permission.objects.filter(pid_id=second_menu_id)
    else:
        thirst_menus = []
    return render(request, 'rbac/menu_list.html',
                  {
                      "menus": menus,
                      "menu_id": menu_id,
                      'second_menus': second_menus,
                      'second_menu_id': second_menu_id,
                      'thirst_menus': thirst_menus,
                      'thirst_menu_id': thirst_menu_id,
                  })


def menu_add(request):
    if request.method == 'GET':
        form = MenuModelForm()
        return render(request, 'rbac/change.html', {'form': form})

    form = MenuModelForm(data=request.POST)
    if form.is_valid():
        form.save()

        return redirect(memory_reverse(request, 'rbac:menu_list'))
    return render(request, 'rbac/change.html', {'form': form})


def menu_edit(request, pk):
    obj = models.Menu.objects.get(id=pk)
    if not obj:
        return HttpResponse('菜单不存在')
    if request.method == 'GET':
        form = MenuModelForm(instance=obj)
        return render(request, 'rbac/change.html', {'form': form})
    form = MenuModelForm(data=request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect(memory_reverse(request, 'rbac:menu_list'))
    return render(request, 'rbac/change.html', {'form': form})


def menu_del(request, pk):
    # obj2 = models.Menu.objects.get(id=pk)
    # if request.method == "GET":
    #     return render(request, 'rbac/delete.html', {'obj2': obj2})
    # obj2.delete()
    # return redirect(memory_reverse(request,'rbac:menu_list'))
    url = memory_reverse(request, 'rbac:menu_list')
    if request.method == 'GET':
        return render(request, 'rbac/delete.html', {'cancel': url})

    models.Menu.objects.filter(id=pk).delete()
    return redirect(url)


def second_menu_add(request, menu_id):
    """
    添加二级菜单
    :param request:
    :return:
    """
    menu_object = models.Menu.objects.get(id=menu_id)
    if request.method == 'GET':
        form = SecondMenuModelForm(initial={'menu': menu_object})
        return render(request, 'rbac/change.html', {'form': form})

    form = SecondMenuModelForm(data=request.POST)
    if form.is_valid():
        form.save()

        return redirect(memory_reverse(request, 'rbac:menu_list'))
    return render(request, 'rbac/change.html', {'form': form})


def second_menu_edit(request, pk):
    """
    添加二级菜单
    :param request:
    :return:
    """
    permission_object = models.Permission.objects.get(id=pk)
    if request.method == 'GET':
        form = SecondMenuModelForm(instance=permission_object)
        return render(request, 'rbac/change.html', {'form': form})

    form = SecondMenuModelForm(data=request.POST, instance=permission_object)
    if form.is_valid():
        form.save()

        return redirect(memory_reverse(request, 'rbac:menu_list'))
    return render(request, 'rbac/change.html', {'form': form})


def second_menu_del(request, pk):
    url = memory_reverse(request, 'rbac:menu_list')
    if request.method == 'GET':
        return render(request, 'rbac/delete.html', {'cancel': url})

    models.Permission.objects.filter(id=pk).delete()
    return redirect(url)


def thirst_menu_add(request, second_menu_id):
    """
    添加二级菜单
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = PermissionModelForm()
        return render(request, 'rbac/change.html', {'form': form})

    form = PermissionModelForm(data=request.POST)
    if form.is_valid():
        second_menu_obj = models.Permission.objects.filter(id=second_menu_id).first()
        if not second_menu_obj:
            return HttpResponse('二级菜单不存在,请重新选择')
        # form.instance中包含用户提交的所有的值
        # 相当于做了下面的事情
        # instance = models.Permission(title='',name='',url='',)
        # instance.pid = second_menu_obj
        # instance.save
        form.instance.pid = second_menu_obj
        form.save()
        return redirect(memory_reverse(request, 'rbac:menu_list'))
    return render(request, 'rbac/change.html', {'form': form})


def thirst_menu_edit(request, pk):
    """
    编辑三级菜单
    :param request:
    :return:
    """
    permission_object = models.Permission.objects.get(id=pk)
    if request.method == 'GET':
        form = PermissionModelForm(instance=permission_object)
        return render(request, 'rbac/change.html', {'form': form})

    form = PermissionModelForm(data=request.POST, instance=permission_object)
    if form.is_valid():
        form.save()

        return redirect(memory_reverse(request, 'rbac:menu_list'))
    return render(request, 'rbac/change.html', {'form': form})


def thirst_menu_del(request, pk):
    url = memory_reverse(request, 'rbac:menu_list')
    if request.method == 'GET':
        return render(request, 'rbac/delete.html', {'cancel': url})

    models.Permission.objects.filter(id=pk).delete()
    return redirect(url)


def multi_permissions(request):
    """
    批量操作权限
    :param request:
    :return:
    """
    post_type = request.GET.get('type')
    generate_formset_add_class = formset_factory(MultiAddPermissionForm, extra=0)
    update_formset_class = formset_factory(MultiEditPermissionForm, extra=0)
    generate_formset = None
    update_formset = None
    # 批量添加
    if request.method == 'POST' and post_type == 'generate':

        formset = generate_formset_add_class(data=request.POST)
        if formset.is_valid():
            object_list = []
            post_row_list = formset.cleaned_data
            has_error = False

            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]

                try:
                    new_object = models.Permission(**row_dict)
                    # 判断唯一索引
                    new_object.validate_unique()
                    object_list.append(new_object)
                except Exception as e:
                    # 把错误信息添加到formset里面
                    formset.errors[i].update(e)
                    generate_formset = formset
                    has_error = True

            # 要先判断是否有错误信息
            # 批量添加
            if not has_error:
                models.Permission.objects.bulk_create(object_list, batch_size=100)
        else:
            generate_formset = formset

    # 批量更新
    if request.method == 'POST' and post_type == 'update':

        formset = update_formset_class(data=request.POST)
        if formset.is_valid():
            post_row_list = formset.cleaned_data

            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]
                permission_id = row_dict.pop("id")
                # print(row_dict)
                try:
                    row_object = models.Permission.objects.filter(id=permission_id).first()
                    for k, v in row_dict.items():
                        setattr(row_object, k, v)
                    row_object.validate_unique()
                    row_object.save()
                except Exception as e:
                    # 把错误信息添加到formset里面
                    formset.errors[i].update(e)
                    update_formset = formset

        else:
            update_formset = formset

    # 获取项目中所有的URL
    all_url_dict = get_all_url_dict()
    # 集合 项目中所有name集合
    router_name_set = set(all_url_dict.keys())

    # 获取数据库中所有的URL
    permissions = models.Permission.objects.all().values('id', 'title', 'name', 'url', 'menu_id', 'pid_id')
    permission_dict = OrderedDict()
    # 集合
    permission_name_set = set()
    for row in permissions:
        permission_dict[row['name']] = row
        permission_name_set.add(row['name'])

    for name, value in permission_dict.items():
        router_row_dict = all_url_dict.get(name)
        if not router_row_dict:
            continue
        if value['url'] != router_row_dict['url']:
            value['url'] = '路由和数据库不一致'

    # 应该添加,删除,修改的权限有哪些?
    # 计算出应该增加的name
    if not generate_formset:
        generate_name_list = router_name_set - permission_name_set
        generate_formset = generate_formset_add_class(
            initial=[row_dict for name, row_dict in all_url_dict.items() if name in generate_name_list])
    # 计算出应该删除的name
    delete_name_list = permission_name_set - router_name_set
    delete_row_list = [row_dict1 for name, row_dict1 in permission_dict.items() if name in delete_name_list]

    # 计算出应该更新的name
    # 操作要有隐形的ID 要不然无法正确更新
    if not update_formset:
        update_name_list = router_name_set & permission_name_set
        update_formset = update_formset_class(
            initial=[row_dict for name, row_dict in permission_dict.items() if name in update_name_list])

    return render(
        request,
        'rbac/multi_permissions.html',
        {
            'generate_formset': generate_formset,
            'delete_row_list': delete_row_list,
            'update_formset': update_formset,
        }
    )


def multi_permissions_del(request, pk):
    url = memory_reverse(request, 'rbac:multi_permissions')
    if request.method == 'GET':
        return render(request, 'rbac/delete.html', {'cancel': url})

    models.Permission.objects.filter(id=pk).delete()
    return redirect(url)


def distribute_permissions(request):
    # 业务中的用户表 "app01.models.UserInfo""

    user_id = request.GET.get('uid')
    user_object = UserInfo.objects.filter(id=user_id).first()
    if not user_object:
        user_id = None

    role_id = request.GET.get('rid')
    role_object = models.Role.objects.filter(id=role_id).first()
    if not role_object:
        role_id = None
    if request.method == 'POST' and request.POST.get('type') == 'role':
        roles_id_list = request.POST.getlist('roles')
        # print(":::::::::", roles_id_list)
        # 把用户和角色关系添加到第三张表(关系表)
        if not user_object:
            return HttpResponse('请选择用户')
        else:
            user_object.roles.set(roles_id_list)

    if request.method == 'POST' and request.POST.get('type') == 'permission':
        permission_id_list = request.POST.getlist('permissions')

        if not role_object:
            return HttpResponse('请选择角色')
        role_object.permissions.set(permission_id_list)

    if user_id:
        user_has_roles = user_object.roles.all()
    else:
        user_has_roles = []

    user_has_roles_dict = {item.id: None for item in user_has_roles}

    if role_object:
        user_has_permissions = role_object.permissions.all()
        user_has_permissions_list = [item.id for item in user_has_permissions]
    # 如果选中角色,优先显示角色所拥有的权限,没有选角色才显示用户拥有的所有的权限
    elif user_object:
        user_has_permissions = user_object.roles.filter(permissions__id__isnull=False).values('id',
                                                                                              'permissions').distinct()
        user_has_permissions_list = [item['permissions'] for item in user_has_permissions]
    else:
        user_has_permissions_list = []

    all_user_list = UserInfo.objects.all()

    all_role_list = models.Role.objects.all()
    menu_permission_list = []
    # 所有的一级菜单
    all_menu_list = models.Menu.objects.values('id', 'title')
    """
    [
        {id:1,title:菜单1,children:[{id:1,title:x1, menu_id:1,'children':[{id:11,title:x2,pid:1},] },{id:2,title:x1, menu_id:1 },]},
        {id:2,title:菜单2,children:[{id:3,title:x1, menu_id:2 },{id:5,title:x1, menu_id:2 },]},
        {id:3,title:菜单3,children:[{id:4,title:x1, menu_id:3 },]},
    ]
    """
    all_menu_dict = {}
    """
           {
               1:{id:1,title:菜单1,children:[{id:1,title:x1, menu_id:1,children:[{id:11,title:x2,pid:1},] },{id:2,title:x1, menu_id:1,children:[] },]},
               2:{id:2,title:菜单2,children:[{id:3,title:x1, menu_id:2,children:[] },{id:5,title:x1, menu_id:2,children:[] },]},
               3:{id:3,title:菜单3,children:[{id:4,title:x1, menu_id:3,children:[] },]},
           }
           """
    for item in all_menu_list:
        item['children'] = []
        all_menu_dict[item['id']] = item
        """all_menu_dict={
            1:{'id':1,'title':XX}
        }
        """

    # 所有的二级菜单
    all_second_menu_list = models.Permission.objects.filter(menu__isnull=False).values('id', 'title', 'menu_id')
    """
        [
            {id:1,title:x1, menu_id:1,children:[{id:11,title:x2,pid:1},] },   
            {id:2,title:x1, menu_id:1,children:[] },
            {id:3,title:x1, menu_id:2,children:[] },
            {id:4,title:x1, menu_id:3,children:[] },
            {id:5,title:x1, menu_id:2,children:[] },
        ]
    """
    all_second_menu_dict = {}
    for row in all_second_menu_list:
        row['children'] = []
        all_second_menu_dict[row['id']] = row
        # 数据库有foreignkey约束   如果没有约束 需要 if menu_id: 做判断
        menu_id = row['menu_id']
        all_menu_dict[menu_id]['children'].append(row)
        # 所有的三级菜单
    all_thirst_menu_list = models.Permission.objects.filter(menu__isnull=True).values('id', 'title', 'pid_id')
    for row in all_thirst_menu_list:
        pid = row['pid_id']
        if not pid:
            continue
        all_second_menu_dict[pid]['children'].append(row)
    # 构造出来的数据格式
    """
     print(all_menu_list)
            [
                {
                    'id': 1,
                    'title': '信息管理',
                    'children': [
                        {
                            'id': 1,
                            'title': '客户列表',
                            'menu_id': 1,
                            'children': [
                                {
                                    'id': 2,
                                    'title': '添加客户',
                                    'pid_id': 1
                                },
                                {
                                    'id': 3,
                                    'title': '删除客户',
                                    'pid_id': 1
                                },
                                {
                                    'id': 4,
                                    'title': '修改客户',
                                    'pid_id': 1
                                },
                                {
                                    'id': 5,
                                    'title': '批量导入',
                                    'pid_id': 1
                                },
                                {
                                    'id': 6,
                                    'title': '下载模板',
                                    'pid_id': 1
                                },
                                {
                                    'id': 16,
                                    'title': '销售',
                                    'pid_id': 1
                                }
                            ]
                        },
                        {
                            'id': 7,
                            'title': '账单列表',
                            'menu_id': 1,
                            'children': [
                                {
                                    'id': 8,
                                    'title': '添加账单',
                                    'pid_id': 7
                                },
                                {
                                    'id': 9,
                                    'title': '删除账单',
                                    'pid_id': 7
                                },
                                {
                                    'id': 10,
                                    'title': '修改账单',
                                    'pid_id': 7
                                }
                            ]
                        }
                    ]
                },
                {
                    'id': 2,
                    'title': '用户管理',
                    'children': [
                        {
                            'id': 17,
                            'title': 'CEO',
                            'menu_id': 2,
                            'children': [
                                
                            ]
                        },
                        {
                            'id': 19,
                            'title': '角色列表',
                            'menu_id': 2,
                            'children': [
                                {
                                    'id': 20,
                                    'title': '添加角色',
                                    'pid_id': 19
                                },
                                {
                                    'id': 21,
                                    'title': '删除角色',
                                    'pid_id': 19
                                },
                                {
                                    'id': 22,
                                    'title': '编辑角色',
                                    'pid_id': 19
                                },
                                {
                                    'id': 27,
                                    'title': '重置密码',
                                    'pid_id': 19
                                }
                            ]
                        },
                        {
                            'id': 23,
                            'title': '用户列表',
                            'menu_id': 2,
                            'children': [
                                {
                                    'id': 24,
                                    'title': '添加用户',
                                    'pid_id': 23
                                },
                                {
                                    'id': 25,
                                    'title': '删除用户',
                                    'pid_id': 23
                                },
                                {
                                    'id': 26,
                                    'title': '编辑用户',
                                    'pid_id': 23
                                }
                            ]
                        }
                    ]
                },
                {
                    'id': 3,
                    'title': '销售列表',
                    'children': [
                        {
                            'id': 12,
                            'title': 'check_list',
                            'menu_id': 3,
                            'children': [
                                
                            ]
                        }
                    ]
                },
                {
                    'id': 6,
                    'title': '权限管理',
                    'children': [
                        {
                            'id': 28,
                            'title': '菜单列表',
                            'menu_id': 6,
                            'children': [
                                {
                                    'id': 29,
                                    'title': '添加菜单',
                                    'pid_id': 28
                                },
                                {
                                    'id': 30,
                                    'title': '编辑菜单',
                                    'pid_id': 28
                                },
                                {
                                    'id': 31,
                                    'title': '删除菜单',
                                    'pid_id': 28
                                },
                                {
                                    'id': 32,
                                    'title': '添加二级菜单',
                                    'pid_id': 28
                                },
                                {
                                    'id': 33,
                                    'title': '编辑二级菜单',
                                    'pid_id': 28
                                },
                                {
                                    'id': 34,
                                    'title': '删除二级菜单',
                                    'pid_id': 28
                                },
                                {
                                    'id': 35,
                                    'title': '添加三级菜单',
                                    'pid_id': 28
                                },
                                {
                                    'id': 36,
                                    'title': '编辑三级菜单',
                                    'pid_id': 28
                                },
                                {
                                    'id': 37,
                                    'title': '删除三级菜单',
                                    'pid_id': 28
                                }
                            ]
                        }
                    ]
                }
            ]    
    """

    # print(all_menu_list)
    # print(user_has_permissions_list)
    return render(
        request,
        'rbac/distribute_permissions.html',
        {
            'all_user_list': all_user_list,
            'all_role_list': all_role_list,
            "all_menu_list": all_menu_list,
            'user_id': user_id,
            'user_has_roles_dict': user_has_roles_dict,
            'user_has_permissions_list': user_has_permissions_list,
            'role_id': role_id,
        }
    )
