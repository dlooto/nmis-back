# coding=utf-8
#
# Created on Mar 21, 2014, by Junn
# 
#

import logging

from django.db import models
from django.core.cache import cache
from django.db.models import Manager
from django.db.models.query import QuerySet

logs = logging.getLogger('django')


class BaseManager(Manager):

    def __init__(self):
        super(BaseManager, self).__init__()

    def cache_all(self):
        pass

    def get_by_id(self, obj_id):
        """
        从数据库获取对象数据
        注: 不做对象缓存

        :param obj_id: 对象id, 一般为int型
        :return:
        """
        if not obj_id:
            return None

        try:
            return self.get(id=int(obj_id))
        except self.model.DoesNotExist:
            return None
        except Exception as e:
            logs.warn(e)
            return None

    def get_cached(self, obj_id):
        """
        通过对象id, 获取单个的缓存数据对象. 若缓存中没有该数据, 则从数据库获取对象并进行缓存.
        """
        obj = self.get_cached_only(obj_id)
        if not obj:
            try:
                obj = self.get(id=int(obj_id))
                obj.cache()
            except self.model.DoesNotExist:
                logs.error('Object not found: %s %s' % (self.model.__name__, obj_id))
                return None
            except Exception as e:
                logs.exception('get_cached object error: \n %s' % e)
                return None

        return obj

    def get_cached_only(self, obj_id):
        """
        通过对象id获取单个的缓存数据对象(仅从缓存中获取对象)
        """
        return cache.get(self.make_key(obj_id)) if obj_id else None

    def get_cached_many(self, obj_id_list):
        """
        返回缓存中的多个对象列表, 通过id列表
        :param obj_id_list:
        :return:
        """
        if not obj_id_list:
            return None
        obj_list_keys = []
        for obj_id in obj_id_list:
            obj_list_keys.append(self.make_key(obj_id))
        objs = cache.get_many(obj_list_keys)
        if not objs or len(objs) < len(obj_id_list):
            objs = self.filter(id__in=obj_id_list)
            if not objs:
                return None
            for obj in objs:
                obj.cache()
        return objs

    def make_key(self, obj_id):
        """生成cache key """
        # logs.debug('make cache key: %s%s%s' % (self.__module__, self.model.__name__, obj_id))
        return u'%s%s%s' % (self.__module__, self.model.__name__, obj_id)

    def clear_cache(self, objs):
        """
        批量清除缓存或清除单个对象缓存
        :param objs: QuerySet object, object list or single object
        :return:
        """
        if isinstance(objs, QuerySet):
            objs = list(objs)
        if isinstance(objs, list) or isinstance(objs, set):
            keys = list()
            for item in objs:
                keys.append(type(item).objects.make_key(item.id))
            cache.delete_many(keys)
        else:
            cache.delete(type(objs).objects.make_key(objs.id))

    # def get_obj_by_id(self, obj_id, use_cache=True):
    #     """
    #     :param obj_id: 对象id
    #     :param use_cache: 是否优先从缓存中获取数据, 默认优先从缓存中取
    #     :return: obj
    #     """
    #     if use_cache:
    #         obj = self.get_cached(obj_id)
    #     else:
    #         obj = self.get_by_id(obj_id)
    #     if obj:
    #         return obj


class BaseModel(models.Model):
    default_timeout = 30 * 60    # 默认缓存30分钟, timeout=None 则表示永不过期

    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    objects = BaseManager()

    VALID_ATTRS = [
        'created_time'
    ]

    class Meta:
        abstract = True
        ordering = ['-created_time']

    def __unicode__(self):
        return u'%s' % self.id

    def __str__(self):
        return self.__unicode__()

    def update(self, data):
        """
        更新对象并保存
        :param data:  字典类型, key值与model字段(fields)严格一致, value为新值
        """
        for attr in data.keys():

            if attr in self.VALID_ATTRS and data.get(attr) is not None:
                setattr(self, attr, data.get(attr))
        self.save()
        return self

    def cache(self, timeout=None):
        """
        the object cache itself, cached using obj.id
        """
        # cache.set(type(self).objects.make_key(self.id), self, timeout=timeout)
        self.cache_by_key(self.id, timeout=timeout if timeout else self.default_timeout)

    def cache_by_key(self, _key, timeout=None):
        """
        通过指定key缓存对象
        :param _key:
        """
        cache.set(type(self).objects.make_key(_key), self, timeout=timeout if timeout else self.default_timeout)
                
    def clear_cache(self):  # clear from cache
        cache.delete(type(self).objects.make_key(self.id))
