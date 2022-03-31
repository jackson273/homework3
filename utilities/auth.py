import config
from utilities.models import User
from functools import wraps
from flask import flash, redirect, url_for, request

def is_authenticated(request):
    '''Check username, token in database'''
    username = request.cookies.get('username', '')
    token = request.cookies.get('token', '')
    if token:
        try:
            user = User.filter(username=username)[0]
            return user.token == token
        except:
            pass
    return False

def login_required(func):
    @wraps(func)
    def vertify(*args, **kwargs):
        if is_authenticated(request):
            return func(*args, **kwargs)
        else:
            flash('Please login now!','error')
            return redirect(url_for('login'))
    return vertify

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS