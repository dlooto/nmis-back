#coding=utf-8
#
# Created on 2013-8-7, by Junn
#
#

#  通用工具模块
import settings
import base64
from math import sin
import uuid, random, re, hashlib, importlib, time, string, inspect
from types import DynamicClassAttribute
from enum import Enum

# 用于求字符串长度，中文汉字计算为两个英文字母长度
ecode = lambda s: s.encode('gb18030')

BASE64ALTCHARS = '-_'

def gen_uuid():
    return str(uuid.uuid1())


def gen_uuid1():
    """gen_uuid生成规则基础上去掉所有横扛"""
    return gen_uuid().replace('-', '')


def rename_file(file, file_name=''):
    """
    rename user uploaded file with uuid or given file name, return renamed file
    file:   request.FILES中获取的数据对象
    """
    suffix = '.' + file.name.split('.')[-1]
    file.name = (file_name or gen_uuid()) + suffix
    return file


phone_format = r'^((\+86)|(86)|(086))?1[34578]\d{9}$'
email_format = r'''^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'''

MOBILE_PHONE_COMPILE = re.compile(phone_format)
PASSWORD_COMPILE = re.compile(r'^\w{6,18}$')
EMAIL_COMPILE = re.compile(email_format)


def is_password_valid(password):
    return True if password and PASSWORD_COMPILE.match(password) else False


def is_phone_valid(phone):
    return True if phone and MOBILE_PHONE_COMPILE.match(phone) else False


def is_email_valid(email):
    """ 对email格式进行验证
    :param email: email字符串
    :return:  True or False
    """
    return True if email and EMAIL_COMPILE.match(email) else False


def normalize_phone(phone):
    """手机号规范化处理, 截取后面11位返回, 如将+8615982231010转为15982231010, 即去掉号码前的86|086|+86等
    """
    phone = ''.join(phone).strip()
    if phone[0] != '+' and len(phone) == 11:
        return phone
    if len(phone) <= 11:
        return phone
    return phone[-11:]  # 从倒数11位起取到尾部


def random_num(len=6):
    """
    根据传入的len长度, 随机生成对应长度的数字字符串
    """
    a = string.digits * (len / 10 + 1)
    return ''.join(random.sample(a, len))


def make_sig(s, secret_key, offset=''):
    """算法: 根据字符串及密钥, 进行加密生成签名"""
    return hashlib.md5('%s%s_%s' % (s, secret_key, offset)).hexdigest().upper()


def hav(theta):
    s = sin(theta / 2)
    return s * s


EARTH_RADIUS = 6371  # 地球平均半径，6371km


def timesince(start_time, end_time, default="1天"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    diff = end_time - start_time
    if end_time > start_time:
        periods = (
            (diff.days / 365, "年"),
            (diff.days / 30, "个月"),
           # (diff.days / 7, "周"),
            (diff.days, "天"),
           # (diff.seconds / 3600, "小时"),
           # (diff.seconds / 60, "分钟"),
           # (diff.seconds, "秒"),
        )
        for period, unit in periods:
            if period:
                return "%d%s" % (period, unit)

    return default


def str_to_time(timestr, format='%Y-%m-%d %H:%M:%S'):
    """将时间字符串转为对应的时间对象"""
    return time.strptime(timestr, format)

def str_to_time1(timestr, format='%Y-%m-%d %H:%M'):
    """将时间字符串转为对应的时间对象"""
    return time.strptime(timestr, format)

def float_list_to_str(float_list):
    """float元素类型列表转为字符串输出"""
    result = ''
    for f in float_list:
        result = '%s|%s' % (result, str(f))
    return result[1:]   


def make_instance(module_name, class_name, *args, **kwargs):
    """
    build instance by module_name and class name passed
    :param module_name: 模板名
    :param class_name: 类名

    Examples:
        x = make_instance("users.models", "User", 0, 4, disc="bust")
    """
    try:
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        return class_(*args, **kwargs)
    except NameError as e:
        raise NameError("Module %s or class %s not defined" % (module_name, class_name))
    except Exception as e:
        raise e  

def get_class_for_name(module_name, class_name):
    """
    Get class from class_name and module_name passed
    :param module_name:
    :param class_name:
    :return:
        class type object
    """
    try:
        m = importlib.import_module(module_name)
        c = getattr(m, class_name)
    except ImportError as e:
        raise e
    except AttributeError as e:
        raise e
    except Exception as e:
        raise e
    return c

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def get_email_host_url(email, prefix='http://'):
    """
    通过邮箱获取邮箱的登录链接
    """
    email = email or ''
    phs = [
        ('163.com', 'mail.163.com'),
        ('126.com', 'mail.126.com'),
        ('189.cn', 'mail.189.cn'),
        ('qq.com', 'mail.qq.com'),
        ('sina.com', 'mail.sina.com.cn'),
        ('sina.cn', 'mail.sina.com.cn'),
        ('gmail.com', 'www.google.com/gmail'),
    ]

    def fallback():
        _pattern = re.compile('@(.*?)$')
        m = _pattern.search(email)
        if m:
            return prefix + m.group(1)
        return ''

    for pattern, host in phs:
        if pattern in email:
            return prefix + host

    return fallback()


def b64encode(s):
    """当 s 最后一位为空格时不能使用"""
    s += (3 - len(s) % 3) * ' '
    return base64.b64encode(s, altchars=BASE64ALTCHARS)


def b64decode(s):
    return base64.b64decode(s, altchars=BASE64ALTCHARS).rstrip()


def filter_emoji(orig_str, dest_str=''):
    """
    把emoji表情变成字符串
    :param orig_str:原字符
    :param dest_str:新字符
    :return:新字符
    """
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(dest_str,orig_str)


def to_bool(value):
    """
    将传入的类bool参数转换为bool值, 如'False'等都会转换为False返回
    :param value: 类bool变量的参数值, 如'False', 'false', 'True', 'true'等
    :return: bool
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (unicode, str)):
        if not value: # 空字符串
            return False
        if value.lower() == 'false':
            return False
        if value.lower() == 'true':
            return True
    raise Exception(u'Bool值转换异常: %s' % value)


def check_day(day):
    """
    检查日期格式是否正确
    :param day:
    """
    pattern = re.compile(r'\d{4}-\d{2}-\d{2}$')
    return True if day and re.match(pattern, day) else False


def included_in(a, b):
    """
    判断列表a是否被列表b包含
    :param a: list object
    :param b: list object
    :return: 交集等于a, 则a包括于b
    """
    return set(a).intersection(set(b)) == set(a)  # 求交集后判断是否与相等


class BaseEnum(Enum):
    """
        自定义枚举类型
        基于python enum.Enum类型
        定义枚举成员时可将二元元祖对象赋值给枚举成员
        .e.g:
        GenderEnum(BaseEnum):
            FEMALE = ('F', '女')
            MALE = ('M', ‘男’)
    """
    @DynamicClassAttribute
    def value(self):
        """The value of the Enum member."""
        if isinstance(self._value_, tuple):
            return self._value_[0]
        return self._value_

    @DynamicClassAttribute
    def value_name(self):
        """The value_name of the Enum member. 枚举值显示名称"""
        return self._value_[0] if isinstance(self._value_, tuple) else ''

    @classmethod
    def members(cls):
        return cls.__members__.items()

    @classmethod
    def values(cls):
        return tuple([item.value for name, item in cls.members()])

    @classmethod
    def value_names(cls):
        return tuple([item.value_name for name, item in cls.members()])