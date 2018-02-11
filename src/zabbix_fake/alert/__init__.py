'''
import all commands from management scripts
'''


import os
from flask import Blueprint

# static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')

# template_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'html')

# alert = Blueprint('alert', __name__, template_folder=template_folder, static_url_path='/static', static_folder=static_folder)

alert = Blueprint('alert', __name__)
from urls import *
