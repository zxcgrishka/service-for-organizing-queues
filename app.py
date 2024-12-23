from flask import Flask, render_template, request, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime

# Конфигурация
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///lr_queue.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'supersecretkey'

# Инициализация приложения
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

# Модели
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class QueueTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    entries = db.relationship('QueueEntry', backref='table', lazy=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class QueueEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('queue_table.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Маршруты
@app.route('/')
def index():
    tables = QueueTable.query.order_by(QueueTable.date.desc()).all()
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
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return 'Неверные данные'

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/search', methods=['GET'])
def search():
    searching_table = request.args.get('searching_table')
    results = []
    if searching_table:
        results = QueueTable.query.filter(QueueTable.name.ilike(f'%{searching_table}%')).all()
    return render_template('index.html', searching_table=searching_table, results=results)


@app.route('/queue', methods=['GET', 'POST'])
@login_required
def queue():
    if request.method == 'POST':
        table_name = request.form['table_name']
        new_table = QueueTable(name=table_name)
        db.session.add(new_table)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('queue.html')


@app.route('/make/<int:table_id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def delete_table(table_id):
    table = QueueTable.query.get_or_404(table_id)
    QueueEntry.query.filter_by(table_id=table.id).delete()
    db.session.delete(table)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)