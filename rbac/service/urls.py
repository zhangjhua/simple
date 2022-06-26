from django.urls import reverse
from django.http import QueryDict



def memory_url(request, name, *args, **kwargs):
    """
    生成带有原搜索条件的URL
    :param request:
    :param name:
    :return:
    """
    basic_url = reverse(name,args=args,kwargs=kwargs)
    # 当前URL无参数
    if not request.GET:
        return basic_url
    # 拿到了原搜索条件

    query_dict = QueryDict(mutable=True)
    # 相当于_filter = "mid=2"(客户端传过来后面的参数 )
    query_dict['_filter'] = request.GET.urlencode()
    return '%s?%s' % (basic_url, query_dict.urlencode())



def memory_reverse(request,name,*args,**kwargs):
    """
    反向生成URL
    在URL中 把原来的搜索条件获取
    在url中将原来搜索条件 如filter = mid=1
    :param request:
    :param name:
    :param args:
    :param kwargs:
    :return:
    """
    url = reverse(name,args=args,kwargs=kwargs)
    origin_params = request.GET.get('_filter')
    if origin_params:
        url = '%s?%s' % (url, origin_params,)
    return url