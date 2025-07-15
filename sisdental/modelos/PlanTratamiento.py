from sisdental import db
from datetime import datetime

class PlanTratamiento(db.Model):
    __tablename__ = 'planes_tratamiento'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    nombre_plan = db.Column(db.String(200), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    costo_total = db.Column(db.Float, default=0.0)
    estado = db.Column(db.String(50), default='none') # Activo, Finalizado, Cancelado
    paciente = db.relationship('Paciente', foreign_keys=[paciente_id], backref='planes_tratamiento')
    # Conexión con el Doctor que crea el plan
    doctor = db.relationship('Doctor', foreign_keys=[doctor_id], backref='planes_creados')
    # Un Plan de Tratamiento tiene muchos "detalles" (los tratamientos incluidos)
    # cascade="all, delete-orphan" significa que si borras un plan, se borran sus detalles
    detalles = db.relationship('PlanTratamientoDetalle', backref='plan', lazy='dynamic', cascade="all, delete-orphan")
    # Un Plan de Tratamiento tiene muchas "cuotas" (el plan de pagos)
    cuotas = db.relationship('Cuota', backref='plan', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<PlanTratamiento {self.id} - {self.nombre_plan}>'