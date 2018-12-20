from flask import current_app
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask_wtf.csrf import generate_csrf

from csh.models import User, News
from csh.modules.index import index_blu


@index_blu.route('/')
def hello_world():
    current_app.logger.debug('debug')
    current_app.logger.error('error')
    # print(current_app.permanent_session_lifetime)
    # 判断用户是否登陆
    data={}
    user_id=session.get('user_id')
    print(current_app.url_map)
    if not user_id:
        data={'info':None}
    else:
        user=User.query.get(user_id)
        data['info']=user.to_dict()
    # 获取排行新闻
    news_l=[]
    news=News.query.order_by(News.clicks.desc()).limit(10)
    for new in news:
        news_l.append(new.to_dict())
    data['news_l']=news_l
    return render_template('news/index.html',data=data)
@index_blu.route('/favicon.ico')
def tubiao():
    # return current_app.send_static_file('news/favicon.ico')
    return redirect(url_for('static',filename='news/favicon.ico'))

