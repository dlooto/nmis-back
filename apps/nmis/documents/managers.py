# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

import logging

from base.models import BaseManager

logger = logging.getLogger(__name__)


class FileManager(BaseManager):

    def create(self):
        pass

    def bulk_save_or_update(self, files):
        """
        批量保存文档
        :param files: {'id: 1, 'name': '', 'path': '', 'cate': ''}
        :return:
        """

        result_dict = {
            'updated': [],
            'created': [],
            'all': [],
        }
        import os
        for file in files:
            file['uuid_name'] = os.path.basename(file.get('path'))
            file_obj, created = self.update_or_create(file)
            result_dict['all'].append(file_obj)
            if created:
                result_dict['created'].append(file_obj)
            else:
                result_dict['updated'].append(file_obj)

        return result_dict


