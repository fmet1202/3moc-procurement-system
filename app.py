import os
from flask import Flask
from extensions import db, login_manager, csrf, limiter
from config import Config
from models import AdminUser

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    csrf.init_app(app)
    limiter.init_app(app)

    from routes.public import public_bp
    from routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    with app.app_context():
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(AdminUser, int(user_id))

if __name__ == "__main__":
    app = create_app()
    print("3 MOC System Running on http://127.0.0.1:5000")
    print("Admin portal: http://127.0.0.1:5000/admin")
    # debug=True must never run in production (Render sets FLASK_ENV/PORT,
    # so this branch only ever executes locally via `python app.py`)
    app.run(debug=True)