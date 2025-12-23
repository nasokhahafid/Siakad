from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    from .models.user import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)

    # Load configuration from Config class
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from .api.users_api import users_bp
    from .api.matakuliah_api import matkul_bp
    from .routes import main_bp
    from .blueprints.elearning import elearning_bp
    from .blueprints.pengajuan import pengajuan_bp
    from .blueprints.akademik import akademik_bp
    from .blueprints.admin import admin_bp

    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(matkul_bp, url_prefix='/api')
    app.register_blueprint(main_bp)
    app.register_blueprint(elearning_bp)
    app.register_blueprint(pengajuan_bp)
    app.register_blueprint(akademik_bp)
    app.register_blueprint(admin_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'status': 'error', 'message': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'status': 'error', 'message': 'Internal server error'}, 500

    return app
