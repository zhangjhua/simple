from django.db import models


# Create your models here.

class Menu(models.Model):
    title = models.CharField(verbose_name='一级菜单的名称', max_length=32)
    icon = models.CharField(verbose_name='图标', max_length=32)

    def __str__(self):
        return self.title


class Permission(models.Model):
    """
    权限表
    """
    title = models.CharField(verbose_name='标题', max_length=32)
    url = models.CharField(verbose_name='含正则的url', max_length=128)
    menu = models.ForeignKey(verbose_name='所属菜单', to='Menu', null=True, blank=True,
                             help_text='null表示不是菜单,非null才表示是二级菜单', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='URL别名', max_length=32, unique=True)
    pid = models.ForeignKey(to='Permission', null=True, blank=True, related_name='parents', verbose_name='关联的权限',
                            help_text='对于非菜单权限需要选择一个可以成为菜单的权限,用户做默认展开和选中菜单.', on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class Role(models.Model):
    title = models.CharField(verbose_name='角色名称', max_length=32)
    # 创建第三张表 角色和权限
    permissions = models.ManyToManyField(verbose_name='拥有的权限', to='Permission', blank=True)

    def __str__(self):
        return self.title


class UserInfo(models.Model):
    name = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=64)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    # 用户和角色的关系表
    roles = models.ManyToManyField(verbose_name='拥有的角色', to=Role, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        # django以后再做数据库迁移时，不再为UserInfo类创建相关的表以及表结构了。
        # 此类可以当做"父类"，被其他Model类继承。
        abstract = True



"""
current_user = models.UserInfo.objects.filter(name=user,password=pwd).first()
# 获取当前用户所拥有的权限 select id,name,XXfrom db
permission_list = current_list.roles.filter(permissions__isnull=False).values(permissions__id,permissions__url).distinct()
# 有BUG
问题1:
    一个用户拥有多个角色
    一个角色拥有多个权限
    需要去重
    
问题2:
    角色和权限关系:
    用户表
    用户和角色关系表
    



"""
