
from flask import Blueprint

index_blu=Blueprint('index',__name__,template_folder='templates')
from . import views
