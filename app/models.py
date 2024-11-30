from app import db, bcrypt
from flask_login import UserMixin

class Parameters(db.Model):
    CodeId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50))
    aggregation_type = db.Column(db.String(20), default='avg')  # 'avg', 'sum', 'min', 'max', 'weighted_avg'
    weight_parameter_id = db.Column(db.Integer, nullable=True)  # ID параметра-веса (расхода)
    values = db.relationship('HourlyValues', backref='parameter', lazy=True)

class HourlyValues(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    CodeId = db.Column(db.Integer, db.ForeignKey('parameters.CodeId'))
    DateTime = db.Column(db.DateTime)
    Value = db.Column(db.Float)

# модель для хранения настроек страниц
class PageSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(100))
    id_list = db.Column(db.String(500))
    _children = None  # Приватный атрибут для хранения дочерних страниц

    @property
    def page_ids(self):
        # Преобразование строки ID в список чисел
        return [int(x.strip()) for x in self.id_list.split(',') if x.strip()]

    @property
    def parent(self):
        hierarchy = PageHierarchy.query.filter_by(child_id=self.id).first()
        return hierarchy.parent if hierarchy else None

    @property
    def children(self):
        if self._children is None:
            hierarchies = PageHierarchy.query.filter_by(parent_id=self.id).order_by(PageHierarchy.order).all()
            self._children = [h.child for h in hierarchies]
        return self._children

    @children.setter
    def children(self, value):
        self._children = value

    @property
    def parent_id(self):
        hierarchy = PageHierarchy.query.filter_by(child_id=self.id).first()
        return hierarchy.parent_id if hierarchy else None

    def clear_children_cache(self):
        self._children = None

class PageHierarchy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('page_settings.id'), nullable=True)
    child_id = db.Column(db.Integer, db.ForeignKey('page_settings.id'), nullable=False)
    order = db.Column(db.Integer, default=0)  # для сортировки страниц

    parent = db.relationship('PageSettings', foreign_keys=[parent_id], backref='children_refs')
    child = db.relationship('PageSettings', foreign_keys=[child_id], backref='parent_ref')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password_hash):
        if len(password_hash) < 3:
            raise ValueError("Пароль должен содержать минимум 3 символов")
        self.password_hash = bcrypt.generate_password_hash(password_hash).decode('utf-8')

    def check_password(self, password_hash):
        return bcrypt.check_password_hash(self.password_hash, password_hash)

    def __repr__(self):
        return f'<User {self.username}>'
