# app.py
from flask import Flask
from sisdental.controllers import register_routes
from sisdental.models import init_db  # Importamos init_db para usarlo aquí

def create_app():
    app = Flask(__name__)

    # Inicializar DB dentro del app_context
    with app.app_context():
        init_db()

    register_routes(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
