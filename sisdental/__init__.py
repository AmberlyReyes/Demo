from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
load_dotenv()

import os

db = SQLAlchemy()

def crear_app():
   # app = Flask(__name__)
    
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
     
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Importar modelos aquí para que se registren con SQLAlchemy
    from sisdental.modelos import (
        Paciente, Persona, Doctor, Asistente, Usuario, Cita,
        HistorialClinico, Factura, Consulta, Enfermedad, Tratamiento, Pago
    )
    with app.app_context():
        db.create_all()

    return app
