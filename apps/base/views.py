# coding=utf-8
#
# Created on 2013-8-13, by Junn
#
#

from django import http
from django.http.response import Http404, HttpResponseServerError
from django.middleware.csrf import get_token
from django.template import RequestContext, loader, TemplateDoesNotExist
from django.views.decorators.csrf import requires_csrf_token
from rest_framework import exceptions, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from base import codes, resp
from base.exceptions import ParamsError, CsrfError
from .resp import LeanResponse


class BaseAPIView(GenericAPIView):
    """
    customize the APIView for customize exception response
    """

    def check_object_any_permissions(self, request, obj):
        """
        检查是否有满足的权限(满足其中一个即可, 模仿check_object_permissions)
        """
        for permission in self.get_permissions():
            if permission.has_object_permission(request, self, obj):
                return
        self.permission_denied(request, message=u'无操作权限')

    def check_object_perm_domains(self, request, obj):
        if obj in request.user.get_perm_domains():
            return
        self.permission_denied(request, message='无操作权限')

    def get_object_or_404(self, obj_id, model, use_cache=True):
        """
        :param obj_id: 对象id
        :param model:  对象对应的类类型
        :param use_cache: 是否优先从缓存中获取数据, 默认优先从缓存中取
        :return:
        """
        if use_cache:
            obj = model.objects.get_cached(obj_id)
        else:
            obj = model.objects.get_by_id(obj_id)
        if obj:
            return obj
        raise NotFound('Object Not Found:%s %s' % (type(model), obj_id))

    def get_objects_or_404(self, pk_key_cls_dict, use_cache=True):
        """
        通过对象id检查对象是否存在, 且对象都存在时, 则返回对象数据

        :param pk_key_cls_dict: 字典类型
        Sample:
            objects = get_objects_or_404({
                'organ_id': Organ, 'candidate_id': Candidate
            })

        :return 返回字典, 如 {'organ_id': <Organ obj>}
        """
        results = {}
        for pk_key, model in pk_key_cls_dict.items():
            pk_value = self.request.data.get(pk_key) or self.request.GET.get(pk_key)
            results.update({pk_key: self.get_object_or_404(pk_value, model, use_cache)})

        return results

    def get_paginated_stuff(self):
        """
        传递paginator的get_paginated_stuff结果
        """
        return self.paginator.get_paginated_stuff()

    def handle_exception(self, exc):
        """
        重写异常处理方法
        Handle any exception that occurs, by returning an appropriate response,
        or re-raising the error.
        """
        if isinstance(exc, exceptions.Throttled):
            # Throttle wait header
            self.headers['X-Throttle-Wait-Seconds'] = '%d' % exc.wait

        if isinstance(exc, (exceptions.NotAuthenticated,
                            exceptions.AuthenticationFailed)):
            # WWW-Authenticate header for 401 responses, else coerce to 403
            auth_header = self.get_authenticate_header(self.request)

            if auth_header:
                self.headers['WWW-Authenticate'] = auth_header
            else:
                exc.status_code = status.HTTP_403_FORBIDDEN

        # ######## return related Response object  ############
        if isinstance(exc, ParamsError):
            return Response(codes.get('params_error'), status=exc.status_code, exception=True)

        if isinstance(exc, exceptions.MethodNotAllowed):
            return Response(codes.get('method_not_allowed'), status=exc.status_code, exception=True)

        elif isinstance(exc, CsrfError):
            return Response(codes.get('csrf_invalid'), status=exc.status_code, exception=True)

        elif isinstance(exc, exceptions.ParseError):
            return Response(codes.get('parse_error'), status=exc.status_code, exception=True)

        elif isinstance(exc, exceptions.AuthenticationFailed):
            return Response(codes.get('authentication_failed'), status=exc.status_code, exception=True)

        elif isinstance(exc, exceptions.NotAuthenticated):
            return Response(codes.get('not_authenticated'), status=exc.status_code, exception=True)

        elif isinstance(exc, exceptions.NotAcceptable):
            return Response(codes.get('not_acceptable'), status=exc.status_code, exception=True)

        elif isinstance(exc, exceptions.UnsupportedMediaType):
            return Response(codes.get('unsupported_media_type'), status=exc.status_code, exception=True)

        elif isinstance(exc, exceptions.Throttled):
            return Response(codes.get('throttled'), status=exc.status_code, exception=True)

        elif isinstance(exc, (Http404, NotFound)):
            return Response(codes.get('object_not_found'), status=status.HTTP_404_NOT_FOUND, exception=True)

        elif isinstance(exc, exceptions.PermissionDenied):
            return Response(codes.get('permission_denied'), status=status.HTTP_403_FORBIDDEN, exception=True)

        if isinstance(exc, (HttpResponseServerError, exceptions.APIException)):
            if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                return Response(codes.get('server_error'), status=exc.status_code, exception=True)

        raise Exception


def csrf_failure(request, reason=''):
    """
    customize the response for csrf_token invalid
    """
    get_token(request)
    return LeanResponse(codes.get('csrf_invalid'), status=403)


@requires_csrf_token
def server_error(request, template_name='500.html'):
    """
    500 error handler.  Customize the default server_error
    """
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return http.HttpResponseServerError('<h1>Server Error (500)</h1>')
    return http.HttpResponseServerError(template.render(RequestContext(request, {'request_path': request.path})))


def get_pages(self, serializer_data, results_name='data'):
    """
    将serializer数据转换为分页数据
    :param self:
    :param serializer_data: 序列化的数据
    :param results_name: 数据结果集名称, 默认为'data'
    :return:
    """
    single_page = self.paginate_queryset(serializer_data)
    if single_page:
        serializer_data = single_page
    response = resp.serialize_response(serializer_data, results_name=results_name)
    response.data.update(self.get_paginated_stuff())
    return response
