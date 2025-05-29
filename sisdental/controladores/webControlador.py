from flask import render_template, request, redirect, url_for
from sisdental.controladores.PacienteControlador import (
    crear_paciente, obtener_todos, obtener_por_id, actualizar_paciente, eliminar_paciente, obtener_por_cedula
)

def register_routes(app):
    """Registra todas las rutas de la aplicación Flask en el objeto 'app'."""
    
    # Ruta principal
    @app.route('/')
    def mainpage():
        return render_template('mainpage.html')

    # Listar todos los pacientes
    @app.route('/pacientes')
    def index():
        pacientes = obtener_todos()
        return render_template('index.html', pacientes=pacientes)

    # Crear nuevo paciente
    @app.route('/crear', methods=('GET', 'POST'))
    def crear():
        error = None

        if request.method == 'POST':
            nombre          = request.form['nombre']
            cedula          = request.form['cedula']
            telefono        = request.form['telefono']
            direccion       = request.form['direccion']
            email           = request.form['email']
            aseguradora     = request.form['aseguradora']
            num_aseguradora = request.form['num_aseguradora']
            nacimiento      = request.form['nacimiento']

            # Verificar si la cédula existe
            if obtener_por_cedula(cedula):
                error = f"La cédula '{cedula}' ya está registrada."
                return render_template('crear.html', error=error)

            try:
                crear_paciente(
                    nombre, cedula, telefono, direccion, email,
                    aseguradora, num_aseguradora, nacimiento
                )
            except Exception as e:
                error = f"Error insertando paciente: {e}"
                return render_template('crear.html', error=error)

            return redirect(url_for('index'))

        return render_template('crear.html', error=error)

    # Editar pacientes
    @app.route('/<int:id>/editar', methods=('GET', 'POST'))
    def editar(id):
        paciente = obtener_por_id(id)
        if not paciente:
            return "Paciente no encontrado", 404

        if request.method == 'POST':
            nombre          = request.form['nombre']
            cedula          = request.form['cedula']
            telefono        = request.form['telefono']
            direccion       = request.form['direccion']
            email           = request.form['email']
            aseguradora     = request.form['aseguradora']
            num_aseguradora = request.form['num_aseguradora']
            nacimiento      = request.form['nacimiento']

            actualizar_paciente(
                id, nombre, cedula, telefono, direccion,
                email, aseguradora, num_aseguradora, nacimiento
            )
            return redirect(url_for('index'))

        return render_template('editar.html', pacientes=paciente)

    # Eliminar pacientes
    @app.route('/<int:id>/eliminar', methods=('POST',))
    def eliminar(id):
        eliminar_paciente(id)
        return redirect(url_for('index'))

    # Detalle de un paciente
    @app.route('/paciente/<int:id>')
    def detalle_paciente(id):
        paciente = obtener_por_id(id)
        if not paciente:
            return "Paciente no encontrado", 404
        return render_template('detalle.html', paciente=paciente)