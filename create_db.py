from app import db, app
from app.models import Parameters, HourlyValues
from datetime import datetime, timedelta
import random
from sqlalchemy import text
from app import create_app, db
app = create_app()

def create_database():
    with app.app_context():
        db.create_all()
        print("База данных успешно создана!")

def generate_values(parameters, start_date, end_date):
    values = []
    current_date = start_date
    
    while current_date <= end_date:
        for param in parameters:
            # Генерируем случайные значения в зависимости от типа параметра
            if param.CodeId == 1:  # Температура воды
                value = random.uniform(60, 90)
            elif param.CodeId == 2:  # Давление
                value = random.uniform(5, 8)
            elif param.CodeId == 3:  # Расход газа
                value = random.uniform(1000, 2000)
            elif param.CodeId == 4:  # КПД
                value = random.uniform(85, 95)
            elif param.CodeId == 5:  # Температура воздуха
                value = random.uniform(-10, 25)
            elif param.CodeId == 6:  # Уровень CO2
                value = random.uniform(0, 10)
            elif param.CodeId == 7:  # Уровень CO
                value = random.uniform(0, 100)
            elif param.CodeId == 8:  # Уровень NOx
                value = random.uniform(0, 200)
            elif param.CodeId == 9:  # Расход воздуха
                value = random.uniform(500, 1500)
            elif param.CodeId == 10:  # Температура дымовых газов
                value = random.uniform(150, 250)
            elif param.CodeId == 11:  # Давление в топке
                value = random.uniform(-50, 50)
            elif param.CodeId == 12:  # Температура питательной воды
                value = random.uniform(20, 40)
            elif param.CodeId == 13:  # Расход питательной воды
                value = random.uniform(100, 300)
            elif param.CodeId == 14:  # Мощность котла
                value = random.uniform(200, 480)
            elif param.CodeId == 15:  # Содержание O2
                value = random.uniform(0, 21)
            elif param.CodeId == 16:  # Температура пара
                value = random.uniform(150, 250)
            elif param.CodeId == 17:  # Давление пара
                value = random.uniform(10, 20)
            elif param.CodeId == 18:  # Расход пара
                value = random.uniform(5, 15)
            elif param.CodeId == 19:  # Температура уходящих газов
                value = random.uniform(100, 200)
            elif param.CodeId == 20:  # Влажность воздуха
                value = random.uniform(30, 70)
            
            values.append(HourlyValues(
                CodeId=param.CodeId,
                DateTime=current_date,
                Value=round(value, 2)
            ))
        
        current_date += timedelta(hours=1)
        
        # Записываем данные пакетами по 1000 записей
        if len(values) >= 1000:
            db.session.add_all(values)
            db.session.commit()
            values = []
    
    # Записываем оставшиеся данные
    if values:
        db.session.add_all(values)
        db.session.commit()

def populate_test_data():
    with app.app_context():
        # Проверяем, есть ли уже данные в таблице Parameters
        if Parameters.query.first() is None:
            # Создаем тестовые параметры
            parameters = [
                Parameters(CodeId=1, Name='Температура воды'),
                Parameters(CodeId=2, Name='Давление'),
                Parameters(CodeId=3, Name='Расход газа'), 
                Parameters(CodeId=4, Name='КПД котла'),
                Parameters(CodeId=5, Name='Температура воздуха'),
                Parameters(CodeId=6, Name='Уровень CO2'),
                Parameters(CodeId=7, Name='Уровень CO'),
                Parameters(CodeId=8, Name='Уровень NOx'),
                Parameters(CodeId=9, Name='Расход воздуха'),
                Parameters(CodeId=10, Name='Температура дымовых газов'),
                Parameters(CodeId=11, Name='Давление в топке'),
                Parameters(CodeId=12, Name='Температура питательной воды'),
                Parameters(CodeId=13, Name='Расход питательной воды'),
                Parameters(CodeId=14, Name='Мощность котла'),
                Parameters(CodeId=15, Name='Содержание O2'),
                Parameters(CodeId=16, Name='Температура пара'),
                Parameters(CodeId=17, Name='Давление пара'),
                Parameters(CodeId=18, Name='Расход пара'),
                Parameters(CodeId=19, Name='Температура уходящих газов'),
                Parameters(CodeId=20, Name='Влажность воздуха')
            ]
            db.session.add_all(parameters)
            db.session.commit()
            
            # Создаем тестовые часовые данные
            start_date = datetime(2024, 11, 1)
            end_date = datetime(2024, 12, 1)
            
            generate_values(parameters, start_date, end_date)
            
            print("База данных успешно заполнена тестовыми данными!")
        else:
            print("Тестовые данные уже существуют в базе данных!")

def add_period_data(start_date, end_date):
    """
    Добавляет данные за указанный период
    :param start_date: datetime, начальная дата
    :param end_date: datetime, конечная дата
    """
    with app.app_context():
        parameters = Parameters.query.all()
        if not parameters:
            print("Ошибка: параметры не найдены в базе данных!")
            return
            
        # Проверяем наличие данных за указанный период
        existing_data = HourlyValues.query.filter(
            HourlyValues.DateTime.between(start_date, end_date)
        ).first()
        
        if existing_data:
            print(f"За период с {start_date} по {end_date} уже существуют данные!")
            return
            
        generate_values(parameters, start_date, end_date)
        print(f"Данные за период с {start_date} по {end_date} успешно добавлены!")

def upgrade(query='ALTER TABLE parameters ADD COLUMN weight_parameter_id INTEGER'):
    # Добавляем колонку aggregation_type, если её нет
    with app.app_context():
        try:
            #db.session.execute(text('ALTER TABLE parameters ADD COLUMN aggregation_type VARCHAR(20) DEFAULT "avg"'))
            db.session.execute(text(query))
            db.session.commit()
            print("Колонка weight_parameter_id успешно добавлена")
        except Exception as e:
            print(f"Ошибка при добавлении колонки: {e}")
            db.session.rollback()
        
def downgrade(query='ALTER TABLE parameters DROP COLUMN weight_parameter_id'):
    # Удаляем колонку aggregation_type, если она существует
    with app.app_context():
        try:    
            #db.session.execute(text('ALTER TABLE parameters DROP COLUMN aggregation_type'))
            db.session.execute(text(query))
            db.session.commit()
            print("Колонка weight_parameter_id успешно удалена")
        except Exception as e:
            print(f"Ошибка при удалении колонки: {e}")
            db.session.rollback()   

if __name__ == "__main__":
    #create_database()
    #populate_test_data()
    upgrade('ALTER TABLE parameters ADD COLUMN weight_parameter_id INTEGER')
    # Пример добавления данных за другой период:
    # start = datetime(2024, 11, 1)
    # end = datetime(2024, 11, 30)
    # add_period_data(start, end)