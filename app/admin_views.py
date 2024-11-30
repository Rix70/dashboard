from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_admin import Admin, AdminIndexView, expose 
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required
from werkzeug.exceptions import HTTPException

from app import db
from app.models import HourlyValues, PageSettings, Parameters, User

# Создаем классы представлений
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        flash('Для доступа к этой странице необходимы права администратора.', 'error')
        return redirect(url_for('auth.login'))

class UserAdminView(SecureModelView):
    column_list = ['id', 'username', 'is_admin']
    column_searchable_list = ['username']
    column_filters = ['is_admin']
    form_columns = ['username', 'is_admin']
    column_labels = {
        'id': 'ID',
        'username': 'Имя пользователя',
        'is_admin': 'Администратор'
    }   
    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50

class ParametersView(SecureModelView):
    column_list = ['CodeId', 'Name', 'aggregation_type', 'weight_parameter_id']
    column_labels = {
        'CodeId': 'ID параметра',
        'Name': 'Название',
        'aggregation_type': 'Тип агрегации',
        'weight_parameter_id': 'ID параметра-веса'
    }
    column_searchable_list = ['Name', 'CodeId']
    column_filters = ['aggregation_type']
    form_choices = {
        'aggregation_type': [
            ('avg', 'Среднее'),
            ('sum', 'Сумма'),
            ('min', 'Минимум'),
            ('max', 'Максимум'),
            ('weighted_avg', 'Средневзвешенное')
        ]
    }
    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50  

class HourlyValuesView(SecureModelView):
    column_list = ['DateTime', 'CodeId', 'Value']
    column_labels = {
        'DateTime': 'Дата и время',
        'CodeId': 'ID параметра',
        'Value': 'Значение'
    }
    column_searchable_list = ['CodeId']
    column_filters = ['DateTime', 'CodeId']
    page_size = 50

class PageSettingsView(SecureModelView):
    column_list = ['page_name', 'id_list']
    column_labels = {
        'page_name': 'Название страницы',
        'id_list': 'Список параметров'
    }
    column_searchable_list = ['page_name']

class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('Для доступа к этой странице необходимы права администратора.', 'error')
        return redirect(url_for('auth.login', next=request.url))

    @expose('/')
    def index(self):
        if not self.is_accessible():
            return self.inaccessible_callback(name='admin.index')
        return super(CustomAdminIndexView, self).index()

    def handle_url_error(self, error):
        if isinstance(error, HTTPException):
            if error.code == 403:
                flash('У вас нет прав для доступа к этой странице.', 'error')
                return redirect(url_for('auth.login'))
        return super(CustomAdminIndexView, self).handle_url_error(error)

def init_admin(app):
    admin = Admin(
        app, 
        name='Админ-панель', 
        template_mode='bootstrap4',
        index_view=CustomAdminIndexView(),
        base_template='admin/custom_master.html'
    )
    
    # Регистрация представлений
    admin.add_view(UserAdminView(User, db.session, name='Пользователи'))
    admin.add_view(ParametersView(Parameters, db.session, name='Параметры'))
    admin.add_view(HourlyValuesView(HourlyValues, db.session, name='Часовые данные'))
    admin.add_view(PageSettingsView(PageSettings, db.session, name='Настройки страниц'))
    
    return admin 
