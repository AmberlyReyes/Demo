from . import db

class Paciente(db.Model):
    __tablename__ = "pacientes"

    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(150))
    email = db.Column(db.String(100))
    aseguradora = db.Column(db.String(100))
    num_aseguradora = db.Column(db.String(50), unique=True)
    nacimiento = db.Column(db.String(10))  
