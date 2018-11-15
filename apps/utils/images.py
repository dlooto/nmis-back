# coding=utf8

"""
该图片工具模块在换用Pillow上有问题, 如下:
from PIL import Image
from PIL import ImageFile

产生异常: IOError: broken data stream when reading image file
"""

import os
import copy, logging
from PIL import Image
from PIL import ImageFile

from . import files, eggs
import settings

logger = logging.getLogger('django')


def save_image(file, dest_filename, create_thumb=False, thumb_size=settings.DEFAULT_THUMB_SIZE, cate=''):
    '''保存图片
    @param: file 传入的文件参数, request.FILES中获取的数据对象
    @param: dest_filename 文件数据将保存的目标文件名
    @param: create_thumb  是否生成缩略图
    @param: thumb_size    缩略图尺寸
    @param: cate          要保存的图片类型, avatar-头像, 否则为其他
    '''
    
    if not file:
        return ''
    
    dirs = settings.IMG_DIR
    if cate == 'avatar':
        dirs = settings.USER_AVATAR_DIR

    image = ImageIO.parse(file)

    ImageIO.save(image, '%s/%s' % (settings.MEDIA_ROOT, dirs['original']), dest_filename)  # save original image
    
    if create_thumb and thumb_size:
        image.thumbnail(thumb_size, Image.ANTIALIAS)
        ImageIO.save(image, '%s/%s' % (settings.MEDIA_ROOT, dirs['thumb']), dest_filename)  # save thumbnail image
    
    return dest_filename   # TODO: 后续修改该函数, 返回True or False.


def save_original(file, original_path):
    """
    根据传入的文件数据, 生成原图保存.
    file:  传入的文件参数, request.FILES中获取的数据对象
    """
    if not file or not original_path:
        return ''
    
    file_name = eggs.gen_uuid1()+'.jpg'
    ImageIO.save(ImageIO.parse(file), original_path, file_name)
    return file_name


def save_thumb(file, thumb_path, thumb_name, thumb_size=(90, 90)):
    """
    根据传入的文件数据, 生成缩略图保存, 缩略图与原图同名, 存储路径不一样
    :param file:  request.FILES中获取的数据对象
    :param thumb_name:  该名字与原图名字一致
    """
    if not file or not thumb_path:
        return
    
    image = ImageIO.parse(file)
    image.thumbnail(thumb_size, Image.ANTIALIAS)
    return ImageIO.save(image, thumb_path, thumb_name)


class ImageIO(object):
    """
    该类提供一些常用的图片I/O操作方法，包括解析远程图片，打开或关闭本地图片等.
    注：所有的方法均未拦截错误，如有必要，请在上层处理.
    """

    @classmethod
    def parse(cls, file):
        """解析远程图片文件, 生成Image类型对象返回.
        
        :param file: 从request.FILES中获取的数据对象

        :return img: PIL Image Object
        """
        try:
            parser = ImageFile.Parser()
            for chunk in file.chunks():
                parser.feed(chunk)
        except Exception as e:
            logger.error('%s' % e)
        finally:
            image = parser.close()

        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        return image

    @classmethod
    def open(cls, path, filename):
        """
        通过指定的路径名和文件名打开文件系统内的图片.
        params:
            path: 文件所在的主目录
            filename：文件名

        returns:
            img: PIL Image Object
        """
        full = os.path.join(path, filename)
        if not os.path.exists(full):
            raise Exception("path %s not exist" % full)
        return Image.open(full)

    @classmethod
    def save(cls, image, path, filename, format="JPEG", quality=100, create_dir=True):
        '''保存Image对象到文件系统.

        params:
            image：PIL Image Object
            path：存储图片文件的主目录
            filename：文件名
            format：保存的格式
            quality：保持的图片质量
            create_dir：当该参数为True，指定的主目录不存在则会尝试创建.

        returns：
            执行成功返回True，否则返回False或抛出相关异常
        '''

        path = os.path.normpath(path)
        if not files.is_file_exist(path):
            if create_dir:
                os.makedirs(path)
            else:
                return False
        image.save(os.path.join(path, filename), format, quality=quality)
        return True


