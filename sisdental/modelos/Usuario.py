# En sisdental/modelos/Usuario.py
from sisdental import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    # Aumentamos el tamaño a 255 caracteres (o usa db.Text si prefieres longitud ilimitada)
    password = db.Column(db.String(255), nullable=False)
    administrador = db.Column(db.Boolean, default=False)
    doctor = db.Column(db.Boolean, default=False)
    asistente = db.Column(db.Boolean, default=False)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), unique=True, nullable=True)
    persona = db.relationship('Persona', backref='usuario', uselist=False)

    # --- MÉTODOS AÑADIDOS ---
    def set_password(self, password):
        """Crea un hash seguro para la contraseña."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña contra el hash almacenado."""
        return check_password_hash(self.password, password)