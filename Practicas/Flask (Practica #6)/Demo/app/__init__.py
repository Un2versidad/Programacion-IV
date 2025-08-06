from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
import os
import logging

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'super-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['JWT_SECRET_KEY'] = 'jwt-secret'

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)

    login_manager.login_view = 'login'

    # Logging
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(filename='logs/app.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s:%(message)s')

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app