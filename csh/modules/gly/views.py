from datetime import datetime
import time
from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from csh import constants, db
from csh.disanfang.gongyong import user_pd
from csh.disanfang.image_yun import storage
from csh.models import User, News, Category
from csh.modules.gly import gly
from csh.response_code import RET


@gly.route('/login',methods=['POST',"GET"])
def login():
    data={}
    data['cw']=None
    if request.method=="POST":
        dat=request.form
        yhm=dat.get('username')
        mm=dat.get('password')
        if not all([yhm,mm]):
            data['cw']='用户名或密码不能为空'
        user2=User.query.filter(User.mobile==yhm).first()
        if user2 is None:
            data['cw']='用户不存在请注册'
            return render_template('admin/login.html', data=data)
        if not user2.is_admin:
            data['cw']='用户权限不足'
            return render_template('admin/login.html', data=data)
        # print(session)
        session['user_id']=user2.id
        session["user_mobile"] = user2.mobile
        session['user_nc'] = user2.nick_name
        return redirect(url_for('admin.index'))
    return render_template('admin/login.html',data=data)

@gly.route('/index',methods=['POST',"GET"])
@user_pd
def index():
    user=g.user
    data={}
    data['user']=user
    data['img_qz']=constants.QINIU_DOMIN_PREFIX
    return render_template('admin/index.html',data=data)

@gly.route('/yhtj',methods=['get','post'])
def yhtj():
    time=datetime.now()
    xx_time=time.timetuple()
    rq=time.date()
    z_rs=User.query.filter(User.is_admin!=1).count()
    m_rs=User.query.filter(User.create_time>rq.replace(day=1),User.is_admin!=1).count()
    r_rs=User.query.filter(User.create_time>rq.replace(day=xx_time.tm_mday),User.is_admin!=1).count()
    day_l=[]
    day_rs=[]
    for i in range(0,11):
        rz=xx_time.tm_mday-i
        d=rq.replace(day=rz)
        d2=d.replace(day=rz+1)
        day_l.append(d.strftime('%Y-%m-%d').strip())
        day_rs.append(User.query.filter(d2>User.create_time,User.create_time > d).count())
    day_rs.reverse()
    day_l.reverse()
    print(day_l)
    data={'day_rs':day_rs,'day_l':day_l}
    data['z_rs']=z_rs
    data['m_rs']=m_rs
    data['r_rs']=r_rs
    # r_rs=User.query.filter(User.create_time>rq.replace(day=1)).count()
    return render_template('admin/user_count.html',data=data)
@gly.route('/yhlb',methods=['get','post'])
def yhlb():
    dat=request.args
    page=dat.get('p',1)
    try:
        page=int(page)
    except:
        page=1
    yh_l=User.query.filter(User.is_admin!=1).order_by(User.last_login.desc()).paginate(page=page,per_page=2)
    yh=yh_l.items
    dqy=yh_l.page
    zys=yh_l.pages
    data={'yh':yh,'dqy':dqy,'zys':zys}
    return render_template('admin/user_list.html',data=data)
@gly.route('/xwsh',methods=['get','post'])
def xwsh():
    if request.method=="POST":
        pass
    else:
        data={}
        dat = request.args
        page = dat.get('p', 1)
        kw=dat.get('kw')
        f=[]
        if kw:
            f.append(News.title.like("%"+kw+"%"))
            data['kw']=kw
        try:
            page = int(page)
        except:
            page = 1
        xw_l=News.query.filter(*f).order_by(News.create_time.desc()).paginate(page=page,per_page=10)
        xws=xw_l.items
        dqy = xw_l.page
        zys = xw_l.pages
        data['xws']=xws
        data['dqy']=dqy
        data['zys']=zys

        return render_template('admin/news_review.html',data=data)
