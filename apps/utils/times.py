# coding=utf-8
#
# Created on Jan 8, 2015, by Junn
#
import calendar
import datetime
import time
from functools import wraps

##################################################
#  date and time processing utils
##################################################

from dateutil.relativedelta import relativedelta


def now():
    return datetime.datetime.now()


def today():
    return datetime.date.today()


def yesterday():
    return today() + datetime.timedelta(days=-1)


def tomorrow():
    return today() + datetime.timedelta(days=1)


def weekday():
    """
    获取今天星期几， 如，1对应星期一，4对应周期四，6对应周六等
    """
    return datetime.date.isoweekday(datetime.date.today())


def monday():
    """
    获取当前周星期一的日期
    """
    d = today()
    delta = datetime.date.isoweekday(d) - 1
    return d - datetime.timedelta(days=delta)


def saturday():
    """
    获取当前周周六的日期
    """
    d = today()
    delta = 7 - datetime.date.isoweekday(d)
    return d + datetime.timedelta(days=delta - 1)


def sunday():
    """
    获取当前周周日的日期
    """
    d = today()
    delta = 7 - datetime.date.isoweekday(d)
    return d + datetime.timedelta(days=delta)


def after_days(interval, atime=now()):
    """得到给定时间点向后的某天时间, 默认当前时间向后"""
    return atime + datetime.timedelta(days=interval)


def before_days(atime, interval):
    """
    得到向前的某天的时间, 如atime=now, interval=6, 则表示当前时间的前6天的那个时间
    """
    return atime - datetime.timedelta(days=interval)

# #time handling. 时间的操作, 其本上常用的类有：datetime和timedelta


DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def str_to_datetime(timestr, format=DEFAULT_TIME_FORMAT):
    """
    将时间字符串转为datetime对象.
    @param timestr:  字符串格式形如 "2015-07-23 16:12:39"
    最终转化为 datetime.datetime(2015, 7, 23, 16, 12, 39) 类型对象.
    """
    return datetime.datetime.strptime(timestr, format)


def str_to_time(timestr, format=DEFAULT_TIME_FORMAT):
    """
    将时间字符串转为对应的时间对象
    """
    return time.strptime(timestr, format)


def datetime_to_str(a_datetime, format=DEFAULT_TIME_FORMAT):
    """
    datetime对象转为指定格式字条串
    如 datetime.datetime(2015, 7, 23, 16, 12, 39) 转为 "2015-07-23 16:12:39"
    """
    return a_datetime.strftime(format)


def datetime_strftime(d_date, format=DEFAULT_TIME_FORMAT):
    """
    :param d_date: datetime.datetime类型，如：2015-07-23 16:12:39.130297
    如 datetime.datetime.now(2015-07-23 16:12:39.130297) 转为 "2015-07-23 16:12:39"
    """
    return datetime.datetime.strftime(d_date, format)


def incr(a_datetime, hours=0):
    """
    返回增加指定小时数的时间对象
    @param a_datetime:  datetime对象
    @param hours: 小时数
    @return: 如传入 a_datetime=datetime.datetime(2015, 7, 23, 16, 12, 39), hours=3, 
        返回 datetime.datetime(2015, 7, 23, 19, 12, 39)
    """
    if hours == 0:
        return a_datetime
    return a_datetime + datetime.timedelta(hours=hours)


def get_hour_time(a_datetime):
    """
    返回整点小时时间. 如传入2015-07-23 16:12:39, 将返回 2015-07-23 16:00:00
    """
    return a_datetime.replace(minute=0, second=0)


def get_current_hour_time():
    """ 返回当前系统时间的整点小时时间, datetime对象
    如当前系统时间为2015-07-23 16:12:39, 则返回2015-07-23 16:00:00
    """
    return get_hour_time(now())


def time_cost(begin_time):
    """
    计算花费的时间, 单位: 秒
    """
    return (now() - begin_time).total_seconds()


def get_day_begin_time(date_time, format=DEFAULT_TIME_FORMAT):
    """
    返回当前日期的起始时间. 如传入2017-04-07 16:12:39, 将返回 2017-04-07 00:00:00
    """
    return date_time.replace(hour=0, minute=0, second=0).strftime(format)


def get_day_end_time(date_time, format=DEFAULT_TIME_FORMAT):
    """
    返回当前日期的结束时间. 如传入2017-04-07 16:12:39, 将返回 2017-04-07 23:59:59
    """
    return date_time.replace(hour=23, minute=59, second=59).strftime(format)


def get_next_month():
    """
    返回在当前时间的基础上增加一个月后的日期
    """
    # startTime = datetime.datetime.strptime("2018-02-02", '%Y-%m-%d').date()

    return now() + relativedelta(months=+1)


COLON = ':'
HYPHEN = '-'
FORWARD_SLASH = '/'
TIME_FORMAT_YM_HY = '%Y-%m'
TIME_FORMAT_YMD_HY = '%Y-%m-%d'
TIME_FORMAT_YMD_HMS_HY = '%Y-%m-%d %H:%M:%S'


def is_valid_date(timestr, format=None):
    """
    校验日期
    :param timestr: 日期字符串
    :param format:
    :return:  True or False
    """

    if not timestr:
        return False
    try:
        if format:
            time.strptime(timestr, format)
        if FORWARD_SLASH in timestr:
            timestr = timestr.replace(FORWARD_SLASH, HYPHEN, 2)
        char_count = dict()
        for char in timestr:
            char_count[char] = timestr.count(char)
        if COLON not in timestr:
            if char_count.get(HYPHEN) == 1:
                time.strptime(timestr, TIME_FORMAT_YM_HY)
            else:
                time.strptime(timestr, TIME_FORMAT_YMD_HY)
        else:
            time.strptime(timestr, TIME_FORMAT_YMD_HMS_HY)
        return True
    except Exception as e:
        print(e)
        return False


def date_range(begin_date, end_date, format='%Y-%m-%d'):
    """
    获取时间段内的日期
    :param begin_date: 起始日期
    :param end_date: 截止日期
    :param format: 日期参数的格式
    :return: 返回年、月、日字符串元组对象组成的列表[('1900', '01', '31'), ('1900', '02', '01')]
    """
    dates = []
    date = datetime.datetime.strptime(begin_date, format)
    while date <= datetime.datetime.strptime(end_date, format):
        date_str = date.strftime(format)
        dates.append((date_str[:4], date_str[5:7], date_str[8:11]))
        date = date + datetime.timedelta(1)
    return dates


def month_range(begin_date, end_date, format='%Y-%m-%d'):
    """
    获取时间段内的月份
    :param begin_date: 起始日期
    :param end_date: 截止日期
    :param format: 日期参数的格式
    :return: 返回年、月字符串元组对象组成的列表[('1900', '01'), ('1900', '02')]
    """
    month_set = set()
    for date in date_range(begin_date, end_date, format):
        month_set.add((date[0], date[1]))
    month_list = []
    for month in month_set:
        month_list.append(month)
    return sorted(month_list)


def fn_timer(function):
    """
    打印函数方法执行时长
    装饰器
    :param function:
    :return:
    """
    @wraps(function)
    def function_timer(*args, **kwargs):
        begin_time = time.time()
        result = function(*args, **kwargs)
        end_time = time.time()
        print("Total time running %s: %s seconds" % (function.__name__, str(end_time-begin_time)))
        return result
    return function_timer



if __name__ == '__main__':
    print(month_range('2018-01-01', '2018-02-03'))
