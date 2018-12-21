from flask import g
from flask import session

import functools




def user_pd(f):
    @functools.wraps(f)
    def wapper(*args,**kwargs):

        user_id = session.get('user_id')
        if not user_id:
            data = {'info': None}
        else:
            from csh.models import User
            user = User.query.get(user_id)
            info = user.to_dict()
        g.info = info
        return f(*args,**kwargs)
    return wapper

# def login_user_data(f):
#     # 作用就是 保留 原有函数的一些参数设置 不会被 wrapper修改
#     @functools.wraps(f)
#     def wrapper(*args,**kwargs):
#         user_id = session.get('user_id')
#         if not user_id:
#             data = {'info': None}
#         else:
#             from csh.models import User
#             user = User.query.get(user_id)
#             info = user.to_dict()
#         g.info = info
#         return f(*args,**kwargs)
#     return wrapper
#
def news_phb(f):
    @functools.wraps(f)
    def wapper(*args,**kwargs):
        news_l = []
        from csh.models import News
        news = News.query.order_by(News.clicks.desc()).limit(10)
        for new in news:
            news_l.append(new.to_dict())
        g.news_l= news_l
        return f(*args,**kwargs)
    return wapper