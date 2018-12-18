import logging
from redis import StrictRedis


class PeiZhiLei(object):
    #调试模式
    DEBUG=True
    #数据库的配置文件
    SQLALCHEMY_DATABASE_URI='mysql://root:mysql@192.168.47.128:3306/f_db'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    #设置redis配置参数
    REDIS_HOST='192.168.47.128'
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

class TiaoShi(PeiZhiLei):
    DEBUG = True

class xianshang(PeiZhiLei):
    DEBUG = False

zd={"ts":TiaoShi,"xs":xianshang}