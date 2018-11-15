# coding=utf-8
#
# Created by junn, on 17/2/15
#

# 

import logging

from rest_framework.exceptions import NotFound

logger = logging.getLogger(__name__)


def check_objects_exist(request, pkkey_cls_dict):
    """
    通过对象id检查对象是否存在, 且对象都存在时, 则返回对象数据

    :param pkkey_cls_dict: 字典类型
    Sample:
        objects = check_objects_exist(req, {
            'organ_id': Organ, 'candidate_id': Candidate
        })
    """
    results = {}
    for pk, model in pkkey_cls_dict.items():
        pk_value = request.data.get(pk) or request.GET.get(pk)
        obj = model.objects.get_cached(pk_value)
        if not obj:
            logger.debug('%s object not found: %s' % (model.__name__, pk_value))
            raise NotFound
        results.update({pk: obj})

    return results


def check_object_exist(obj_id, model):
    """
    检查对象是否存在
    :param obj_id: 要检查的对象id
    :param model:  对象对应的类类型
    :return:
    """
    obj = model.objects.get_cached(obj_id)
    if not obj:
        logger.debug('%s object not found: %s' % (model.__name__, obj_id))
        raise NotFound
    return obj
