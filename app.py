from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import sys

# Конфигурация
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///lr_queue.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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

@app.route('/queue', methods=['GET', 'POST'])
def queue():
    if request.method == 'POST':
        table_name = request.form['table_name']
        new_table = QueueTable(name=table_name)
        db.session.add(new_table)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('queue.html')

@app.route('/make/<int:table_id>', methods=['GET', 'POST'])
def make(table_id):
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
    table = QueueTable.query.get_or_404(table_id)
    QueueEntry.query.filter_by(table_id=table.id).delete()
    db.session.delete(table)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
