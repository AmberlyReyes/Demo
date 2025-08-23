from sisdental import db
from datetime import datetime

class Cuota(db.Model):
    __tablename__ = 'cuotas'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan_tratamientos.id'), nullable=False)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=True)  # Removida restricción unique=True
    
    numero_cuota = db.Column(db.Integer, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(50), default='Pendiente')  # Posibles valores: 'Pendiente', 'Parcial', 'Pagada'

    factura = db.relationship('Factura', back_populates='cuotas')
    plan = db.relationship('PlanTratamiento', back_populates='cuotas')
    
    def __repr__(self):
        return f'<Cuota {self.numero_cuota} del Plan {self.plan_id}>'