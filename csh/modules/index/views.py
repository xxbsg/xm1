from flask import current_app, jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_wtf.csrf import generate_csrf

from csh.models import User, News, Category
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
    #新闻分类
    cary = Category.query.all()

    cary_l = []
    for i in cary:
        cary_l.append(i.to_dict())
    data['carys'] = cary_l
    # for i in data['carys']:
    #     print(i['name'])
    return render_template('news/index.html',data=data)
@index_blu.route('/favicon.ico')
def tubiao():
    # return current_app.send_static_file('news/favicon.ico')
    return redirect(url_for('static',filename='news/favicon.ico'))
@index_blu.route('/news')
def news():
    # 需要 分类id 时间排序 页数 每页条数
    cid=request.args.get('cid',1)
    page=request.args.get('page',1)
    per_page=request.args.get('per_page',20)
    try:
        cid=int(cid)
        page=int(page)
        per_page=int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        cid=1
        page=1
        per_page=20
    fik_l=[]
    if cid != 1:
        fik_l.append(News.category_id==cid)
    news=News.query.filter(*fik_l).order_by(News.create_time.desc()).paginate(page=page,per_page=per_page)
    totalPage=news.pages#返回总页数

    l=[]
    for i in news.items:
        l.append(i.to_basic_dict())
    return jsonify(errno=0,data=l,totalPage=totalPage)
