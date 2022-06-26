# 用户管理
from rbac import models
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from rbac.forms.role import UserModelForm,UpdateUserModelForm,ResetPasswordUserModelForm


def user_list(request):
    user_queryset = models.UserInfo.objects.all()

    return render(request, 'rbac/user_list.html', {'users': user_queryset})


def user_add(request):
    if request.method == 'GET':
        form = UserModelForm()
        return render(request, 'rbac/change.html', {'form': form})
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:user_list'))
    return render(request, 'rbac/change.html', {'form': form})


def user_edit(request, pk):
    # 取到id的信息数据
    origin_url = reverse('rbac:user_list')
    obj = models.UserInfo.objects.get(id=pk)
    if not obj:
        return HttpResponse('用户不存在')
    if request.method == 'GET':
        form = UpdateUserModelForm(instance=obj)
        return render(request, 'rbac/change.html', {'form': form, 'cancel': origin_url})
    form = UpdateUserModelForm(data=request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:user_list'))
    return render(request, 'rbac/change.html', {'form': form, 'cancel': origin_url})


def user_del(request, pk):
    obj2 = models.UserInfo.objects.get(id=pk)
    if request.method == "GET":
        return render(request, 'rbac/user_del.html', {'obj2': obj2})
    obj2.delete()
    return redirect(reverse('rbac:user_list'))


def user_reset_pwd(request, pk):
    # 重置密码
    obj = models.UserInfo.objects.get(id=pk)
    if not obj:
        return HttpResponse('用户不存在')
    if request.method == 'GET':
        form = ResetPasswordUserModelForm()
        return render(request, 'rbac/change.html', {'form': form})
    form = ResetPasswordUserModelForm(data=request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:user_list'))
    return render(request, 'rbac/change.html', {'form': form})