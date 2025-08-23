from sisdental import db
from datetime import datetime

class PlanTratamiento(db.Model):
    __tablename__ = 'plan_tratamientos'

    id             = db.Column(db.Integer, primary_key=True)
    paciente_id    = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    doctor_id      = db.Column(db.Integer, db.ForeignKey('doctores.id'), nullable=False)
    nombre_plan    = db.Column(db.String(200), nullable=False)
    fecha_inicio   = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    costo_total    = db.Column(db.Float, default=0.0, nullable=False)
    numero_cuotas  = db.Column(db.Integer, default=1, nullable=False)
    estado         = db.Column(db.String(50), default='Activo')

    # == Relaciones ==
    paciente = db.relationship('Paciente', backref='planes_tratamiento')
    doctor   = db.relationship('Doctor',   backref='planes_creados')


    detalles = db.relationship(
        'PlanTratamientoDetalle',
        back_populates='plan',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    citas = db.relationship(
        'Cita',
        back_populates='plan',
        lazy='dynamic'
    )
    cuotas = db.relationship(
        'Cuota',
        back_populates='plan',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    # Relación bidireccional con Factura
    factura = db.relationship(
        'Factura',
        back_populates='plan',
        uselist=False
    )