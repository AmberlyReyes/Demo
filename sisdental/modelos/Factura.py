from sisdental import db

class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'))
    paciente = db.relationship('Paciente', backref='facturas', lazy=True)
    total = db.Column(db.Float)
    # Relaciones con tratamientos y pagos se pueden agregar después
