from sisdental import db
from sisdental.modelos.Persona import Persona

class Doctor(Persona):
    __tablename__ = 'doctores'
    id = db.Column(db.Integer, db.ForeignKey('personas.id'), primary_key=True)
    especialidad = db.Column(db.String(100))
    citas = db.relationship('Cita', backref='doctor', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'doctor',
    }
    