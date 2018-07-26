# coding=utf-8
#
# Created on 2013-8-6, by Junn
#
#
from collections import OrderedDict
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination


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

