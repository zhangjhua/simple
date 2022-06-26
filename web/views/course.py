from stark.service.v1 import StarkHandler
from web.views.base import PermissionHandler


class CourseHandler(PermissionHandler, StarkHandler):
    list_display = ['name', ]
