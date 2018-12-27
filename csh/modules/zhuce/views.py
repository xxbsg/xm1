from datetime import datetime
import re

from flask import make_response, jsonify
from flask import redirect
from flask import request
from random import randint

from flask import session
from flask import url_for

from csh import rs, db
from csh.disanfang.captcha.captcha import captcha
from csh.disanfang.yuntongxun.sms import CCP
from csh.models import User
from csh.modules.zhuce import zc
from csh.response_code import RET


@zc.route('/image_code')
def get_tu_code():
    # 接受图片的id
    code_id=request.args.get('code_id')
    tu_name,tu_neirong,tu_shuju=captcha.generate_captcha()
    # 存储图片id和内容  用作判断
    try:
        rs.setex(code_id,60,tu_neirong)
    except Exception as e:
        return jsonify(errcod=RET.DATAERR,erromsg='存储错误---redis')
    # 返回图片
    resp=make_response(tu_shuju)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp
@zc.route('/fsyzm',methods=['POST'])
def fsyzma():
    data = request.json
    print(data)
    code_id=data.get('image_code_id')
    mobile=data.get('mobile')
    image_nr=data.get("image_code").lower()
    if not all([code_id,mobile,image_nr]):
        return jsonify(errno=RET.DATAERR,errmsg="参数有空")
    if not re.match('1\d{10}',mobile):
        return jsonify(errno=RET.DATAERR,errmsg="手机输入有误")
    if not rs.get(code_id):
        return jsonify(errno=RET.DATAERR,errmsg="验证码超时请重新获取")
    if not rs.get(code_id).decode().lower()==image_nr:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")
    ccp = CCP()
    # 注意： 测试的短信模板编号为1
    sjm='%06d'%randint(0,999999)
    print(sjm)
    # 发送短信
    # a=ccp.send_template_sms('15733151213', [str(sjm), 5], 1)
    a=0
    if a== (-1):
        return jsonify(errno=RET.DATAERR, errmsg="短信发送失败请检查")
    try:
        rs.setex(mobile,300,sjm)
    except Exception as e:
        return jsonify(errno=RET.DATAERR, errmsg="存储失败")
    # print(neirong,image_nr)
    # # print(request.json)
    # ccp = CCP()
    # # 注意： 测试的短信模板编号为1
    # sjm='%06d'%randint(0,999999)
    # # a=ccp.send_template_sms('15733151213', [str(sjm)2, 5], 1)
    return jsonify(errno=RET.OK,errmsg='ok')

@zc.route("/login",methods=["POST"])
def login():
    # json返回手机号 短信验证码 密码
    data=request.json
    print(data)
    mobile=data.get('mobile')
    yzm=data.get('syzm')
    password=data.get('password')
    if not all([mobile,yzm,password]):
        return jsonify(errno=RET.DATAERR,errmsg="参数有空")
    yzm_r=rs.get(mobile)
    if not yzm_r:
        return jsonify(errno=RET.DATAERR,errmsg='验证码不存在')
    if yzm_r.decode() != yzm:
        return jsonify(errno=RET.DATAERR,errmsg="验证码不正确")
    rs.delete(mobile)
    user=User()
    user.mobile=mobile
    user.password=password
    # user.is_admin=1 管理员
    user.nick_name='用户'+mobile
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # return jsonify(errno=RET.DATAERR,errmsg='数据库mysql错误')
    # 保存登陆状态
    session['user_id']=user.id
    session["user_mobile"]=user.mobile
    session['user_nc']=user.nick_name
    return jsonify(errno=RET.OK,errmsg='ok')
@zc.route('/signin',methods=["POST"])
def signin():
    # print("这是form",request.form)
    # print("这是json",request.json)
    # 接受返回的json信息 手机号 密码
    data=request.json
    mobile=data.get('mobile')
    password=data.get('password')
    if not all([mobile,password]):
        return jsonify(errno=RET.DATAERR,errmsg='参数有空值')
    user=User.query.filter(User.mobile==mobile).first()
    if not user:
        return jsonify(errno=RET.NODATA,errmsg='用户不存在不存在')
    if not user.check_passowrd(password):
        return jsonify(errno=RET.DATAERR,errmsg="用户名或密码错误")
    session['user_id'] = user.id
    session["user_mobile"] = user.mobile
    session['user_nc'] = user.nick_name
    user.last_login=datetime.now()
    db.session.commit()
    return jsonify(errno=RET.OK,errmsg='ok')
@zc.route('/logout')
def logout():
    session.pop('user_id',None)
    session.pop('user_mobile',None)
    session.pop('user_nc',None)
    print(session.get('user_id'),session.get('user_mobile'),session.get('user_id'))
    return jsonify(errno=0,errmsg='ok')
