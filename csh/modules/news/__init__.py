from  flask import Blueprint
news=Blueprint('news',__name__,url_prefix='/news')
from . import views