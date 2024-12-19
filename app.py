from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import os
import sys

# Конфигурация
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///lr_queue.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'supersecretkey'

# Инициализация приложения
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

# Модели
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class QueueTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    entries = db.relationship('QueueEntry', backref='table', lazy=True)

class QueueEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('queue_table.id'), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.Integer, nullable=False)

# Маршруты
@app.route('/')
def index():
    tables = QueueTable.query.all()
    return render_template('index.html', tables=tables)


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        email = request.form['email']

        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials'

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/queue', methods=['GET', 'POST'])
def queue():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        table_name = request.form['table_name']
        new_table = QueueTable(name=table_name)
        db.session.add(new_table)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('queue.html')


@app.route('/make/<int:table_id>', methods=['GET', 'POST'])
def make(table_id):
    if 'user_id' not in session:
        return redirect (url_for('login'))
    
    table = QueueTable.query.get_or_404(table_id)
    if request.method == 'POST':
        name = request.form['name']
        new_entry = QueueEntry(name=name, table_id=table_id)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('make', table_id=table_id))
    entries = QueueEntry.query.filter_by(table_id=table_id).all()
    return render_template('make.html', table=table, entries=entries)


@app.route('/delete/<int:table_id>', methods=['POST'])
def delete_table(table_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    table = QueueTable.query.get_or_404(table_id)
    QueueEntry.query.filter_by(table_id=table.id).delete()
    db.session.delete(table)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)