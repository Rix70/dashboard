from app import app, db
from app.models import User

with app.app_context():
    admin = User(username='admin',  is_admin=True)
    admin.set_password('123')
    db.session.add(admin)
    db.session.commit()