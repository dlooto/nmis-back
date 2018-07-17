# NMIS(The Next Medical Industry Solution):  新一代医疗行业解决方案系统

## 功能简介
- 项目管理
- 医疗资产管理

## 代码工程结构
```

├── apps            # Python源码目录
├── deploy          # 部署配置文件目录
├── resources       # 项目资源文件目录: sql脚本, 系统初始数据, 数据备份, shell等 
├── static          # 前端静态文件目录: img/css/js/image等
├── templates       # HTML模板文件目录
├── docs            # 项目文档   
├── logs            # 系统日志存放目录, 一般仅为一个符号链接到其他目录挂载点
├── media           # 音频/媒体等文件存放目录, 一般仅为一个符号链接到其他目录挂载点 
├── README.md
├── fab_env.py      # fabric参数配置   
├── fabfile.py      # fabric脚本模块

```

## 运行部署
- Install Python3.6.5
    >>> sudo apt install python3 python3-pip python-dev python3-dev python-pip virtualenvwrapper
    >>> sudo apt install 
- pip install virtualenvwrapper
- 创建virtualenv环境(指定Python版本)
- git clone ssh://git@gitee.com:juyangtech/nmis.git
- cd <work_dir>/nmis-back
- 创建本地logs, logs/nmis-back, media目录, 修改local.py文件
- pip install -r deploy/requirements.txt
- 安装MySQL/Redis等数据存储服务
- 创建DB: CREATE DATABASE nmis CHARACTER SET utf8;
- python apps/manage.py migrate 


## Initial data with fixtures(加载初始数据)

fixtures can be written as JSON, XML or YAML 
 ```
python apps/manage.py loaddata <fixturename>

python apps/manage.py loaddata channels/channels.json
 ```
* <fixturename> is the name of the fixture file you’ve created
* Each time you run loaddata, the data will be read from the fixture and re-loaded into the database. 
Note this means that if you change one of the rows created by a fixture and then run loaddata again, 
  you’ll wipe out any changes you’ve made.
  
* When running manage.py loaddata, you can also specify a path to a fixture file, which overrides 
  searching the usual directories.


## 如何编写 pytest 测试样例
http://blog.csdn.net/liuchunming033/

只需要按照下面的规则：

* 测试文件以 test_ 开头
* 测试类以 Test 开头，并且不能带有 __init__ 方法
* 测试函数以 test_ 开头
* 断言使用基本的 assert 即可


### 如何执行 pytest 测试样例
```
py.test                 # run all tests below current dir
py.test test_mod.py     # run tests in module
py.test somepath        # run all tests below somepath
py.test - k stringexpr  # only run tests with names that match the# the "string expression", e.g. "MyClass and not method"# will select TestMyClass.test_something# but not TestMyClass.test_method_simple
pytest apps/runtests/integration/_users/test_user.py::UserTestCase::test_login    # 执行模块下某个特定测试方法
```        

## 单元测试代码规范
* 各模块间若有公用的逻辑, 可提取出来.
* 一个py测试模块内, 尽量将对model的测试和对api接口的测试分开为不同的TestCase
* 当请求参数为json时, 必须传入参数content_type='application/json', 且参数必须用json.dumps处理过  
# 
