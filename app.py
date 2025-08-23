from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

from sisdental import crear_app, db, login_manager
from sisdental.controladores.webControlador import register_routes
from sisdental.modelos.Paciente import Paciente  
from sisdental.modelos.Doctor import Doctor
from sisdental.modelos.Usuario import Usuario

#app = Flask(__name__)
app = crear_app()
app.secret_key = 'tu_clave_secreta_aqui'  

# Configuración de la base de datos
login_manager.login_view = 'login'

# Necesitamos que Usuario herede de UserMixin para Flask-Login


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))

# Configuración de carpeta de subida
upload_folder = os.path.join(app.root_path, 'uploads')
app.config['UPLOAD_FOLDER'] = upload_folder



with app.app_context():
    try:
        # Verificar conexión y contar pacientes
        count = db.session.query(Paciente).count()
        usercount = db.session.query(Usuario).count()
        print(f"Total usuarios: {usercount}")
        print(f"Base de datos conectada correctamente. Total pacientes: {count}")
        
    except Exception as e:
        print("Error en la conexión ", e)
        db.session.rollback()

"""
with app.app_context():
    try:
        
        db.drop_all()
        print("Todas las tablas eliminadas.")

      
        db.create_all()
        print("Todas las tablas creadas.")

       
        admin = Usuario(
            username="admin",
            administrador=True
        )
        admin.set_password("123")  

        db.session.add(admin)
        db.session.commit()
        print("Usuario administrador creado ")

    except Exception as e:
        print("Error al reiniciar la base de datos: ", e)
        db.session.rollback()
"""
register_routes(app)
if __name__ == '__main__':
    app.run(debug=True)
