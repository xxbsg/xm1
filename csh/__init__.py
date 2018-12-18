from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.ext.session import Session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect

from peizhi import *
db=None
#日志函数
def setup_log():
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=PeiZhiLei.LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def creat_app(ms="ts"):
    global db
    app = Flask(__name__)
    app.config.from_object(zd[ms])
    db=SQLAlchemy(app=app)
    rs=StrictRedis(host=zd[ms].REDIS_HOST,port=zd[ms].REDIS_PORT)
    Session(app=app)
    # print(zd[ms].DEBUG)
    #scrf 开启
    CSRFProtect(app)
    from csh import models
    #开启日志
    # setup_log()
    return app,db
