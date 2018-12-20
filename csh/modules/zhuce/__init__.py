from flask import Blueprint

zc=Blueprint('zhuce',__name__,url_prefix='/zhuce')
from . import views