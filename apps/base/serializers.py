# coding=utf-8
#
# Created on 2013-8-6, by Junn
#
#
from collections import OrderedDict
from django.core.paginator import InvalidPage, EmptyPage, PageNotAnInteger
from django.utils import six
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound


class BaseModelSerializer(serializers.ModelSerializer):

    created_time = serializers.SerializerMethodField('str_created_time')

    def str_created_time(self, obj):
        return obj.created_time.strftime('%Y-%m-%d %H:%M:%S')

    def str_time_obj(self, time_obj):
        """
        格式化时间字符串
        :param time_obj: 若time_obj为time对象, 则转化为固定格式的字符串返回; 若为字符串则直接返回
        """
        if isinstance(time_obj, str):
            return time_obj
        return time_obj.strftime('%Y-%m-%d %H:%M:%S') if time_obj else ''


class PlugPageNumberPagination(PageNumberPagination):
    """
    定制DRF框架默认的PageNumberPagination, 使分页返回结果添加需要的字段.

    若子类化该类, 则需要在APIView中定义如下类范围常量:
        pagination_class = CustomizedPlugPageNumberPagination

    """

    # 分页查询参数名
    page_query_param = 'page'                       # 请求第几页
    page_size_query_param = 'size'                  # 每页多少条数据

    # 返回结果参数名
    paging_result_param = 'paging'                  # 分页数据块标识

    page_size_result_param = 'page_size'            # 每页数据量
    current_page_result_param = 'current_page'      # 当前第几页
    total_count_result_param = 'total_count'        # 数据总数量

    projects_status_counts = 'status'  # 项目数量块标示
    project_sd = 'SD'  # 进行中项目数量
    project_pe = 'PE'  # 待启动项目数量
    project_do = 'DO'  # 已完成的项目数量

    # 重写PageNumberPagination方法
    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            self.page = paginator.page(1)
        except EmptyPage:
            self.page = paginator.page(paginator.num_pages)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_stuff(self):
        """
        返回分页数据结构, 该结构将添加到最终的json响应结果里.
        :return: 返回数据形如:
                "paging": {
                    "current_page": 1,
                    "page_size": 2,
                    "total_count": 2
                }
        """

        return {
            self.paging_result_param: OrderedDict([
                (self.current_page_result_param, self.page.number),
                (self.page_size_result_param,    len(self.page)),       # 每页的数量
                (self.total_count_result_param,  self.page.paginator.count),  # queryset结果总数
            ])}

    def get_status_count(self, **data):
        """
        返回项目各状态条数数据结构，该结构添加到最终的json响应结果里
        :return: 返回数据形如:
                "status_counts":{
                    "SD": 2
                    "DO": 10
                    "PE": 12
                }
        """
        return {
            self.projects_status_counts: OrderedDict([
                (self.project_do, data.get('DO')),
                (self.project_pe, data.get('PE')),
                (self.project_sd, data.get('SD'))
            ])
        }
