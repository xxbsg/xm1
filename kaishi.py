from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager

from csh import *


app,db=creat_app(ms="ts")
print(app.debug)
manager=Manager(app=app)
Migrate(app=app,db=db)
manager.add_command('db',MigrateCommand)
from csh.modules.index import index_blu
app.register_blueprint(index_blu)
from csh.modules.zhuce import zc
app.register_blueprint(zc)
from csh.modules.news import news
app.register_blueprint(news)
print(app.url_map)
if __name__ == '__main__':
    # db.create_all()
    manager.run()