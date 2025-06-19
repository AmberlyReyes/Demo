from sisdental import db
from sisdental.modelos.Persona import Persona

class Asistente(Persona):
    __tablename__ = 'asistentes'
    id = db.Column(db.Integer, db.ForeignKey('personas.id'), primary_key=True)
    salario = db.Column(db.Float)

    __mapper_args__ = {
        'polymorphic_identity': 'asistente',
    }