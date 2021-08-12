from flask import *
from flask_mail import *
from random import *
import requests
import json
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_uploads import UploadSet, configure_uploads, IMAGES
import timeit
import datetime
import os
from wtforms.fields.html5 import EmailField

app = Flask(__name__)
app.secret_key = os.urandom(24)


# Config MySQL
mysql = MySQL()
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'todo'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize the app for use with this MySQL class
mysql.init_app(app)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('login'))

    return wrap


def not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('index'))
        else:
            return f(*args, *kwargs)

    return wrap

# Home page
@app.route('/')
@is_logged_in
def index():
    uid = session['uid']
    cur = mysql.connection.cursor()
    # Get user by username
    result = cur.execute(
        "SELECT * FROM todo WHERE t_id=%s", [uid])
    product = cur.fetchall()

    if result > 0:
        flash(f"You have {result} list in your todo ", 'success')
    else:
        flash("Create Your First ToDO List", 'success')
    mysql.connection.commit()
    cur.close()

    return render_template('index.html', product=product)


@app.route('/login', methods=['GET', 'POST'])
@not_logged_in
def login():
    if request.method == 'POST':
        # GEt user form
        email = request.form['email']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE email=%s", [email])

        if result > 0:
            # Get stored value
            data = cur.fetchone()
            uid = data['id']
            name = data['name']
            # creating session
            session['logged_in'] = True
            session['uid'] = uid
            session['name'] = name
            return redirect(url_for('index'))
        else:
            flash(
                '''It's looked like you are not used app before, add your name to continue..''', 'danger')
            return redirect(url_for('register'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        # GEt user form
        email = request.form['Email']
        name = request.form['name']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("INSERT INTO users(name, email)"
                             "VALUES(%s, %s)",
                             (name, email))
        flash('''login successfully ''', 'success')

        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/out')
def logout():
    if 'logged_in' in session:
        session.clear()
        return redirect(url_for('login'))
    return redirect(url_for('index'))

# # Add_Task


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if 'uid' in session:
        uid = session['uid']
        if request.method == 'POST':
            task_name = request.form['heading']
            notes = request.form['description']
            # Create cursor
            cur = mysql.connection.cursor()

            # Get user by username
            result = cur.execute("INSERT INTO todo(task_name, notes, t_id)"
                                 "VALUES(%s, %s, %s)",
                                 (task_name, notes, uid))
            mysql.connection.commit()
            cur.close()
            flash("added successfully", "success")
            return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/Task_delete', methods=['GET', 'POST'])
@is_logged_in
def delete():
    if 'id' in request.args:
        task_id = request.args['id']
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE FROM todo WHERE  id=%s", (task_id,))
        id = cur.fetchall()

        cur.close()
        flash("Task Deleted Successfully", 'success')
        return redirect('/')


@app.route('/Task_update', methods=['GET', 'POST'])
@is_logged_in
def update():
    if 'id' in request.args:
        task_id = request.args['id']
        curso = mysql.connection.cursor()
        res = curso.execute(
            "SELECT * FROM todo WHERE id=%s", (task_id,))
        product = curso.fetchall()
        if res:

            if request.method == 'POST':
                task_name = request.form['heading_updated']
                notes = request.form['description_updated']
                # Create cursor
                cur = mysql.connection.cursor()

                # Get user by username
                result = cur.execute("UPDATE todo SET task_name=%s, notes=%s WHERE id=%s",
                                     (task_name, notes, task_id))
                mysql.connection.commit()
                cur.close()
                flash("successfully Updated", "success")
                return redirect('/')
            else:
                flash(f"You are updating task_id {task_id}", 'success')
                return render_template('update.html', product=product)
        else:
            flash('went wrong', 'danger')
            return render_template('update.html', product=product)
    flash('dander')
    return redirect('/')


@app.route('/status')
@is_logged_in
def status():
    if 'id' in request.args:
        task_id = request.args['id']
        curso = mysql.connection.cursor()
        res = curso.execute(
            "SELECT * FROM todo WHERE id=%s", (task_id,))
        # Get stored value
        data = curso.fetchone()
        status = data['status']

        if status == 'Active':
            status_1 = 'Complete'
            curso.execute("UPDATE todo SET status=%s WHERE id=%s",
                          (status_1, task_id))

            return redirect('/')
        else:
            status_2 = 'Active'
            curso.execute("UPDATE todo SET status=%s WHERE id=%s",
                          (status_2, task_id))

            return redirect('/')
    flash('ff')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