@gly.route('/sh',methods=['get','post'])
def sh():
    if request.method=="POST":
        dat=request.json
        xw_id=dat.get('news_id')
        reason=dat.get('reason')
        action=dat.get('action')
        xw = News.query.filter(News.id == xw_id).first()
        if reason!='':
            if action=="reject":
                xw.status=-1
                xw.reason=reason
        else:
            if action=="accept":
                xw.status=0
            elif action=='reject':
                xw.status=-1
        db.session.commit()
        return jsonify(errno=0,errmsg="ok")
    else:
        xw_id=request.args.get('xw_id')
        if xw_id is not None:
            xw=News.query.filter(News.id==xw_id).first()
            data={'xw':xw}
            return render_template('admin/news_review_detail.html',data=data)
@gly.route('/ss',methods=['get','post'])
def ss():
    xw_id = request.args.get('xw_id')
    if xw_id is not None:
        xw = News.query.filter(News.id == xw_id).first()
        data = {'xw': xw}
        return render_template('admin/news_review_detail.html', data=data)


@gly.route('/xwbj',methods=['get','post'])
def xwbj():
    if request.method=="POST":
        pass
    else:
        data={}
        dat = request.args
        kw=dat.get('kw')
        f=[]
        if kw:
            f.append(News.title.like('%'+kw+'%'))
            data['kw']=kw
        page = dat.get('p', 1)
        try:
            page = int(page)
        except:
            page = 1
        xw_l=News.query.filter(*f).order_by(News.create_time.desc()).paginate(page=page,per_page=10)
        xws=xw_l.items
        dqy = xw_l.page
        zys = xw_l.pages
        data['xws'] = xws
        data['dqy'] = dqy
        data['zys'] = zys
        return render_template('admin/news_edit.html',data=data)
#
@gly.route('/bj',methods=['get','post'])
def bj():
    if request.method=="POST":
        dat=request.form
        sy_img = request.files
        biaoti = dat.get('title')
        fenlei = dat.get('category')
        zhaiyao = dat.get('digest')
        neirong = dat.get('content')
        xw_id=dat.get('new_id')
        if not all([biaoti,fenlei,zhaiyao,neirong]):
            return jsonify(errno=RET.PARAMERR,errmsg='参数不全')
        new = News.query.filter(News.id == xw_id).first()
        if new is None:
            return jsonify(errno=RET.PARAMERR, errmsg='差唔次数据')
        if sy_img.__len__() == 0:
            # return jsonify(errno=RET.SESSIONERR, errmsg='没有选择头像')
            pass
        else:
            img_d = sy_img.get('index_image').read()
            img_name = storage(img_d)
            print(img_name)
            new.index_image_url = constants.QINIU_DOMIN_PREFIX + img_name


        new.title=biaoti
        new.digest=zhaiyao
        new.source = '个人'
        new.content=neirong
        new.status=1
        new.category_id = fenlei

        try:

            db.session.commit()
            fl=Category.query.filter(Category.id==int(fenlei)).first()
            fl.news_list.append(new)
            db.session.commit()
        except Exception as e:
            print(e)
        return jsonify(errno=RET.OK, errmsg='ok')

    else:
        fenleis=Category.query.filter(Category.id!=1).all()
        xw_id=request.args.get('xw_id')
        if xw_id is not None:
            xw=News.query.filter(News.id==xw_id).first()
            xw_zl=xw.category

            data={'xw':xw,'fenleis':fenleis,'xw_zl':xw_zl}
            return render_template('admin/news_edit_detail.html',data=data)
@gly.route('/xwfl',methods=['get','post'])
def xwfl():
    if request.method=="POST":
        dat=request.json
        name=dat.get('name')
        id=dat.get('id')
        if name is None:
            return jsonify(errno=RET.PARAMERR,errmsg='参数缺少')
        if id is None:
            fl = Category.query.filter(Category.name == name).first()
            if fl is not None:
                return jsonify(errno=RET.PARAMERR, errmsg='已经有了此分类')
            fl = Category()
            fl.name = name
            db.session.add(fl)
        else:
            fl = Category.query.filter(Category.id == id).first()
            if fl is None:
                return jsonify(errno=RET.PARAMERR, errmsg='没有此分类')
            fl.name = name
        db.session.commit()
        return jsonify(errno=0,errmsg='ok')
    else:
        fenleis = Category.query.filter(Category.id != 1).all()
        data={"fenleis":fenleis}
        return render_template('admin/news_type.html',data=data)