from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def crear_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost/sysdental' #ESTO TODAVIA NO ES FUNCIONAL, TENGO Q CREAR UN USER
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Importar modelos aquí para que se registren con SQLAlchemy
    from sisdental.modelos import Paciente
    with app.app_context():
        db.create_all()

    return app
