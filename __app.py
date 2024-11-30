from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.models import db, User, bcrypt
from app.admin_views import init_admin
from flask_wtf.csrf import CSRFProtect

from datetime import datetime
import pytz
app = Flask(__name__)
app.config.from_object('config.Config')
csrf = CSRFProtect(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Инициализация админ-панели
admin = init_admin(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверное имя пользователя или пароль')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash('Это имя пользователя уже занято')
            return redirect(url_for('register'))
        
        user = User(
            username=request.form['username']
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('register.html')

def convert_time(date):
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    moscow_tz = pytz.timezone('Europe/Moscow')
    return dt.astimezone(moscow_tz)

@app.route('/update_dates', methods=['POST'])
def update_dates():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
        
        # Конвертируем в московское время
        start_date = convert_time(start_date)
        end_date = convert_time(end_date)
        
        # Сохраняем даты в сессию
        session['start_date'] = start_date
        session['end_date'] = end_date
        
        # Возвращаемся на предыдущую страницу
        return redirect(request.referrer or url_for('index'))
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
