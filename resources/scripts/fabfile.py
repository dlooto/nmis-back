# coding=utf-8

########################################################################
#                            开发本地环境快捷操作
########################################################################


import re, os
import time
from contextlib import contextmanager as _contextmanager
from fabric.api import hosts, cd, lcd, env, run, local, with_settings, prefix, settings
from fabric.contrib.files import exists, sudo
from fabric.context_managers import hide
from fabric.api import task


ENVS_DIR   = '/Users/junn/work/envs'
PROD_DIR   = '/Users/junn/work/repos'
ENV_ROOT    = '/Users/junn/work/envs/nats'

PROJECT_NAME = 'nats-server'
CODE_ROOT   = os.path.join(PROD_DIR, PROJECT_NAME)

CONF_ROOT = os.path.join(CODE_ROOT, 'deploy')

# PIP_SOURCE = 'http://pypi.douban.com/simple/ --trusted-host pypi.douban.com'
PIP_SOURCE = 'http://pypi.douban.com/simple/'
CODE_REPOS = 'ssh://git@git.pinbot.me:10022/HopperClouds/nats-server.git'  # 代码仓库

ACTIVATE_PATH = os.path.join(ENV_ROOT, 'bin/activate')


##############################################################################
#                               Fixture data
##############################################################################

INIT_JSON_DATA = [
    'users/users.json',
    'organs/init_organs.json',

    'channels/channels.json',
    'channels/zhilian_position_categories.json',
    'channels/wuyou_position_categories.json',
    'channels/lagou_position_categories.json',

    'flows/email_tpl_variables.json',
    'flows/email_tpls.json',
    'flows/join_pool_reasons.json',
    'flows/init_flows.json',
]


@task
def load_data():
    """
    本地加载所有初始化数据
    """
    with lcd(CODE_ROOT):
        #_migrate_data()
        _load_init_data()


def _update_code():
    remote, branch = 'origin', 'master'

    # with settings(hide('warnings', 'running', 'stdout', 'stderr'), timeout=10,
    with settings(hide('running', 'stdout'), timeout=15, warn_only=True):
        local('git stash save')
        local('git checkout %s' % branch)
        local('git pull --rebase %s %s' % (remote, branch))
        local('git stash pop')


def _init_docker_services():
    with cd(CODE_ROOT):
        local('docker-compose -f services.yml up -d')

        local('chmod +x %s/init_database.sh' % CONF_ROOT)
        local('docker cp %s/init_database.sh effe_mysql_1:/' % CONF_ROOT)
        local('docker exec -it effe_mysql_1 bash -c /init_database.sh')

def _install_env_libs():
    """ 安装运行环境与程序库 """
    with _activate_env():
        local('pip install -r %s/requirements.txt' % CONF_ROOT)

def _migrate_data():
    """ 更新数据与表结构 """
    with _activate_env():
        local('python apps/manage.py migrate')   # 注: migrate中会加载初始数据

def _load_init_data():
    with _activate_env():
        local('python apps/manage.py loaddata %s' % ' '.join(INIT_JSON_DATA))

@_contextmanager
def _activate_env():
    with prefix('source %s' % ACTIVATE_PATH):
        yield