class ImageTrimTools(object):
    @classmethod
    def _crop_with_the_preference_to_width(cls, img, width):
        x, y = img.size

        x_s = width
        y_s = y * x_s / x

        return x_s, y_s

    @classmethod
    def _crop_with_the_preference_to_height(cls, img, height):
        x, y = img.size

        y_s = height
        x_s = x * y_s / y

        return x_s, y_s

    @classmethod
    def auto_crop(cls, image, width, height):
        """按指定的高/宽自动剪裁出所需的图片并得到.

        params:
            image：PIL Image Object
            width：剪裁的宽度
            height：剪裁的高度

        returns：
                                执行成功返回image对象
        """
        if not width and not height:
            return None

        x, y = image.size
        if x <= y:
            x_s, y_s = cls._crop_with_the_preference_to_width(image, width)
            if y_s < height:
                x_s, y_s = cls._crop_with_the_preference_to_height(image, height)
                half_x = width / 2
                half_x_ori = x_s / 2
                XY = (half_x_ori - half_x, 0, half_x_ori + half_x, y_s)
            else:
                half_y = height / 2
                half_y_ori = y_s / 2
                XY = (0, half_y_ori - half_y, x_s, half_y_ori + half_y)
        else:
            x_s, y_s = cls._crop_with_the_preference_to_height(image, height)
            if x_s < width:
                x_s, y_s = cls._crop_with_the_preference_to_width(image, width)
                half_y = height / 2
                half_y_ori = y_s / 2
                XY = (0, half_y_ori - half_y, x_s, half_y_ori + half_y)
            else:
                half_x = width / 2
                half_x_ori = x_s / 2
                XY = (half_x_ori - half_x, 0, half_x_ori + half_x, y_s)

        resized = image.resize((x_s, y_s), Image.ANTIALIAS)
        return resized.crop(XY)

    @classmethod
    def crop(cls, image, xy):
        """根据指定坐标剪裁图片
        params:
            img: Image object
            xy:  剪切坐标,tuple类型,各坐标点为整数, 形如 (x1, y1, x2, y2)
        return:
            image: 按坐标剪切后的New Image object.
        """

        _image = image.copy()
        _image = _image.crop(xy)
        return _image

    @classmethod
    def scale(cls, img, width=None, height=None):
        """按指定的高/宽实现图片缩放.

        params:
            image：PIL Image Object
            width：缩放的宽度
            height：缩放的高度

        returns：
            执行成功返回image对象
            注：宽度和高度只需其一，默认以宽度为准
        """
        x, y = img.size

        if x > y and width:
            x_s = width
            y_s = y * x_s / x
        elif x <= y and height:
            y_s = height
            x_s = x * y_s / y
        else:
            return None

        return img.resize((x_s, y_s), Image.ANTIALIAS)


class BaseImageParser(object):
    """该类仅完成对传入图片的存储，使用示例：
        parser = BaseImageParser()
        if parser.is_valid() and parser.parse() and parser.save():
            print 'Succeed!'
        else:
            print 'Error:', parser.error or parser.sys_error
    params:
        files：image对象列表
        config：相关图片配置
    """

    def __init__(self, files, config):
        self.files = files
        self.parsed = []
        self.config = config
        self.error = ''
        self.sys_error = None

    def is_valid(self):
        """
        验证待处理的图片是否符合要求
        """
        if not self.files:
            self.error = u'请选择需要上传的图片'
            return False

        for name, limit in self.config.get('limits').iteritems():
            func = getattr(self, 'check_' + name, None)
            if func:
                if not func(limit):
                    return False

        return True

    def load_all(self):
        """
         在此完成图片的加载，如从远程下载图片转换为image对象并保存在self.parsed中
        """
        pass

    def parse(self):
        """
        在此完成对图片的处理，如剪裁等操作，完成后将原文件替换
        """
        self.parsed = self.files
        return True

    def save_all_dims(self, img, filename):
        dims = self.config.get('dims')
        if not type(dims) == dict:
            self.sys_error = u'配置错误，"dims"配置项必须为字典形式'
            return False

        for dim in dims.values():
            if not type(dim) == dict:
                continue

            try:
                width, height = dim['size']
                action = dim['action']
                dir = dim['dir']
                quality = dim['quality']
            except:
                self.sys_error = u'配置错误，"size"格式错误'
                return False

            if action == 'crop':
                # 按所需大小剪裁
                manipulated = ImageTrimTools.auto_crop(img, width, height)
            elif action == 'scale':
                # 缩放图片并保持原比例
                manipulated = ImageTrimTools.scale(img, width, height)
            else:
                continue
            if not ImageIO.save(manipulated, dir, filename, quality=quality):
                return False

        return True

    def delete_all_dims(self, filename):
        dims = self.config.get('dims')
        if not type(dims) == dict:
            self.sys_error = u'配置错误，"dims"配置项必须为字典形式'
            return False

        for dim in dims.values():
            files.remove(dim['dir'], filename)     # TODO: some error handling later

        return True

    def save_origin(self, img, filename, quality=100):
        origin = self.config.get('origin')
        if origin and type(origin) == dict and origin.get('dir'):
            if ImageIO.save(img, origin.get('dir'), filename, quality=quality):
                return True
            self.sys_error = u'原图存储错误'
        else:
            self.sys_error = u'配置错误，"origin"配置段格式错误'
        return False

    def save(self, filenames=[], save_origin=True, save_dims=True):
        images = []

        count = len(self.parsed)

        filenames = copy.copy(filenames)
        if filenames:
            if not len(filenames) == count:
                self.sys_error = u'传入的文件名数与图片数不符'
                return False
            filenames = [filename + '.jpg' for filename in filenames]
        else:
            for i in range(count):
                filenames.append(eggs.gen_uuid1() + '.jpg')

        for img, filename in zip(self.parsed, filenames):
            if save_dims and not self.save_all_dims(img, filename):
                return None
            if save_origin and not self.save_origin(img, filename):
                return None

            images.append(filename)

        return images

    def delete(self, filename, delete_all_dims=True):
        if delete_all_dims:
            return self.delete_all_dims(filename)

        return


