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
from base.exceptions import ParamsError, CsrfError, AuthenticationTokenExpired
from settings import DEBUG
from .resp import LeanResponse


class BaseAPIView(GenericAPIView):
    """
    customize the APIView for customize exception response
    """

    def check_object_any_permissions(self, request, obj):
        """
        检查是否满足任意某个权限(满足其中一个即可, 模仿check_object_permissions)
        """
        for permission in self.get_permissions():
            if permission.has_object_permission(request, self, obj):
                return
        self.permission_denied(request, message=u'无操作权限')

    def check_objects_any_permissions(self, request, objs):
        """
        检查是否满足任意某个权限(满足其中一个即可, 模仿check_object_permissions)
        """
        for permission in self.get_permissions():
            if not objs:
                if permission.has_object_permission(request, self, None):
                    return
            elif isinstance(objs, (list, tuple)):
                for obj in objs:
                    if permission.has_object_permission(request, self, obj):
                        return
        self.permission_denied(request, message=u'无操作权限')

    def check_objects_all_permissions(self, request, objs):
        """
        检查是否满足所有权限(满足所有方可, 模仿check_object_permissions)
        """
        for permission in self.get_permissions():
            if not objs:
                if not permission.has_object_permission(request, self, None):
                    self.permission_denied(request, message=u'无操作权限')

            elif isinstance(objs, (list, tuple)):
                for obj in objs:
                    if not permission.has_object_permission(request, self, obj):
                        self.permission_denied(request, message=u'无操作权限')

    def get_user_role_dept_domains(self, request, perm_keys, allOrAny="ALL" ):
        """
        获取用户可操作的权限域（部门ID）
        :param request:
        :param perm_keys: 权限唯一标识List（id或codename）
        :param allOrAny: 默认为字符串"ALL",还可以为"ANY"
        :return: 返回权限域标识List集合(Department类实例ID集合）
        """
        roles = request.user.get_roles()
        roles_tmp = []
        dept_ids = []
        if not perm_keys or not roles:
            return dept_ids

        if allOrAny == "ALL":
            for key in perm_keys:
                for role in roles:
                    for perm in role.get_permissions():
                        if key == perm.id:
                            roles_tmp.append(role)
            for r in roles_tmp:
                departments = r.get_user_role_dept_domains(request.user)
                for dept in departments:
                    dept_ids.append(dept.id)
        if allOrAny == "ANY":
            for key in perm_keys:
                for role in roles:
                    for perm in role.get_permissions():
                        if key == perm.id:
                            roles_tmp.append(role)
            for r in roles_tmp:
                departments = r.get_dept_domains()
                for dept in departments:
                    dept_ids.append(dept.id)
        return dept_ids

    def get_object_or_404(self, obj_id, model, use_cache=True):
        """
        :param obj_id: 对象id
        :param model:  对象对应的类类型
        :param use_cache: 是否优先从缓存中获取数据, 默认优先从缓存中取
        :return:distinct_fields
        """
        if use_cache:
            obj = model.objects.get_cached(obj_id)
        else:
            obj = model.objects.get_by_id(obj_id)
        if obj:
            return obj
        # raise NotFound('Object Not Found:%s %s' % (type(model), obj_id))
        raise NotFound('Object Not Found:%s %s' % (str(model).split('.').pop(-1).replace("'>", ''), obj_id))

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

    def get_pages(self, obj_list, results_name='data', srl_cls_name=None):
        """
        将serializer数据转换为分页数据
        :param obj_list: 要序列化的数据列表, queryset或data_list
        :param results_name: 数据结果集名称, 默认为'data'
        :param srl_cls_name: 重置序列化Serializer名称
        :return:
        """
        single_page = self.paginate_queryset(obj_list)
        if single_page:
            obj_list = single_page
        response = resp.serialize_response(
            obj_list, srl_cls_name=srl_cls_name, results_name=results_name
        )
        response.data.update(self.get_paginated_stuff())
        return response

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

        elif isinstance(exc, AuthenticationTokenExpired):
            return Response(codes.get('token_expired'), status=exc.status_code, exception=True)

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
            if DEBUG:
                return Response(codes.format('object_not_found', exc.detail), status=status.HTTP_404_NOT_FOUND, exception=True)
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



