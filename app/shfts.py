from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session, send_file, flash
from app.models import Parameters, HourlyValues, PageSettings, User, PageHierarchy
from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from io import BytesIO
from sqlalchemy import func, case, and_
import pytz
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db

# Создаем Blueprint
shifts = Blueprint('shifts', __name__)

def get_shift_for_datetime(target_date):
    """Определяет какая смена работает в заданное время"""
    base_date = datetime(2024, 11, 1)  # Опорная дата
    days_diff = (target_date.date() - base_date.date()).days
    
    # Начальное состояние смен на 01.11.2024
    initial_state = {
        'Г': 0,  # дневная смена
        'А': 1,  # ночная 2
        'В': 3,  # выходной
        'Б': 2   # отсыпной(ночная 1)
    }
    
    hour = target_date.hour
    is_day_shift = 8 <= hour < 20
    is_night1_shift = 0 <= hour < 8
    is_night2_shift = 20 <= hour <= 23

    for shift_letter, initial_pos in initial_state.items():
        current_pos = (initial_pos + days_diff) % 4
        if current_pos == 0 and is_day_shift:  # Дневная смена
            return shift_letter
        elif current_pos == 1 and is_night2_shift:  # Ночная смена
            return shift_letter
        elif current_pos == 2 and is_night1_shift:  # Отсыпной
            return shift_letter

            
    return None

@shifts.route('/sore', methods=['GET', 'POST'])
@login_required
def sore():
    # Получаем все параметры для выпадающего списка
    parameters = Parameters.query.all()
    
    # Получаем выбранный параметр из сессии или используем параметр 1 по умолчанию
    selected_parameter_id = session.get('selected_parameter_id', 1)
    
    # Получаем даты из сессии или используем текущую дату
    end_date = session.get('end_date')
    start_date = session.get('start_date')
    
    # Если даты пришли как строки, преобразуем их
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S%z')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S%z')
    
    # Получаем параметр и его тип агрегации
    selected_parameter = Parameters.query.get(selected_parameter_id)
    
    if selected_parameter.aggregation_type == 'weighted_avg' and selected_parameter.weight_parameter_id:
        # Создаем подзапрос для весовых значений
        weight_values = db.session.query(
            HourlyValues.DateTime,
            HourlyValues.Value.label('weight_value')
        ).filter(
            HourlyValues.CodeId == selected_parameter.weight_parameter_id,
            HourlyValues.DateTime.between(start_date, end_date),
            HourlyValues.Value != 0  # Исключаем нулевые веса
        ).subquery()

        # Запрос для средневзвешенного значения
        shift_data = db.session.query(
            case(
                (func.sum(weight_values.c.weight_value) == 0, None),
                else_=(func.sum(HourlyValues.Value * weight_values.c.weight_value) / 
                      func.sum(weight_values.c.weight_value))
            ).label('total_value'),
            func.date(HourlyValues.DateTime).label('date'),
            func.extract('hour', HourlyValues.DateTime).label('hour')
        ).join(
            weight_values,
            HourlyValues.DateTime == weight_values.c.DateTime
        ).filter(
            and_(
                HourlyValues.DateTime.between(start_date, end_date),
                HourlyValues.CodeId == selected_parameter_id
            )
        ).group_by(
            func.date(HourlyValues.DateTime),
            func.extract('hour', HourlyValues.DateTime)
        ).all()
    else:
        # Запрос с учетом типа агрегации
        shift_data = db.session.query(
            case(
                (selected_parameter.aggregation_type == 'sum', func.sum(HourlyValues.Value)),
                (selected_parameter.aggregation_type == 'min', func.min(HourlyValues.Value)),
                (selected_parameter.aggregation_type == 'max', func.max(HourlyValues.Value)),
                else_=func.avg(HourlyValues.Value)
            ).label('total_value'),
            func.date(HourlyValues.DateTime).label('date'),
            func.extract('hour', HourlyValues.DateTime).label('hour')
        ).filter(
            and_(
                HourlyValues.DateTime.between(start_date, end_date),
                HourlyValues.CodeId == selected_parameter_id
            )
        ).group_by(
            func.date(HourlyValues.DateTime),
            func.extract('hour', HourlyValues.DateTime)
        ).all()

    # Агрегируем данные по сменам
    shift_totals = {'А': 0, 'Б': 0, 'В': 0, 'Г': 0}
    shift_counts = {'А': 0, 'Б': 0, 'В': 0, 'Г': 0}  # Для подсчета количества значений
    
    for value, date, hour in shift_data:
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        
        dt = datetime.combine(date, datetime.min.time().replace(hour=int(hour)))
        shift = get_shift_for_datetime(dt)
        
        if shift and value is not None:
            if selected_parameter.aggregation_type in ['sum', 'weighted_avg']:
                shift_totals[shift] += value
            elif selected_parameter.aggregation_type == 'min':
                if shift_counts[shift] == 0 or value < shift_totals[shift]:
                    shift_totals[shift] = value
            elif selected_parameter.aggregation_type == 'max':
                if shift_counts[shift] == 0 or value > shift_totals[shift]:
                    shift_totals[shift] = value
            else:  # avg
                shift_totals[shift] += value
            shift_counts[shift] += 1
    
    # Вычисляем среднее значение для avg
    if selected_parameter.aggregation_type == 'avg':
        for shift in shift_totals:
            if shift_counts[shift] > 0:
                shift_totals[shift] /= shift_counts[shift]

    pages = PageSettings.query.all()
    
    # Добавляем получение данных о сменах за период
    shift_schedule = []
    current_date = start_date
    while current_date <= end_date:
        for hour in range(24):
            current_datetime = current_date.replace(hour=hour)
            shift = get_shift_for_datetime(current_datetime)
            
            shift_schedule.append({
                'datetime': current_datetime,
                'date': current_datetime.date(),
                'hour': hour,
                'shift': shift
            })
        current_date += timedelta(days=1)

    return render_template('sore.html',
                         shift_totals=shift_totals,
                         shift_schedule=shift_schedule,
                         pages=pages,
                         start_date=start_date,
                         end_date=end_date,
                         parameters=parameters,
                         selected_parameter=selected_parameter,
                         selected_parameter_id=selected_parameter_id)