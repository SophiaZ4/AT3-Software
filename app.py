# app.py
from flask import Flask, render_template, send_from_directory, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required
from functools import wraps
import os

from models import db, User # Import from your models file
from auth import auth as auth_blueprint # Import the blueprint from auth.py

app = Flask(__name__)

# Configurations
app.config['SECRET_KEY'] = 'hfeiosahfaoi80132'  # Change this
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance/users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create instance folder if it doesn't exist
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Create database and roles
with app.app_context():
    db.create_all()
    if not Role.query.filter_by(name='admin').first():
        admin_role = Role(name='admin')
        user_role = Role(name='user')
        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()
    if not User.query.filter_by(username='admin').first():
        admin_role = Role.query.filter_by(name='admin').first()
        admin_user = User(username='admin', role=admin_role)
        admin_user.set_password('admin') # Change in production
        db.session.add(admin_user)
        db.session.commit()

# Register Blueprints
app.register_blueprint(auth_blueprint)

# Role-based access decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'admin':
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Main Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rules')
@login_required
def rules():
    return render_template('rules.html')

@app.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html')

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

if __name__ == '__main__':
    app.run(debug=True)