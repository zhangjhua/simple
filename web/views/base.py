class PermissionHandler(object):
    def get_add_btn(self, request, *args, **kwargs):
        from django.conf import settings
        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        name = '%s:%s' %(self.site.namespace, self.get_add_url_name)
        if name in permission_dict:
            return super().get_add_btn(request, *args, **kwargs)
        return None

    def get_list_display(self, request, *args, **kwargs):
        from django.conf import settings
        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        value = []
        change_name = "%s:%s" % (self.site.namespace, self.get_change_url_name)
        del_name = "%s:%s" % (self.site.namespace, self.get_delete_url_name)
        if self.list_display:
            value.extend(self.list_display)
            if change_name in permission_dict and del_name in permission_dict:

                value.append(type(self).display_del)
                value.append(type(self).display_edit)
                return value
            if change_name in permission_dict:
                value.append(type(self).display_edit)
                return value
            if del_name in permission_dict:
                value.append(type(self).display_del)
                return value
        return value