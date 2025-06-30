from sisdental import crear_app, db
from sisdental.modelos.Paciente import Paciente  
from sisdental.modelos.Doctor import Doctor
from sisdental.controladores.webControlador import register_routes

app = crear_app()

with app.app_context():
    try:
        # Verificar conexión y contar pacientes
        count = db.session.query(Paciente).count()
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
