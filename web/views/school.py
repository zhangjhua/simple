from stark.service.v1 import StarkHandler
from web.views.base import PermissionHandler


class SchoolHandler(PermissionHandler, StarkHandler):
    list_display = ['title', ]
