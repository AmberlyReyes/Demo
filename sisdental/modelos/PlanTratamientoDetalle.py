from sisdental import db

class PlanTratamientoDetalle(db.Model):
    __tablename__ = 'planes_tratamiento_detalle'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('planes_tratamiento.id'), nullable=False)
    tratamiento_id = db.Column(db.Integer, db.ForeignKey('tratamientos.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    costo_aplicado = db.Column(db.Float, nullable=False)
    tratamiento = db.relationship('Tratamiento')

    def __repr__(self):
        return f'<DetallePlan {self.id} para Plan {self.plan_id}>'