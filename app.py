from sisdental import crear_app, db
from sisdental.modelos.Paciente import Paciente  # ← necesario para que funcione
from sisdental.controladores.webControlador import register_routes

app = crear_app()

with app.app_context():
    try:

        count = db.session.query(Paciente).count()

        print(f"Base de datos conectada correctamente. Total pacientes: {count}")

    except Exception as e:
        print("Error en la conexión:", e)

register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
