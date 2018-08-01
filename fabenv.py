# coding=utf-8
#
# Created by junn, on 2018-6-20
#

##############################################################################
#                               HOSTS and DIR settings
##############################################################################

import os

from invoke import task, env
from fabric import Config, Connection


USER = 'deploy'
USER_ROOT = '/home/deploy/'
BASE_DIR = '/home/deploy/nmis/'                  # 项目部署根目录

PROD_DIR   = os.path.join(BASE_DIR, 'prod/')     # 程序目录根目录
LOGS_DIR   = os.path.join(BASE_DIR, 'logs/')     # 日志文件目录
MEDIA_DIR  = os.path.join(BASE_DIR, 'media/')    # 媒体静态文件目录根

NGX_LOG_DIR = os.path.join(LOGS_DIR, 'nginx/')    # nginx访问日志

PROCESS_NAME = 'nmis'  # 程序在supervisor中的进程名
PROJECT_NAME = 'nmis-back/'
CODE_ROOT   = os.path.join(PROD_DIR, PROJECT_NAME)          # 后端代码根目录
ENV_ROOT    = os.path.join(USER_ROOT, '.virtualenvs/nmis/')  #
LOGS_ROOT   = os.path.join(LOGS_DIR, PROJECT_NAME)

TEST_CASE_ROOT = os.path.join(CODE_ROOT, 'apps/runtests/')

CONF_ROOT = os.path.join(CODE_ROOT, 'deploy/')

PIP_SOURCE = 'http://pypi.douban.com/simple/ --trusted-host pypi.douban.com'
CODE_REPOS = 'git@gitee.com:tenda-dev/nmis-back.git'  # 代码仓库

# nginx conf
NGX_CONF = {
    'local':  os.path.join(CONF_ROOT, 'local/ngx_web.conf'),
    'prod':   os.path.join(CONF_ROOT, 'prod/ngx_web.conf'),
}

SUPERVISORD_CONF = {   # supervisor conf
    'local':  os.path.join(CONF_ROOT, 'local/supervisord.conf'),
    'prod':   os.path.join(CONF_ROOT, 'prod/supervisord.conf'),
}

ACTIVATE_PATH = os.path.join(ENV_ROOT, 'bin/activate')


##############################################################################
#                               Fixture data
##############################################################################

INIT_JSON_DATA = [
    'users.json',
    'hospitals.json',
    'project_flows.json',

]


@task
def bsite(ctx):
    """ 前置Task: 线上测试主机 """
    env.host = '47.92.154.145'

    env.redis_user = None
    env.redis_host = '127.0.0.1'
    env.redis_auth = 'root'
    env.sudo_password = 'Td@80-ply'

    # return Connection(env.host, user=USER)

@task
def h_prod(ctx):
    """ 前置Task: 生产环境主机 """
    env.host = ''
    env.redis_user = None
    env.redis_host = '127.0.0.1'
    env.redis_auth = 'root'


def get_connection():
    config = Config(
        overrides={'sudo': {'password': env.sudo_password}, },
    )
    return Connection(env.host, user=USER, config=config)


