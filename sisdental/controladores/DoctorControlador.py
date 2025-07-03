from sisdental import db
#from sisdental.modelos import Paciente
from sisdental.modelos.Doctor import Doctor

class DoctorControlador:

    @staticmethod
    def crear_doctor(data):
        try:
            # Obligatorio para que la fila sea de tipo 'doctor'
            data['tipo'] = 'doctor'
            nuevo = Doctor(**data)
            db.session.add(nuevo)
            db.session.commit()
            return nuevo
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear doctor: {e}")
            return None

    @staticmethod
    def obtener_todos():
        return Doctor.query.all()

    @staticmethod
    def obtener_por_id(doctor_id):
        return Doctor.query.get(doctor_id)

    @staticmethod
    def actualizar_doctor(doctor_id, nuevos_datos):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return None
        for clave, valor in nuevos_datos.items():
            setattr(doctor, clave, valor)
        db.session.commit()
        return doctor

    @staticmethod
    def eliminar_doctor(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if doctor:
            db.session.delete(doctor)
            db.session.commit()
            return True
        return False
