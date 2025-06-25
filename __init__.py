import os
from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from flask import redirect, url_for
from flask_minify import Minify 
from flask_compress import Compress


# Create the extension instances here, once and only once
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    Compress(app)

    # --- CONFIGURATION ---
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:////Users/sophiazammit/HSCAT3/instance/users.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # lines for debugging
    print(f"Flask Instance Path: {app.instance_path}")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.signin'
    
    Minify(app=app, html=True, js=True, cssless=True) # Optimisation by minifying files

    from .quiz import quiz_bp # Import quiz
    app.register_blueprint(quiz_bp)

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
    @login_required
    def index():
        # If the user is already logged in, take them to the new /home page
        return render_template('index.html')

    @app.route('/rules')
    @login_required
    def rules():
        return render_template('rules.html')

    #@app.route('/quiz') @login_required def quiz(): return render_template('quiz.html') OLD QUIZ PAGE
    
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