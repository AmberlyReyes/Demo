from sisdental import db
from sisdental.modelos.Persona import Persona

class Paciente(Persona):
    __tablename__ = 'pacientes'
    id = db.Column(db.Integer, db.ForeignKey('personas.id'), primary_key=True)
    aseguradora = db.Column(db.String(100))
    num_aseguradora = db.Column(db.String(50))
    historiales = db.relationship('HistorialClinico', backref='paciente', lazy=True)
    citas = db.relationship('Cita', backref='paciente', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'paciente',
    }

def configure_relationships():
    from sisdental.modelos.Factura import Factura
    from sisdental.modelos.HistorialClinico import HistorialClinico
    from sisdental.modelos.Cita import Cita
    
    Paciente.facturas = db.relationship('Factura', backref='paciente', lazy=True)
    Paciente.historiales = db.relationship('HistorialClinico', backref='paciente', lazy=True)
    Paciente.citas = db.relationship('Cita', backref='paciente', lazy=True)

configure_relationships()