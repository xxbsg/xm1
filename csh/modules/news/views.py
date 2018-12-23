from flask import abort, jsonify
from flask import g
from flask import render_template
from flask import request
from flask import session

from csh import db
from csh.disanfang.gongyong import user_pd,news_phb
from csh.models import News, Comment, CommentLike
from csh.modules.news import news
from csh.response_code import RET


@news.route('/<int:xw_id>')
@news_phb
@user_pd
def new(xw_id):
    print(xw_id)
    info=g.info
    user=g.user

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
    # 显示收藏状态
    data['sc_zt']=False
    user_dzidl = []
    if user is not None:
        if new in user.collection_news:

            data['sc_zt']=True
    # 显示评论列表  需要参数 新闻id
        user_dzids = CommentLike.query.filter(CommentLike.user_id == user.id).all()

        for i in user_dzids:
            user_dzidl.append(i.comment_id)
    pinglun_l=[]
    pingluns=Comment.query.filter(Comment.news_id==new.id).order_by(Comment.create_time.desc()).all()

    for pinglun in pingluns:
        # 点赞--需要参数:用户id 行为 新闻id 评论id
        p_dic=pinglun.to_dict()
        if Comment.query.filter(pinglun.id in user_dzidl).first() is not None:
            p_dic['dz_zt']=True
        pinglun_l.append(p_dic)
    data['pingluns']=pinglun_l
    return render_template('news/detail.html',data=data)
@news.route('/shoucang',methods=["POST"])
@user_pd
def shoucang():
    # 接收数据: 用户id 收藏行为 新闻id
    user=g.user
    if user is None:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    user_id=user.id
    data=request.json
    xingwei=data.get('xingwei')
    new_id=data.get('new_id')
    if xingwei not in ["shoucang","quxiao_sc"]:
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    if new_id is None:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if News.query.filter(News.id==new_id).first() is None:
        return jsonify(errno=RET.NODATA, errmsg="无数据")
    if xingwei =='shoucang':
        if News.query.get(new_id) not in user.collection_news:
            user.collection_news.append(News.query.get(new_id))
    else:
        if News.query.get(new_id) in user.collection_news:
            user.collection_news.remove(News.query.get(new_id))
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="ok")
@news.route('/pinglun',methods=['POST'])
@user_pd
def pinglun():
    # 需要参数 用户id 评论内容 新闻id
    user=g.user
    if user is None:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    data=request.json
    pinglun_nr=data.get('pinglun_nr')
    new_id=data.get('new_id')
    if not all([pinglun_nr,new_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if News.query.filter(News.id == new_id).first() is None:
        return jsonify(errno=RET.NODATA, errmsg="无数据")
    comment=Comment()
    comment.content=pinglun_nr
    comment.user_id=user.id
    comment.news_id=new_id
    fu_id=data.get('fu_id')
    # 回复需要有父id
    if fu_id is not None:
        comment.parent_id=fu_id
    db.session.add(comment)
    db.session.commit()
    dat={}
    dat['comment']=comment.to_dict()
    return jsonify(errno=RET.OK, errmsg="ok",dat=dat)
@news.route('/dianzan',methods=['POST'])
@user_pd
def dianzan():
    # 点赞 需要参数:用户id 行为 新闻id 评论id
    user=g.user
    if user is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    dat=request.json
    new_id=dat.get('new_id')
    pl_id=dat.get('pl_id')
    xingwei=dat.get('xingwei')
    if not all([new_id,pl_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if xingwei not in ['dianzan','quxiao_dz']:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if News.query.get(new_id) is None:
        return jsonify(errno=RET.NODATA, errmsg="无数据")
    comment=Comment.query.get(pl_id)
    if comment is None:
        return jsonify(errno=RET.NODATA, errmsg="无数据")

    if xingwei=='dianzan':

        if CommentLike.query.filter(CommentLike.user_id==user.id,CommentLike.comment_id==pl_id).first() is None:
            commentlike=CommentLike()
            commentlike.user_id=user.id
            commentlike.comment_id=pl_id
            db.session.add(commentlike)
            comment.like_count+=1

    else:
        commentlike=CommentLike.query.filter(CommentLike.user_id==user.id,CommentLike.comment_id==pl_id).first()
        if commentlike is not None:
            db.session.delete(commentlike)
            comment.like_count -= 1
    db.session.commit()
    return jsonify(errno='0',errmsg='ok')