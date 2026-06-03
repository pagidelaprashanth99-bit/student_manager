from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "your-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///student_manager.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path,
        "static",
        "uploads"
    )

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    from app.auth import auth
    from app.teacher import teacher
    from app.student import student
    from app.emergency import emergency

    app.register_blueprint(auth)
    app.register_blueprint(teacher)
    app.register_blueprint(student)
    app.register_blueprint(emergency)

    with app.app_context():
        db.create_all()

    return app
