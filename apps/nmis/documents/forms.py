# coding=utf-8
#
# Created by gong, on 2018-10-16
#

"""

"""

import logging

from nmis.hospitals.consts import ARCHIVE
from nmis.projects.consts import DOCUMENT_DIR
from base.forms import BaseForm
from utils.files import upload_file

logs = logging.getLogger(__name__)


class UploadFileForm(BaseForm):

    def __init__(self, req, *args, **kwargs):
        BaseForm.__init__(self, req, *args, **kwargs)
        self.req = req
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'file_type_err': '不支持的文件类型',
            'file_err': '文件不存在',
            'file_name_err': '文件名称错误',
            'file_size_err': '上传文件过大，默认上传大小2.5M'
        })

    def is_valid(self):
        if not self.check_file_type() or not self.check_file_size() or not self.check_file_key():
            return False
        return True

    def check_file_type(self):
        for tag in self.req.FILES.keys():
            files = self.req.FILES.getlist(tag)
            for file in files:
                if file.content_type not in ARCHIVE.values():
                    self.update_errors('%s' % file.name, 'file_type_err')
                    return False
        return True

    def check_file_name(self):
        pass

    def check_file_key(self):
        if not self.req.FILES.keys():
            self.update_errors('file', 'file_err')
            return False
        return True

    def check_file_size(self):
        """
        校验文件大小，以字节校验，默认2621440字节（2.5M）
        :return:
        """
        for tag in self.req.FILES.keys():
            file = self.req.FILES.get(tag)
            if file.size > 2621440:
                self.update_errors('file_size', 'file_size_err')
                return False
        return True

    def save(self):
        upload_success_files = []
        for tag in self.req.FILES.keys():
            files = self.req.FILES.getlist(tag)
            for file in files:
                result = upload_file(file, DOCUMENT_DIR, file.name)
                if result:
                    upload_success_files.append(result)
                else:
                    return '%s%s' % (file.name, '上传失败'), False
        return upload_success_files, True
