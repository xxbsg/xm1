from flask import abort
from flask import g
from flask import render_template

from csh.disanfang.gongyong import user_pd,news_phb
from csh.models import News
from csh.modules.news import news


@news.route('/<int:xw_id>')
@news_phb
@user_pd
def new(xw_id):
    print(xw_id)
    info=g.info
    news_l=g.news_l
    data={}
    data["info"]=info
    data['news_l']=news_l
    try:
        new=News.query.filter(News.id==xw_id).first()
    except Exception as e:
        return "cuo wu"
    if not new:
        abort(404)
    data['new']=new.to_dict()
    return render_template('news/detail.html',data=data)