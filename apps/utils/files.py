#coding=utf8

"""
used for file process
"""

import os, logging
import settings

logs = logging.getLogger('django')


def is_file_exist(path):
    """ 判断文件或目录是否存在 """
    return os.path.exists(path)


def remove(path, fileName=None):
    """remove file from the filesystem"""
    if not fileName:
        fullpath = path
    else:
        fullpath = os.path.join(path, fileName)
        
    try:
        os.remove(fullpath)
        return True
    except OSError as e:
        logs.error("delete file %s error: %s" % (fullpath, e))
        return False


def save_file(file, base_dir, file_name):
    """保存文件
    @param file  传入的文件参数, request.FILES中获取的数据对象, file需要先经过rename处理, 以便获取到file.name
    @param file_name  保存的目标文件名
     """
    
    if not file: return ''
    try:
        dest = open('%s/%s/%s' % (settings.MEDIA_ROOT, base_dir, file_name), 'wb+')
        for chunk in file.chunks():
            dest.write(chunk)
        dest.close()
    except Exception as e:
        logs.exception(e)
        dest.close()

    return file_name