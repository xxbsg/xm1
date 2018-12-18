from flask import current_app
from flask import redirect
from flask import render_template
from flask import url_for

from csh.modules.index import index_blu


@index_blu.route('/')
def hello_world():
    current_app.logger.debug('debug')
    current_app.logger.error('error')
    # print(current_app.permanent_session_lifetime)
    print(current_app.url_map)
    return render_template('news/index.html')
@index_blu.route('/favicon.ico')
def tubiao():
    # return current_app.send_static_file('news/favicon.ico')
    return redirect(url_for('static',filename='news/favicon.ico'))