class GenericImageParser(BaseImageParser):
    """
            该类用于根据配置验证、处理、保存用户上传的图片
            使用环境：由客户端通过request.FILES上传图片，服务器自动处理图片的场景
    params:
        files：从request.FILES中得到的图片
        config：相关图片配置
    """

    def check_formats(self, formats):
        """
        验证上传的图片格式是否符合要求
        """
        for image in self.files:
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in formats:
                self.error = u'上传的图片中包含不被支持的格式'
                return False
        return True

    def check_max_file_size(self, max_image_size):
        """
                    验证上传的图片是否超过文件大小限制
        """
        for image in self.files:
            if image.size > max_image_size:
                self.error = u'上传的图片超过大小限制'
                return False
        return True

    def check_min_image_size(self, limit):
        """
        验证上传的图片尺寸是否小于最小限制
        """

        if not self.load_all():
            return False

        for image in self.parsed:
            if image.size[0] < limit[0] or image.size[1] < limit[1]:
                self.error = u'上传的图片尺寸太小'
                return False
        return True

    def load_all(self):
        if self.parsed:
            return True

        try:
            for file in self.files:
                self.parsed.append(ImageIO.parse(file))
        except Exception as e:
            self.error = u'图片解析失败'
            self.sys_error = 'Error in parsing image:', str(e)
            return False

        return True

    def parse(self):
        return self.load_all()


class ManualCropParser(GenericImageParser):
    def __init__(self, file_names, xy, config):
        self.file_names = file_names
        self.parsed = []
        self.xy = xy
        self.config = config
        self.error = ''
        self.sys_error = None

    def is_valid(self):
        return self.load_all()

    def load_all(self):
        if self.parsed:
            return True

        origin = self.config.get('origin')
        if origin and type(origin) == dict and origin.get('dir'):
            base_path = origin.get('dir')
        else:
            self.sys_error = u'配置错误，"origin"配置段格式错误'
        for name in self.file_names:
            if not name:
                self.error = u'含有无效的文件名'
                return False

            path = os.path.join(base_path, name)
            if not os.path.exists(path):
                self.error = u'获取文件错误'
                return False

            try:
                self.parsed.append(Image.open(path))
            except Exception as e:
                self.error = u'含有无效的文件'
                self.sys_error = str(e)

        return True

    def parse(self):
        try:
            croped = []
            for image in self.parsed:
                croped.append(ImageTrimTools.crop(image, self.xy))
            self.parsed = croped
        except Exception as e:
            self.sys_error = str(e)
            return False
        return True

    def save(self, save_origin=False, save_dims=True, **kwargs):
        return super(ManualCropParser, self).save(self.file_names,
                                                  save_origin=False)


def check_images_exist(dims, filenames):
    """
    通过传入的图片规格配置和文件名，验证文件是否存在

    params:
        dims:        图片规格配置（lershare标准media配置方式），必须是dict
        fileName：        需要验证的文件名称

    return:
                    成功返回True，否则返回False
    """

    for filename in filenames:
        for dim in dims.values():
            if not os.path.exists(os.path.join(dim.get('dir'), filename)):
                return False
    return True
