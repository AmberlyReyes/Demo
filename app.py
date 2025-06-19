from sisdental import crear_app, db
from sisdental.modelos.Paciente import Paciente  
from sisdental.modelos.Doctor import Doctor
from sisdental.controladores.webControlador import register_routes

def crearDoc():
        data = {
                'id': 0,
                'nombre': "Pepe",
                'cedula': 2323,
                'telefono': 123,
                'direccion': "alla",
                'email': "Pepe@gmail.com",
                'especialidad': "Todologo"
            }
        try:
            nuevo = Doctor(**data)
            db.session.add(nuevo)
            db.session.commit()
            return nuevo
        except Exception as e:
            error = f"Error insertando Doc: {e}"
            db.session.rollback()

app = crear_app()

with app.app_context():
   
<<<<<<< HEAD
    db.drop_all()
    db.create_all()
=======
    #db.drop_all()
    #db.create_all()
    #crearDoc()
>>>>>>> 714cb03b0a4fc8c3c9ea1b7d870a5dfb1f7f13bd
    
    try:
        count = db.session.query(Paciente).count()
        docCount = db.session.query(Doctor).count()
        print(f"Base de datos conectada correctamente. Total pacientes: {count}")
        print(f"Total Doctores: {docCount}")

    except Exception as e:
        print("Error en la conexión:", e)

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
