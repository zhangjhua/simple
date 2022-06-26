# 角色管理

from rbac import models
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from rbac.forms.role import RoleModelForm


def role_list(request):
    role_queryset = models.Role.objects.all()

    return render(request, 'rbac/role_list.html', {'roles': role_queryset})


def role_add(request):
    origin_url = reverse('rbac:role_list')
    if request.method == 'GET':
        form = RoleModelForm()
        return render(request, 'rbac/change.html', {'form':form})
    form = RoleModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:role_list'))
    return render(request, 'rbac/change.html', {'form': form,'cancel':origin_url})

def role_edit(request,pk):
    # 取到id的信息数据
    obj = models.Role.objects.filter(id=pk).first()
    origin_url = reverse('rbac:role_list')
    if not obj:
        return HttpResponse('角色不存在')
    if request.method == 'GET':
        form = RoleModelForm(instance=obj)
        return render(request, 'rbac/change.html', {'form': form})
    form = RoleModelForm(data=request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:role_list'))
    return render(request, 'rbac/change.html', {'form': form,'cancel':origin_url})


def role_del(request,pk):
    obj2 = models.Role.objects.get(id=pk)
    if request.method == "GET":
        return render(request, 'rbac/role_del.html', {'obj2': obj2})
    obj2.delete()
    return redirect(reverse('rbac:role_list'))