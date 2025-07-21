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

    @staticmethod
    def obtener_por_id(tratamiento_id):
    
        return Tratamiento.query.get(tratamiento_id)

    @staticmethod
    def actualizar(tratamiento_id, data):
       
        tratamiento = Tratamiento.query.get(tratamiento_id)
        if tratamiento:
            tratamiento.nombre = data['nombre']
            tratamiento.descripcion = data['descripcion']
            tratamiento.costo = data['costo']
            db.session.commit()
            return True
        return False

    @staticmethod
    def eliminar(tratamiento_id):
       
        tratamiento = Tratamiento.query.get(tratamiento_id)
        if tratamiento:
            db.session.delete(tratamiento)
            db.session.commit()
            return True
        return False
    