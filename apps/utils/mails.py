# coding: utf-8
import base64
import logging
from hashlib import md5
from email.parser import FeedParser
from poplib import POP3, POP3_SSL, error_proto
from re import compile

# import DNS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('django')

ENCODING_MAP = {'gb2312': 'gbk'}
MX_DNS_CACHE = {}

PATTERN_POP3 = [
    (compile('mxbiz\d?\.qq\.com'), 'pop.exmail.qq.com'),
    (compile('\.qq\.com$'), 'pop.qq.com:995'),
    (compile('\.zoho\.com$'), 'pop.zoho.com:995'),
    (compile('\.netease\.com'), 'pop.163.com'),
]


def get_pop3_by_mx(mx):
    """
    通过对MX记录进行匹配来得到POP3服务器地址
    需要完善 ``PATTERN_POP3`` 来支持更多的邮件服务

    >>> get_pop3_by_mx('mxbiz1.qq.com.')
    'pop.qq.com'
    """
    for pattern, pop3 in PATTERN_POP3:
        if pattern.search(mx):
            return pop3
    return None


# def get_pop3_by_email(email):
#     """
#     通过邮件地址得到POP3服务器地址
#     """
#     if not email or '@' not in email:
#         return None
#
#     host = email.split('@')[-1]
#     try:
#         mx_list = MX_DNS_CACHE.setdefault(host, DNS.mxlookup(host))  # 对查询过的mx记录进行缓存
#     except DNS.ServerError:
#         return None
#     mx = mx_list[0][1]
#     pop3 = get_pop3_by_mx(mx)
#     logger.info('email: {} mx: {} pop3: {}'.format(email, mx_list, pop3))
#     return pop3


def feed_decode(body):
    """
    使用 ``FeedParser`` 对邮件的body进行解码
    如果 body 中含有附件等, 只取邮件正文
    """

    def _traverse(msg):
        if isinstance(msg._payload, list):
            return _traverse(msg._payload[0])
        return msg

    parser = FeedParser()
    for data in body:
        parser.feed(data + '\n')
    messages = parser.close()
    payload = _traverse(messages)
    return payload.get_payload(decode=True)


class Mail(object):
    def __init__(self, server_msg, body, octets):
        self.server_msg = server_msg
        self.body = body
        self.octets = octets

        self.id = self.get_md5()

    def get_md5(self):
        m = md5()
        m.update(''.join(self.body))
        return m.hexdigest()

    def decode(self, s, charset):
        if charset in ENCODING_MAP:
            charset = ENCODING_MAP[charset]
        return str.decode(s, charset)

    def get_subject(self):
        """
        返回邮件标题

        :rtype: unicode
        """
        pattern = compile('^[sS]ubject: =\?(.+?)\?B\?(.*)\?=')
        for line in self.body:
            m = pattern.search(line)
            if m:
                string = base64.b64decode(m.group(2))
                return self.decode(string, m.group(1))
        return u''

    def get_text(self):
        """
        返回解码后的邮件原文

        :rtype: unicode
        """
        text = feed_decode(self.body)
        if not text:
            return u''
        for encoding in ('utf-8', 'gbk'):
            try:
                return text.decode(encoding)
            except UnicodeError:
                pass
        return text

    def __str__(self):
        return 'Mail object - {}'.format(self.body[0])


class Mailbox(object):
    def __init__(self, username, password, server=None):
        """
        :param username:
        :param password:
        :param server: 'pop.zoho.com:995'
        """
        self._username = username
        self._password = password

        # if server is None:
        #     server = get_pop3_by_email(username)

        self._server = server
        self._client = None

    @property
    def client(self):
        """
        :rtype: POP3
        """
        if not self._client:
            host_port = self._server.split(':')
            kw = {}
            if len(host_port):
                kw['host'] = host_port[0]
            if len(host_port) == 2:
                kw['port'] = int(host_port[1])
            logger.debug('creating pop3 client {}'.format(kw))
            if kw.get('port') == 995:
                client = POP3_SSL(**kw)
            else:
                client = POP3(**kw)
            client.user(self._username)
            client.pass_(self._password)
            self._client = client
        return self._client

    def is_alive(self):
        """检测当前连接是否可用, 当服务器或帐号信息不正确时返回 ``False`` """
        if not self._server:
            return False
        try:
            self.client.stat()
            return True
        except (error_proto, Exception) as e:
            logger.exception('invalid connection')
            return False

    def get_stat(self):
        """
        :return: (message_count, total_size)
        """
        return self.client.stat()

    def get_count(self):
        """邮箱中邮件总数"""
        return self.get_stat()[0]

    def retrieve(self, index):
        """
        :return: A ``Mail`` object.
        """
        retrieved = self.client.retr(index)  # (server_msg, body, octets)
        return Mail(*retrieved)

    def mails(self):
        """
        :rtype: list[Mail]
        """
        import poplib
        old_line = poplib._MAXLINE
        poplib._MAXLINE *= 4
        for i in self._get_indexes():
            try:
                yield self.retrieve(i)
            except Exception:
                logger.warning(u'邮件获取报错,或许需要调整poplib._MAXLINE, index:{}'.format(i))
        poplib._MAXLINE = old_line

    def _get_indexes(self, start=1):
        """
        Return valid mail index for ``retrieve`` .
        """
        for i in range(self.get_stat()[0], 0, -1):
            yield i

    def __str__(self):
        return '<Mailbox object - {} mails with {}>'.format(self.get_count(), self._username)


def verify(email, password, pop3=''):
    """
    输入邮件地址和密码检验是否可以登录到邮件服务器
    """
    pop3 = pop3 or get_pop3_by_email(email)
    if not pop3:
        return False

    mail_box = Mailbox(username=email, password=password, server=pop3)
    return mail_box.is_alive()

