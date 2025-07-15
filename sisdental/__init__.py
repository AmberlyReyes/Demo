from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

import os

db = SQLAlchemy()
login_manager = LoginManager()

def crear_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates')
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
     
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Carpeta de subida DENTRO de static/
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Importar modelos aquí para que se registren con SQLAlchemy
    from sisdental.modelos import (
        Paciente, Persona, Doctor, Asistente, Usuario, Cita,
        HistorialClinico, Factura, Consulta, Enfermedad, Tratamiento, Pago, ArchivoHistorial,PlanTratamiento, PlanTratamientoDetalle, Cuota
    )
    with app.app_context():
        db.create_all()

    return app
