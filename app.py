import json
import time, os
import config

from flask import Flask, render_template, request, send_from_directory, redirect, flash, make_response, jsonify
from flask.helpers import url_for
from werkzeug.utils import secure_filename

from utilities.auth import User, login_required, is_authenticated, allowed_file
from utilities import bot


app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
IMAGES_ROOT = config.IMAGES_ROOT

# ----------------------------Routes------------------------------------ #

@app.route('/index/', methods=['GET'])
def profile():
    username = request.cookies.get('username', '')
    user_query = User.filter(username=username)
    if user_query:
        user = user_query[0]
    else:
        user = None
    posts = User.get_all_posts_of_user()
    return render_template('index.html', user=user, posts=posts)

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('profile'))

@app.route('/create-post/', methods=['POST'])
@login_required
def create_post():
    title = request.form.get('title', '')
    text = request.form.get('text', '')
    username = request.cookies.get('username', '')
    user_query = User.filter(username=username)
    if 'image' in request.files: 
        image = request.files['image']
        if image and allowed_file(image.filename):
            if user_query:
                user = user_query[0]
                filename = secure_filename(image.filename)
                imageURL = os.path.join(config.IMAGES_ROOT, filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.create_post(title, text, imageURL)
                user.save()
                flash('Created successfully!!!', 'message')
                return redirect(url_for('profile'))

    flash('Error when trying create your post!!!', 'error')
    return redirect(url_for('profile'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if is_authenticated(request):
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user_query = User.filter(username=username)
        if user_query:
            user = user_query[0]
            if user.authenticate(password):
                session_token = user.init_session()
                response = make_response(redirect(url_for('index')))
                response.set_cookie(key='username',value=username)
                response.set_cookie(key='token',value=session_token)
                return response
            else:
                flash('Username or password is invalid', 'error')
        else:
            flash('Username or password is invalid!', 'error')

    return render_template('login.html')

@app.route('/logout/')
@login_required
def logout():
    username = request.cookies.get('username', '')
    User.filter(username=username)[0].terminate_session()
    response = make_response(redirect(url_for('login')))
    response.set_cookie(key='username',value='')
    response.set_cookie(key='token',value='')
    flash('Logout successfully!', 'message')
    return response

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if is_authenticated(request):
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        if password != password_confirm:
            flash('Re-enter password is incorrect!', 'error')
        elif User.filter(username=username):
            flash('This username is already existed!', 'error')
        else:
            User.create(username, password)
            flash('Register successfully', 'message')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/upload/<path:filename>')
def image_file(filename):
    return send_from_directory(config.UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    print('Server started!')
    app.run("localhost", 5000, debug=True)