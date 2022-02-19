import os
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = 'static/uploads/'
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

print(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT*FROM posts WHERE id =?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close
    print(session.get('user'))
    return render_template('index.html', posts=posts, user=session.get('user'))


@app.route('/bloglist')
def blogList():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close
    print(session.get('user'))
    return render_template('index.html', posts=posts, user=session.get('user'))


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('blog-post.html', post=post, user=session.get('user'))


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        caption = request.form['caption']
        author = request.form['author']

        if not title:
            flash('Title is required!')
        elif 'file' not in request.files:
            flash(request.files)
        elif not caption:
            flash('Summary is missing')
        elif not author:
            flash('Author is missing')
        else:
            file = request.files['file']

            if file.filename == '':
                flash('No selected file')
            elif file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                uploadFileName = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(uploadFileName)
                conn = get_db_connection()
                conn.execute('INSERT INTO posts (title, content, caption, author, image_url ) VALUES (?,?,?,?,?)',
                             (title, content, caption, author, filename))
                conn.commit()
                conn.close()
                return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


@app.route('/signin', methods=('GET', 'POST'))
def signIn():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']

        conn = get_db_connection()
        users = conn.execute('SELECT * FROM users WHERE email = ?',
                             [email]).fetchall()
        conn.commit()
        conn.close()

        if len(users) > 0:
            user = users[0]
            if check_password_hash(user['user_password'], password):
                session['user'] = user['user_name']
                redirect(url_for('index'))
            else:
                flash("password is wrong")
        else:
            flash('User not exist')

    if session.get('user'):
        return redirect(url_for('index'))
    else:
        return render_template('signin.html')


@app.route('/signup', methods=('GET', 'POST'))
def signUp():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        re_pass = request.form['re_pass']

        print(name, email, password)
        _hashedPass = generate_password_hash(password)
        if password != re_pass:
            flash("Password is no match")
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (user_name, email, user_password) VALUES (?,?,?)',
                         (name, email, _hashedPass))
            conn.commit()
            conn.close()
            return redirect(url_for('signIn'))

    if session.get('user'):
        return redirect(url_for('index'))
    else:
        return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html', user=session.get('user'))
