from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session, send_file, flash
from app.models import Parameters, HourlyValues, PageSettings, User, PageHierarchy
from datetime import datetime


# Создаем Blueprint
chart = Blueprint('chart', __name__)

@chart.route('/get_parameter_data', methods=['POST'])
def get_parameter_data():
    data = request.get_json()
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%dT%H:%M')
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%dT%H:%M')
    parameter_id = data['parameter_id']
    
    values = HourlyValues.query.filter(
        HourlyValues.CodeId == parameter_id,
        HourlyValues.DateTime.between(start_date, end_date)
    ).order_by(HourlyValues.DateTime).all()
    
    return jsonify({
        'dates': [v.DateTime.strftime('%d.%m.%Y %H:%M') for v in values],
        'values': [v.Value if v.Value is not None else None for v in values]
    })