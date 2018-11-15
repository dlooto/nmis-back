# coding=utf-8
#
# Created by gong, on 2018-10-16
#

"""

"""

import logging

import settings
from nmis.hospitals.consts import ARCHIVE
from nmis.documents.models import File
from base.forms import BaseForm
from utils.files import upload_file, is_file_exist

logger = logging.getLogger(__name__)


class UploadFileForm(BaseForm):

    def __init__(self, req, doc_base_dir, *args, **kwargs):
        BaseForm.__init__(self, req, *args, **kwargs)
        self.req = req
        self.doc_base_dir = doc_base_dir
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
                result = upload_file(file, self.doc_base_dir)
                if result:
                    upload_success_files.append(result)
                else:
                    return '%s%s' % (file.name, '上传失败'), False
        return upload_success_files, True


class FileBulkCreateOrUpdateForm(BaseForm):

    def __init__(self, req_user, files, cate_dict, *args, **kwargs):
        BaseForm.__init__(self, files, *args, **kwargs)
        self.req_user = req_user
        self.files = files
        self.cate_dict = cate_dict
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'file_cate_err': '文档类为空或数据错误',
            'files_blank': '文件列表为空或数据错误',
            'file_name_error': '文件名称为空或数据错误',
            'file_name_out_of_bounds': '文件名称长度不能超过100个字符',

            'file_path_error': '文件路径为空或数据错误',
            'file_path_out_of_bounds': '文件路径长度不能超过1000个字符',

            'file_not_exists': '文件不存在',
        })

    def is_valid(self):
        if not self.check_files():
            return False
        if not self.check_file_name():
            return False
        if not self.check_file_path():
            return False
        # 测试时可屏蔽check_file_exists
        if not self.check_file_exists():
            return False
        if not self.check_file_cate():
            return False
        return True

    def check_files(self):
        if not self.files:
            self.update_errors('files', 'files_blank')
            return False
        return True

    def check_file_cate(self):
        if self.files:
            for files in self.files:
                if files.get('cate') not in self.cate_dict:
                    self.update_errors('file_cate', 'file_cate_err')
                    return False
        return True

    def check_file_name(self):
        if self.files:
            for file in self.files:
                if not file.get('name'):
                    self.update_errors('name', 'file_name_error')
                    return False
                if not file.get('name').strip():
                    self.update_errors('name', 'file_name_error')
                    return False
                if len((file.get('name').strip())) > 100:
                    self.update_errors('name', 'file_name_out_of_bounds')
                    return False
        return True

    def check_file_path(self):
        if self.files:
            for file in self.files:
                if not file.get('path'):
                    self.update_errors('path', 'file_path_error')
                    return False
                if not file.get('path').strip():
                    self.update_errors('path', 'file_name_error')
                    return False
                if len((file.get('path').strip())) > 1000:
                    self.update_errors('path', 'file_path_out_of_bounds')
                    return False
        return True

    def check_file_exists(self):
        if self.files:
            import os
            for file in self.files:
                if file.get('path'):
                    path = os.path.join(settings.MEDIA_ROOT, file.get('path'))
                    if not is_file_exist(path):
                        self.update_errors('path', 'file_not_exists')
                        return False
        return True

    def check_file_id(self):
        if self.files:
            file_ids = [file.get('id') for file in self.files if file.get('id')]
            file_list = File.objects.filter(id__in=file_ids).all()
            if len(file_ids) > len(file_list):
                self.update_errors('id', 'file_not_exists')
                return False
        return True

    def save(self):
        file_data_list = list()
        if self.files:
            for file in self.files:
                file_data = {
                    'cate': file.get('cate'),
                    'path': file.get('path'),
                    'name': file.get('name'),
                    'creator': self.req_user,
                }
                file_data_list.append(file_data)
        file_list = File.objects.bulk_create_or_update(file_data_list)
        return file_list
