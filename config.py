import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Загружаем секретный ключ из переменных окружения
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Путь к базе данных
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    
    # Настройки админ-панели
    FLASK_ADMIN_SWATCH = 'cerulean'
    
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY')
    HOST = '0.0.0.0'
    PORT = 5000
