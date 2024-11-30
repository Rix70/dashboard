from flask import Flask, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from flask_bcrypt import Bcrypt

# Создаем объекты расширений без инициализации
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    # Конфигурация приложения
    app.config.from_object(Config)
    csrf = CSRFProtect(app)

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Настройка login_manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    login_manager.login_message_category = 'warning'
    
    # Импорт и регистрация blueprints
    from app.routes import main
    from app.login_route import auth
    from app.chart_route import chart
    from app.shfts import shifts
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(chart)
    app.register_blueprint(shifts)
    
    # Настройка загрузчика пользователя
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Инициализация админки
    from app.admin_views import init_admin
    init_admin(app)
    
    return app