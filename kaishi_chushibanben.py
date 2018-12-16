import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask.ext.wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager

app = Flask(__name__)
manager=Manager(app=app)

class PeiZhiLei(object):
    #调试模式
    DEBUG=True
    #数据库的配置文件
    SQLALCHEMY_DATABASE_URI='mysql://root:mysql@192.168.47.142:3306/f_db'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    #设置redis配置参数
    REDIS_HOST='192.168.47.142'
    REDIS_PORT=6379
    #配置session
    SECRET_KEY='dyh'
    SESSION_TYPE = 'redis'
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1)
    SESSION_USE_SIGNER = True  # 修改为True之后就必须要是何止 serect_key
    PERMANENT_SESSION_LIFETIME = 3600
    #配置日志
    # 默认日志等级
    LOG_LEVEL = logging.DEBUG


app.config.from_object(PeiZhiLei)
db=SQLAlchemy(app=app)
rs=StrictRedis(host=PeiZhiLei.REDIS_HOST,port=PeiZhiLei.REDIS_PORT)
Session(app=app)
Migrate(app=app,db=db)
manager.add_command('db',MigrateCommand)
#scrf 开启
CSRFProtect(app)
#日志函数
def setup_log(config_name):
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
@app.route('/')

def hello_world():

    print(app.permanent_session_lifetime)
    return 'Hello World!'


if __name__ == '__main__':
    # db.create_all()
    manager.run()