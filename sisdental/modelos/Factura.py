from sisdental import db
from datetime import datetime

class Factura(db.Model):
    __tablename__ = 'facturas'

    id = db.Column(db.Integer, primary_key=True)
    # --- CORRECCIÓN ---
    # La FK debe apuntar a 'personas.id' por la herencia polimórfica.
    paciente_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    
    fecha_emision = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), default='Pendiente')

    # --- RELACIONES MEJORADAS ---
    paciente = db.relationship('Paciente', backref='facturas')
    pagos = db.relationship('Pago', backref='factura', lazy='dynamic', cascade="all, delete-orphan")
    
    # === RELACIÓN AÑADIDA ===
    # Esta es la nueva relación explícita.
    # Le dice a la Factura que está vinculada a una (y solo una) Cuota.
    cuota_asociada = db.relationship('Cuota', back_populates='factura', uselist=False)

    def __repr__(self):
        return f'<Factura {self.id} para Paciente {self.paciente_id}>'