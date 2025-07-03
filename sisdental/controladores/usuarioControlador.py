from sisdental import db
#from sisdental.modelos import Paciente
from sisdental.modelos.Usuario import Usuario
from sisdental.modelos.Persona import Persona

class UsuarioControlador:

    @staticmethod
    def crear_usuario(data):
        try:
            # Obligatorio para que la fila sea de tipo 'usuario'
            #data['tipo'] = 'usuario'
            nuevo = Usuario(**data)
            db.session.add(nuevo)
            db.session.commit()
            return nuevo
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuario: {e}")
            return None

    @staticmethod
    def obtener_todos():
        return Usuario.query.all()

    @staticmethod
    def obtener_por_id(usuario_id):
        return Usuario.query.get(usuario_id)

    @staticmethod
    def actualizar_usuario(usuario_id, nuevos_datos):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return None
        for clave, valor in nuevos_datos.items():
            setattr(usuario, clave, valor)
        db.session.commit()
        return usuario

    @staticmethod
    def eliminar_usuario(usuario_id):
        usuario = Usuario.query.get(usuario_id)
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            return True
        return False