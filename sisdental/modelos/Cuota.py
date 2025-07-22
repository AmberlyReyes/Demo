from sisdental import db
from datetime import datetime

class Cuota(db.Model):
    __tablename__ = 'cuotas'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('planes_tratamiento.id'), nullable=False)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=True, unique=True) # Hacemos la FK única
    
    numero_cuota = db.Column(db.Integer, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(50), default='Pendiente')

    factura = db.relationship('Factura', back_populates='cuota_asociada')

    def __repr__(self):
        return f'<Cuota {self.numero_cuota} del Plan {self.plan_id}>'