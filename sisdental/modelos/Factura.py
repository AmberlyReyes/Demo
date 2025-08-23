from sisdental import db
from datetime import datetime

class Factura(db.Model):
    __tablename__ = 'facturas'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan_tratamientos.id'), nullable=True)
    fecha_emision = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), default='Pendiente')

    paciente = db.relationship('Paciente', backref='facturas')
    pagos = db.relationship('Pago', backref='factura', lazy='dynamic', cascade="all, delete-orphan")
    plan = db.relationship('PlanTratamiento', back_populates='factura')

    cuotas = db.relationship('Cuota', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Factura {self.id} para Paciente {self.paciente_id}>'