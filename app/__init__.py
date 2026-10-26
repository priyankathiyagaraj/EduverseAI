import os
from flask import Flask, render_template, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flasgger import Swagger
from config import config_by_name

# Core extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_name=None):
    """Application Factory for EduVerse AI."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    import sys
    from pathlib import Path
    if getattr(sys, 'frozen', False):
        bundle_dir = Path(sys._MEIPASS)
        template_folder = str(bundle_dir / 'app' / 'templates')
        static_folder = str(bundle_dir / 'app' / 'static')
        app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    else:
        app = Flask(__name__)

    config_obj = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_obj)

    Swagger(app, config={
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    })

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Exclude API endpoints from CSRF if using raw JSON POST/PUT/DELETE
    # CSRF is active for web forms and header-passed tokens for fetch/ajax
    # Register Jinja context processors for navigation, user session, and compare count
    app.jinja_env.globals.update(zip=zip)

    @app.context_processor
    def inject_globals():
        user = session.get('user')
        compare_list = session.get('compare_list', [])
        pending_queries_count = 0
        if user and user.get('role') == 'admin':
            try:
                from app.models.student_query import StudentQuery
                pending_queries_count = StudentQuery.query.filter_by(status='PENDING').count()
            except Exception:
                pending_queries_count = 0
        return {
            'current_user': user,
            'compare_count': len(compare_list),
            'compare_list': compare_list,
            'pending_queries_count': pending_queries_count
        }

    @app.before_request
    def track_student_activity():
        user = session.get('user')
        if user and user.get('role') == 'student':
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            last_touch = session.get('_last_activity_touch')
            if not last_touch or (now.timestamp() - last_touch > 60):
                session['_last_activity_touch'] = now.timestamp()
                try:
                    from app.services.student_analytics_service import touch_student_activity
                    touch_student_activity(user.get('id'))
                except Exception:
                    pass

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.colleges import colleges_bp
    from app.routes.comparison import comparison_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.analytics import analytics_bp
    from app.routes.admin import admin_bp
    from app.routes.student import student_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(colleges_bp)
    app.register_blueprint(comparison_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)

    return app
