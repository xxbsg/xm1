from flask import g, jsonify
from flask import render_template
from flask import request

from csh import constants
from csh import db
from csh.disanfang.gongyong import user_pd
from csh.disanfang.image_yun import storage
from csh.models import User, News, Category
# from csh.modules.user import user
from . import user
from csh.response_code import RET


@user.route('/')
@user_pd
def zhuyemian():
    info = g.info
    user = g.user
    data = {}
    data["info"] = info

    return render_template('news/user.html',data=data)
@user.route('/base_info',methods=['post','get'])
@user_pd
def baseinfo():
    data={}
    user=g.user
    method = request.method



    if method == 'POST':
        if user is None:
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登陆')
        dat=request.json
        gxqianming=dat.get('new_gxqm','')
        nc=dat.get("nick_name")
        gender=dat.get('gender')
        if not all([nc,gender]):
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        user.nick_name=nc
        user.gender=gender
        user.signature=gxqianming
        db.session.commit()
        return jsonify(errno=RET.OK, errmsg='ok')
    else:
        if user is None:
            data['nc'] = ''
        else:
            data['nc']=user.nick_name
            data['gxqm']=user.signature
            data['gender']=user.gender



    return render_template('news/user_base_info.html',data=data)
# 头像
@user.route('/touxiang',methods=['post','get'])
@user_pd
def touxiang():
    info=g.info
    user=g.user
    data={}
    data['info']=info
    if request.method=='POST':
        if user is None:
            return jsonify(errno=RET.SESSIONERR,errmsg='没有登陆')
        img=request.files
        print(img)
        if img.__len__() ==0:
            return jsonify(errno=RET.SESSIONERR,errmsg='没有选择头像')
        img_d=img.get('avatar').read()
        img_name=storage(img_d)
        print(img_name)
        user.avatar_url=img_name
        db.session.commit()
        dat={'avatar_url':constants.QINIU_DOMIN_PREFIX+img_name}
        return jsonify(errno='0',errmsg='0k',data=dat)
        # print(img.get('avatar').read())
    else:

          pass
    return render_template('news/user_pic_info.html',data=data)
# 修改密码
@user.route('/xiugaimima',methods=['post','get'])
@user_pd
def xgmm():
    user=g.user
    if request.method=="POST":
        if user is None:
            return jsonify(errno=RET.SESSIONERR, errmsg='没有登陆')
        dat=request.json
        old_mm=dat.get('old_password')
        new1_mm=dat.get('new_password')
        new2_mm=dat.get('new_password2')
        if not all([old_mm,new1_mm,new2_mm]):
            return jsonify(errno=RET.PARAMERR,errmsg='参数不全')
        if new1_mm != new2_mm:
            return jsonify(errno=RET.PARAMERR,errmsg='两次输入的密码不一致')
        if not user.check_passowrd(old_mm):
            return jsonify(errno=RET.PARAMERR,errmsg='输入的密码错误')
            user.password = new2_mm
            db.session.commit()
        else:
            return jsonify(errno=RET.PARAMERR,errmsg='和原密码一致,没有修改')

        return jsonify(errno='0',errmsg='0k')
    else:
        return render_template('news/user_pass_info.html')
# 我的收藏
@user.route('/mysc',methods=['post','get'])
@user_pd
def mysc():
    data = {}
    info=g.info
    user=g.user
    data['info']=info
    if user is None:
        data = {}
    else:
        news=user.collection_news
        new_id=[]
        for i in news:
            new_id.append(i.id)
        page=request.args.get('page',1)
        try:
            page=int(page)
        except Exception as e:
            page=1
        news_sc = News.query.filter(News.id.in_(new_id) ).order_by(News.create_time.desc()).paginate(page=page,per_page=2)
        items=news_sc.items
        dqy=news_sc.page
        zys=news_sc.pages
        data['news_sc']=items
        data['dqy']=dqy
        data['zys']=zys
    return render_template('news/user_collection.html',data=data)
# 发布新闻
@user.route('/fbxw',methods=['post','get'])
@user_pd
def fbxw():
    data = {}
    user=g.user
    if request.method=='POST':
        if user is None:
            return  jsonify(errno=RET.SESSIONERR,errmsg='用户未登录')
        dat=request.form
        print(dat)
        biaoti=dat.get('title')
        fenlei=dat.get('cagtegory_id')
        zhaiyao = dat.get('digest')
        sy_img = request.files
        print(sy_img)
        neirong = dat.get('content')
        if not all([biaoti,fenlei,zhaiyao,neirong]):
            return jsonify(errno=RET.PARAMERR,errmsg='参数不全')
        if sy_img.__len__() == 0:
            return jsonify(errno=RET.SESSIONERR, errmsg='没有选择头像')

        img_d = sy_img.get('index_image').read()
        img_name = storage(img_d)
        print(img_name)
        new = News()
        new.index_image_url = constants.QINIU_DOMIN_PREFIX+img_name
        new.title=biaoti
        new.digest=zhaiyao
        new.source = '个人'
        new.content=neirong
        new.status=1
        new.category_id = fenlei
        new.user_id = user.id
        try:
            db.session.add(new)

            db.session.commit()
            fl=Category.query.filter(Category.id==int(fenlei)).first()
            fl.news_list.append(new)
            db.session.commit()
        except Exception as e:
            print(e)
        return jsonify(errno=RET.OK, errmsg='ok')

    else:
        fenleis=Category.query.all()
        data['fenleis']=fenleis
        return render_template('news/user_news_release.html',data=data)

    # 关注列表
@user.route('/gzlb', methods=['post', 'get'])
@user_pd
def gzlb():
    user=g.user
    data={}
    if request.method=="POST":
        dat=request.json
        action=dat.get('action')
        user_id = dat.get('user_id')
        if not all([action,user_id]):
            return jsonify(errno=RET.SESSIONERR,errmsg='参数不全')
        if user is None:
            return jsonify(errno=RET.SESSIONERR,errmsg='未登录')
        user2=User.query.filter(User.id==user_id).first()
        if user2 in user.followers:
            user.followers.remove(user2)
            db.session.commit()
        return jsonify(errno=0,errmsg='ok')
    else:

        data['user']=user
        data['is_followed'] = True  # 关注状态
        data['tx_qz']=constants.QINIU_DOMIN_PREFIX

        gz = user.followers
        new_id = []
        for i in gz:
            new_id.append(i.id)
        page = request.args.get('page', 1)
        try:
            page = int(page)
        except Exception as e:
            page = 1
        news_sc = gz.paginate(page=page,per_page=2)
        items = news_sc.items
        dqy = news_sc.page
        zys = news_sc.pages
        data['gz'] = items
        data['dqy'] = dqy
        data['zys'] = zys

        return render_template('news/user_follow.html',data=data)
@user.route('/xwlb', methods=['post', 'get'])
@user_pd
def xwlb():
    data={}
    user=g.user
    data['user']=user
    if request.method=='POST':
        return jsonify(errno=0,errmsg='ok')
    else:

        gz = user.news_list
        # new_id = []
        # for i in gz:
        #     new_id.append(i.id)
        page = request.args.get('p', 1)
        try:
            page = int(page)
        except Exception as e:
            page = 1
        news_sc = gz.paginate(page=page, per_page=2)
        items = news_sc.items
        dqy = news_sc.page
        zys = news_sc.pages
        data['gz'] = items
        data['dqy'] = dqy
        data['zys'] = zys


        return render_template('news/user_news_list.html',data=data)
