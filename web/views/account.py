from django.shortcuts import render, HttpResponse, redirect

from rbac.service.init_permission import init_permission
from web import models
from web.utils.md5 import gen_md5
from django.urls import reverse


def login(request):

    # 用户登陆
    if request.method == 'GET':
        return render(request, 'login.html')
    user = request.POST.get('user')
    pwd = gen_md5(request.POST.get('pwd',''))
    current_user = models.UserInfo.objects.filter(name=user, password=pwd).first()

    if not current_user:
        return render(request, 'login.html', {'msg': '用户名或者密码错误'})
    request.session['user_info'] = {'id': current_user.id,'nickname': current_user.nickname}
    # 调用权限函数
    init_permission(current_user,request)
    return redirect('/index/')


def logout(request):
    request.session.delete()

    return redirect(reverse('login'))


def index(request):
    return render(request,'index.html')
