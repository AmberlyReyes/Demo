from sisdental import crear_app, db
from sisdental.modelos.Paciente import Paciente  
from sisdental.modelos.Doctor import Doctor
from sisdental.controladores.webControlador import register_routes
from sisdental.modelos.Usuario import Usuario
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

#app = Flask(__name__)
app = crear_app()
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave segura


# Configuración de la base de datos
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Necesitamos que Usuario herede de UserMixin para Flask-Login
# Puedes hacerlo directamente en tu modelo o así:
Usuario.__bases__ = (UserMixin,) + Usuario.__bases__

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

with app.app_context():
    try:
        # Verificar conexión y contar pacientes
        count = db.session.query(Paciente).count()
        usercount = db.session.query(Usuario).count()
        print(f"Total usuarios: {usercount}")
        print(f"Base de datos conectada correctamente. Total pacientes: {count}")
        # Agregar un doctor solo si no existe con esa cédula
        cedula_doctor = "402-12345678"  
        doctor_existente = Doctor.query.filter_by(cedula=cedula_doctor).first()
        if not doctor_existente:
            nuevo_doctor = Doctor(
                nombre="Ana Martínez",
                cedula=cedula_doctor,
                telefono="5551234",
                direccion="Av. Central 123",
                email="ana.martinez@ejemplo.com",
                especialidad="Ortodoncia"
            )
            db.session.add(nuevo_doctor)
            db.session.commit()
            print(f"Doctor agregado: {nuevo_doctor.nombre}")
        else:
            print(f"El doctor con cédula {cedula_doctor} ya existe: {doctor_existente.nombre}")

    except Exception as e:
        print("Error en la conexión o al agregar doctor:", e)
        db.session.rollback()

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
