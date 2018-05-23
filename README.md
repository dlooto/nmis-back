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
- pip install virtualenvwrapper
- 创建virtualenv环境(指定Python版本)
- pip install requirements.txt
- 安装MySQL/Redis等数据存储服务
- git clone ssh://git@gitee.com:juyangtech/nextcloud.git
- 创建本地logs, media目录, 修改local.py文件
