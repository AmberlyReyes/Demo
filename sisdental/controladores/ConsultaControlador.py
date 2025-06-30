from sisdental import db
from sisdental.modelos.Consulta import Consulta
from datetime import date


class ConsultaControlador:

    @staticmethod
    def crear_consulta(data):
        consulta = Consulta(**data)
        db.session.add(consulta)
        db.session.commit()
        return consulta

    @staticmethod
    def obtener_por_id(consulta_id):
        return Consulta.query.get(consulta_id)

    @staticmethod
    def obtener_por_historial(historial_clinico_id):
        return Consulta.query.filter_by(historial_clinico_id=historial_clinico_id).order_by(Consulta.fecha.desc()).all()

    @staticmethod
    def obtener_por_paciente(paciente_id):
        return Consulta.query.filter_by(paciente_id=paciente_id).order_by(Consulta.fecha.desc()).all()

    @staticmethod
    def actualizar_consulta(consulta_id, nuevos_datos):
        consulta = Consulta.query.get(consulta_id)
        if not consulta:
            return None
        for clave, valor in nuevos_datos.items():
            setattr(consulta, clave, valor)
        db.session.commit()
        return consulta

    @staticmethod
    def eliminar_consulta(consulta_id):
        consulta = Consulta.query.get(consulta_id)
        if consulta:
            db.session.delete(consulta)
            db.session.commit()
            return True
        return False

    @staticmethod
    def calcular_edad(nacimiento):
        hoy = date.today()
        return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))