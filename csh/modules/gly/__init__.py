from flask import Blueprint
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from csh.disanfang.gongyong import user_pd
from csh.models import User

gly=Blueprint('admin',__name__,url_prefix='/admin')
from . import views
@gly.before_request

def pdgly():
    a=request.url
    if not a.endswith('login'):
        user_id=session.get('user_id')
        user=User.query.filter(User.id==user_id).first()
        if user is None:
            return redirect(url_for('admin.login'))
        if not user.is_admin:
            return redirect(url_for('admin.login'))