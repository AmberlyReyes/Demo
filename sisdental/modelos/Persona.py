from sisdental import db

class Persona(db.Model):
    __tablename__ = 'personas'
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(150))
    email = db.Column(db.String(100))
    nacimiento = db.Column(db.Date)
    tipo = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'persona',
        'polymorphic_on': tipo
    }