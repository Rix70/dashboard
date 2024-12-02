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
    """
    Определяет какая смена работает в заданное время
    
    Args:
        target_date (datetime): Дата и время для определения смены
        
    Returns:
        str: Буква смены (А, Б, В или Г) или None если смена не определена
    """
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
    """
    Отображает страницу соревнования смен с агрегированными данными по параметрам
    """
    parameters = Parameters.query.all()
    
    # Получаем выбранный параметр из сессии или используем параметр 1 по умолчанию
    selected_parameter_id = session.get('selected_parameter_id', 3)
    
    # Получение и валидация дат
    end_date = session.get('end_date')
    start_date = session.get('start_date')
    
    # Если даты пришли как строки, преобразуем их
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S%z')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S%z')
    
    # Получаем параметр и его тип агрегации
    selected_parameter = Parameters.query.get_or_404(selected_parameter_id)
    print(selected_parameter_id, selected_parameter.Name, selected_parameter.aggregation_type, selected_parameter.weight_parameter_id)
    if selected_parameter.aggregation_type == 'weighted_avg' and selected_parameter.weight_parameter_id:
        shift_totals = calculate_weighted_average(selected_parameter, start_date, end_date)
    else:
        shift_totals = calculate_regular_aggregation(selected_parameter, start_date, end_date)

    # Формирование графика работы смен
    shift_schedule = generate_shift_schedule(start_date, end_date)

    return render_template('sore.html',
                         shift_totals=shift_totals,
                         shift_schedule=shift_schedule,
                         start_date=start_date,
                         end_date=end_date,
                         parameters=parameters,
                         selected_parameter=selected_parameter,
                         selected_parameter_id=int(selected_parameter_id))

def calculate_weighted_average(parameter, start_date, end_date):
    """Расчет средневзвешенного значения по сменам"""
    weight_values = db.session.query(
        HourlyValues.DateTime,
        HourlyValues.Value.label('weight_value')
    ).filter(
        HourlyValues.CodeId == parameter.weight_parameter_id,
        HourlyValues.DateTime.between(start_date, end_date),
        HourlyValues.Value != 0
    ).subquery()

    shift_data = db.session.query(
        HourlyValues.Value,
        HourlyValues.DateTime,
        weight_values.c.weight_value
    ).join(
        weight_values,
        HourlyValues.DateTime == weight_values.c.DateTime
    ).filter(
        and_(
            HourlyValues.DateTime.between(start_date, end_date),
            HourlyValues.CodeId == parameter.CodeId
        )
    ).all()

    shift_totals = {shift: {'sum': 0, 'weight_sum': 0} for shift in 'АБВГ'}

    for value, dt, weight in shift_data:
        shift = get_shift_for_datetime(dt)
        if shift and value is not None and weight is not None:
            shift_totals[shift]['sum'] += value * weight
            shift_totals[shift]['weight_sum'] += weight

    return {shift: totals['sum'] / totals['weight_sum'] if totals['weight_sum'] > 0 else 0 
            for shift, totals in shift_totals.items()}

def calculate_regular_aggregation(parameter, start_date, end_date):
    """Расчет обычной агрегации (сумма, минимум, максимум, среднее)"""
    shift_data = db.session.query(
        HourlyValues.Value,
        HourlyValues.DateTime
    ).filter(
        and_(
            HourlyValues.DateTime.between(start_date, end_date),
            HourlyValues.CodeId == parameter.CodeId
        )
    ).all()

    shift_totals = {shift: [] for shift in 'АБВГ'}
    
    for value, dt in shift_data:
        shift = get_shift_for_datetime(dt)
        if shift and value is not None:
            shift_totals[shift].append(value)

    aggregation_funcs = {
        'sum': sum,
        'min': min,
        'max': max,
        'avg': lambda x: sum(x) / len(x)
    }

    return {shift: aggregation_funcs.get(parameter.aggregation_type, 
                                       aggregation_funcs['avg'])(values) if values else 0
            for shift, values in shift_totals.items()}

def generate_shift_schedule(start_date, end_date):
    """Генерация графика работы смен"""
    schedule = []
    current_date = start_date
    while current_date <= end_date:
        schedule.append({
            'date': current_date.date(),
            'hour': current_date.hour,
            'shift': get_shift_for_datetime(current_date)
        })
        current_date += timedelta(hours=1)
    return schedule

@shifts.route('/update_shift_data', methods=['POST'])
@login_required
def update_shift_data():
    parameter_id = request.json.get('parameter_id')
    
    if parameter_id:
        session['selected_parameter_id'] = parameter_id

        end_date = session.get('end_date')
        start_date = session.get('start_date')
        # Если даты пришли как строки, преобразуем их
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S%z')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S%z')
        
        # Получаем параметр и его тип агрегации
        selected_parameter = Parameters.query.get_or_404(parameter_id)
        if selected_parameter.aggregation_type == 'weighted_avg' and selected_parameter.weight_parameter_id:
            shift_totals = calculate_weighted_average(selected_parameter, start_date, end_date)
        else:
            shift_totals = calculate_regular_aggregation(selected_parameter, start_date, end_date)

        # Получаем график работы смен с подсчетом часов
        shift_schedule = generate_shift_schedule(start_date, end_date)
        shift_hours = {shift: len([x for x in shift_schedule if x['shift'] == shift]) 
                      for shift in 'АБВГ'}

        aggregation_type = selected_parameter.aggregation_type.replace('weighted_avg', 'средневзвешенное') \
                                                            .replace('avg', 'среднее') \
                                                            .replace('sum', 'сумма') \
                                                            .replace('min', 'минимум') \
                                                            .replace('max', 'максимум')
                                                            
        return jsonify({
            'title': selected_parameter.Name,
            'aggregation_type': aggregation_type, 
            'weight_parameter_id': selected_parameter.weight_parameter_id,
            'shift_totals': shift_totals,
            'shift_hours': shift_hours,
            'shift_schedule': shift_schedule
        })
    
    return jsonify({'error': 'Parameter ID not provided'}), 400