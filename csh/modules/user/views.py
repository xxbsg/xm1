from flask import g, jsonify
from flask import render_template
from flask import request

from csh import db
from csh.disanfang.gongyong import user_pd
from csh.models import User
from csh.modules.user import user
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
    if user is  None:
        data['nc']=''
        if method == 'POST':
            return jsonify(errno=RET.SESSIONERR,errmsg='用户未登陆')
    if method == 'POST':
        dat=request.json
        gxqianming=dat.get('new_gxqm','')
        nc=dat.get("new_nc")
        gender=dat.get('gender')
        if not all([nc,gender]):
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        user.nick_name=nc
        user.gender=gender
        user.signature=gxqianming
        db.session.commit()
        return jsonify(errno=RET.OK, errmsg='ok')
    data['nc']=user.nick_name



    return render_template('news/user_base_info.html',data=data)