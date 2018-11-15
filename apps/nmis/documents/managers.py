# coding=utf-8
#
# Created by gong, on 2018-10-16
#

import logging

from base.models import BaseManager

logger = logging.getLogger(__name__)


class FileManager(BaseManager):

    def create(self):
        pass

    def bulk_create_or_update(self, files):
        """
        批量保存文档
        :param files: {'id: 1, 'name': '', 'path': '', 'cate': ''}
        :return:
        """
        result_list = []
        try:
            for file in files:
                file_obj, created = self.update_or_create(path=file.pop('path'), defaults=file)
                result_list.append(file_obj)
            return result_list
        except Exception as e:
            logger.exception(e)
            return None


