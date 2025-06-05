from sisdental import db

class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    fecha_emision = db.Column(db.Date)
    fecha_vencimiento = db.Column(db.Date)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'))
    total = db.Column(db.Float)
    # Relaciones con tratamientos y pagos se pueden agregar después