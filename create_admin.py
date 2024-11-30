from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Удаляем все существующие таблицы
        db.drop_all()
        
        # Создаем таблицы заново
        db.create_all()
        
        # Создаем администратора
        admin = User(
            username='123',
            is_admin=True
        )
        admin.set_password('123')
        
        db.session.add(admin)
        db.session.commit()
        
        print('База данных инициализирована. Создан пользователь admin с паролем admin') 