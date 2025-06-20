import os
from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required

# Create the extension instances here, once and only once
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # --- CONFIGURATION ---
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'users.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.signin'

    # Import blueprints
    from . import auth
    app.register_blueprint(auth.auth)
    
    # Import models
    from . import models

    with app.app_context():
        db.create_all()
        # Create admin user if needed
        if not models.User.query.filter_by(username='admin').first():
            print("Creating default admin user...")
            admin_user = models.User(username='admin', is_admin=True)
            admin_user.set_password('Pass123!')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created.")

    # --- MAIN ROUTES ---
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/rules')
    def rules():
        return render_template('rules.html')

    @app.route('/quiz')
    @login_required
    def quiz():
        return render_template('quiz.html')
    
    # --- PWA Routes (THE FIX IS HERE) ---
    @app.route('/manifest.json')
    def manifest():
        # Use app.static_folder to provide the correct, secure path
        return send_from_directory(app.static_folder, 'manifest.json')

    @app.route('/sw.js')
    def service_worker():
        # Use app.static_folder to provide the correct, secure path
        return send_from_directory(app.static_folder, 'sw.js')

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))