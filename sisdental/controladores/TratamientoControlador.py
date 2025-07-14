from sisdental import db
from sisdental.modelos.Tratamiento import Tratamiento

class TratamientoControlador:
    @staticmethod
    def obtener_todos():
        return Tratamiento.query.order_by(Tratamiento.nombre).all()

    @staticmethod
    def crear(data):
        nuevo = Tratamiento(**data)
        db.session.add(nuevo)
        db.session.commit()
        return nuevo
    
    # Aquí irían las funciones de obtener_por_id, actualizar y eliminar...