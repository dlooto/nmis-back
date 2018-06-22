# coding=utf-8

########################################################################

# 版本发布步骤:
#   git branch v010                 # 在本地创建新分支
#   git push upstream v010:v010     # 推送新分支到远程仓库
#   fab h156 deploy:v010            # 在新分支上执行发布命令
#
# 命令用法:
#   fab h156    deploy     <==only deploy on 156 host
#   fab h_prod  deploy     <==deploy all host in prod hosts
#   fab h156 runtests:nmis,test_api.py   <==运行测试, 其中:nmis,test_api.py为参数

########################################################################

from fabenv import *


# @task
# @with_settings(user=USER)
# def init_deploy_env():
#     """
#     初始化部署环境: create deploy dirs, install libs, clone code and init docker services
#         创建部署目录结构: envs, logs, media, prod
#         安装相应的python/django包
#         创建local设置/符号链接
#         git-clone程序目录
#
#         注: 当前脚本假设服务主机deploy账号已创建
#     """
#     print('Start init deploy...')
#
#     with cd(USER_ROOT):
#         if exists(BASE_DIR):
#             print('%s dir existed, exit directly' % BASE_DIR)
#             return
#
#         # create required dir-structure
#         run('mkdir %s' % BASE_DIR)
#         run('mkdir %s %s %s %s' % (ENVS_DIR, LOGS_DIR, MEDIA_DIR, PROD_DIR))
#         run('mkdir %s %s && mkdir %s' % (ENV_ROOT, LOGS_ROOT, NGX_LOG_DIR))
#         run('mkdir %s' % RESUME_DIR)
#
#     run('virtualenv %s' % ENV_ROOT)
#
#     with cd(PROD_DIR):
#         run('git clone %s' % CODE_REPOS)
#
#     # install python libs
#     with _activate_env():
#         run('pip install -r %s/requirements.txt -i %s' % (CONF_ROOT, PIP_SOURCE))
#
#     # create symbol link: logs, media, nginx conf, supervisord.conf
#     # and init docker services
#     with cd(CODE_ROOT):
#         run('ln -s %s logs' % LOGS_DIR)
#         run('ln -s %s media' % MEDIA_DIR)
#
#         sudo('ln -s %s /etc/nginx/sites-enabled/ngx_web.conf' % NGX_CONF[INIT_ENV_TYPE])
#         sudo('ln -s %s /etc/supervisor/conf.d/supervisord.conf' % SUPERVISORD_CONF[INIT_ENV_TYPE])
#
#     # create docker services
#     _init_docker_services()
#
#     print('Init deploy env success.')
#
#
# @task
# @with_settings(user=USER)
# def init_global_data():
#     """
#     初始化系统数据(创建superuser, loaddata): run this after init_deploy_env
#     """
#     with cd(CODE_ROOT):
#         _update_code()
#         _migrate_data()
#         _load_init_data()
#
@task
def runtests(test_suite='', test_module=''):
    """
    运行测试用例: 示例 fab h156 runtests:suite_name,module_name. 默认运行所有测试用例
    :param test_suite: 要运行的测试包, 如fab h156 runtests:units 将运行units下的所有测试模块
    :param test_module: 要运行具体测试模块, 如fab h104 runtests:units,test_utils.py, 将
                运行runtests/units/test_utils.py里的所有测试用例
    """
    c = get_connection()
    with c.cd(CODE_ROOT):
        if not test_suite:  # run all testcases
            c.run('pytest %s' % TEST_CASE_ROOT)
            return
        if not test_module:
            c.run('pytest %s/%s' % (TEST_CASE_ROOT, test_suite))
            return
        c.run('pytest %s/%s/%s' % (TEST_CASE_ROOT, test_suite, test_module))


@task
def deploy(remote='origin', branch='master'):
    """
    发布更新: fab h156 deploy <==发布更新到指定hosts
    :param remote: 远程仓库名称, 默认为 origin
    :param branch: 部署发布用到的代码分支
    """
    c = get_connection()

    with c.cd(CODE_ROOT):
        _update_code(c, remote, branch)
        _install_env_libs(c)
        _migrate_data(c)

    _flush_redis(c, env.redis_host, env.redis_auth)
    _restart_server(c)


@task
def lean_deploy(remote="origin", branch="master"):
    """
    轻量部署: 更新后端代码并重启gunicorn服务. 用法: fab h156 lean_deploy
    :param remote: 远程代码仓库名, 默认origin
    :param branch: 远程代码仓库分支, 默认master
    :return:
    """
    c = get_connection()
    with c.cd(CODE_ROOT):
        c.run('git checkout %s' % branch)
        c.run('git stash save')
        c.run('git pull')
        c.run('git stash pop')

    _flush_redis(c, env.redis_host, env.redis_auth)
    print("redis flushed")
    c.sudo('supervisorctl %s %s' % ("restart", PROCESS_NAME))
    c.sudo('service nginx restart')
    print("Nginx restarted.")


@task
def supervisor(command='restart', program='all'):
    """
    执行supervisor 命令 示例: fab h156 supervisor:restart,nmis (default: restart all)
    @param command: ('start', 'restart', 'stop', 'status')
    @param program: 应用进程名, 如 nmis
    """
    c = get_connection()

    if command not in ('start', 'stop', 'restart', 'status'):
        return
    if command == 'status':
        program = ''
    c.run('sudo supervisorctl %s %s' % (command, program))


def _flush_redis(c, redis_host, auth):
    """
    刷新缓存
    """
    c.run('redis-cli -h %s  -a %s flushall' % (redis_host, auth))
    print("Redis flushed.")


def _update_code(c, remote, branch):
    c.run('git checkout %s' % branch)
    c.run('git stash save')
    # c.run('git pull %s master' % remote)   # TODO: I don't know why this not works...
    c.run('git pull ')
    c.run('git stash pop')
    # c.run('git fetch %s %s:%s' % (remote, branch, branch))
    # c.run('git checkout %s' % branch)


def _install_env_libs(c):
    """ 安装运行环境与程序库 """
    with c.prefix("source %s" % ACTIVATE_PATH):
        c.run('pip install -r %s/requirements.txt' % CONF_ROOT)


def _migrate_data(c):
    """ 更新数据与表结构 """
    with c.prefix('source %s' % ACTIVATE_PATH):
        with c.cd(CODE_ROOT):
            c.run('python apps/manage.py migrate')   # 注: migrate中会加载初始数据
            c.run('python apps/manage.py collectstatic --noinput')

def _load_init_data(c):
    with c.prefix("source %s" % ACTIVATE_PATH):
        c.run('python apps/manage.py loaddata %s' % ' '.join(INIT_JSON_DATA))

def _restart_server(c):
    """ 重启web服务 """
    c.sudo('supervisorctl reread')  # 用reload将出错
    c.sudo('supervisorctl restart %s' % PROCESS_NAME)
    c.sudo('service nginx reload')
    print("Nginx config reloaded")
