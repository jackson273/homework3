import json
import time, os
import config

from flask import Flask, render_template, request, send_from_directory, redirect, flash, make_response
from flask.helpers import url_for
from werkzeug.utils import secure_filename

from utilities.auth import User, login_required, is_authenticated, allowed_file
from utilities import bot


app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
IMAGES_ROOT = config.IMAGES_ROOT

# ----------------------------Routes------------------------------------ #

@app.route('/profile/', methods=['GET'])
@login_required
def profile():
    username = request.cookies.get('username', '')
    user_query = User.filter(username=username)
    user = user_query[0]
    return render_template('profile.html', username=username, imageURL=user.imageURL)

@app.route('/', methods=['GET'])
def index():
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
    flash('Logout successfully!', 'message')
    return redirect(url_for('login'))

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

@app.route('/edit-pwd/', methods=['GET', 'POST'])
@login_required
def edit_password():
    if request.method == 'POST':
        username = request.cookies.get('username')
        password_old = request.form.get('password_old', '')
        password_new = request.form.get('password_new', '')
        password_confirm = request.form.get('password_confirm', '')
        user = User.filter(username=username)[0]
        if not user.authenticate(password_old):
            flash('Old password is incorrect', 'error')
        elif password_new != password_confirm:
            flash('New password is incorrect!', 'error')
        else:
            user.edit_pwd(password_new)
            flash('Change password successfully', 'message')
            return redirect(url_for('login'))
    
    return render_template('edit_password.html')

@app.route('/edit-profile-pic/', methods=['GET', 'POST'])
@login_required
def upload_file():
    user = User.filter(username=request.cookies.get('username', ''))[0]
    if request.method == 'POST':
        # check if the post request has the file part
        if 'image' in request.files: 
            image = request.files['image']
            # If the user does not select a file, the browser submits an empty file without a filename.
            if image.filename:
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    new_imageURL = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(new_imageURL)
                    user.imageURL =  f"{IMAGES_ROOT}{filename}" 
                    user.save()
                    flash('Changed image successfully!!!')
                    return redirect(url_for('image_file', filename=filename))
                    #return redirect(url_for('upload_file'))
                else:
                    flash('Not supported image', 'error')
            else:
                flash('No selected image', 'error')
        else:
            flash('No image part', 'error')

    return render_template('edit_profile_pic.html', user_imageURL=user.imageURL)

@app.route('/upload/<path:filename>')
def image_file(filename):
    return send_from_directory(config.UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    print('Server started!')
    app.run("localhost", 5000, debug=True)