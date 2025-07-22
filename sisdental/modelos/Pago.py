from sisdental import db
from datetime import datetime

class Pago(db.Model):
    __tablename__ = 'pagos'

    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    monto = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Pago {self.id} de ${self.monto} para Factura {self.factura_id}>'