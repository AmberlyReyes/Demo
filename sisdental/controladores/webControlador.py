from flask import render_template, request, redirect, url_for
from sisdental import db
from sisdental.controladores.PacienteControlador import PacienteControlador
from sisdental.controladores.citaControlador import citaControlador


def register_routes(app):
    """Registra todas las rutas de la aplicación Flask en el objeto 'app'."""

    # Ruta principal
    @app.route('/')
    def mainpage():
        return render_template('mainpage.html')
    
        
    # Listar todos los pacientes
    @app.route('/pacientes')
    def index():
        pacientes = PacienteControlador.obtener_todos()
        return render_template('index.html', pacientes=pacientes)
    
    @app.route('/buscarPaciente')
    def buscarPaciente():
        return render_template('buscarPaciente.html')
    
    # Listar Citas
    @app.route('/citas')
    def indexCita():
        pacientes = citaControlador.obtener_todos()
        return render_template('indexCita.html', pacientes=pacientes)

    # Crear nuevo paciente
    @app.route('/crear', methods=('GET', 'POST'))
    def crear():
        error = None

        if request.method == 'POST':
            data = {
                'nombre': request.form['nombre'],
                'cedula': request.form['cedula'],
                'telefono': request.form['telefono'],
                'direccion': request.form['direccion'],
                'email': request.form['email'],
                'aseguradora': request.form['aseguradora'],
                'num_aseguradora': request.form['num_aseguradora'],
                'nacimiento': request.form['nacimiento']
            }

            # Verificar si la cédula existe
            if PacienteControlador.obtener_por_cedula(data['cedula']):
                error = f"La cédula '{data['cedula']}' ya está registrada."
                return render_template('crear.html', error=error)

            try:
                PacienteControlador.crear_paciente(data)
            except Exception as e:
                error = f"Error insertando paciente: {e}"
                return render_template('crear.html', error=error)

            return redirect(url_for('index'))

        return render_template('crear.html', error=error)

    # Crear nuevo Cita
    @app.route('/crearCita', methods=('GET', 'POST'))
    def crearCita():
        error = None

        if request.method == 'POST':
            data = {
                'paciente_id': request.form['paciente_id'],
                'doctor_id': request.form['doctor_id'],
                'fecha': request.form['fecha'],
                'hora': request.form['hora'],
            }

            # Verificar si la Cita choca con otra TO-DO
            #if PacienteControlador.obtener_por_cedula(data['cedula']):
            #    error = f"La cédula '{data['cedula']}' ya está registrada."
            #    return render_template('crear.html', error=error)

            try:
                citaControlador.crear_cita(data)
            except Exception as e:
                error = f"Error insertando cita: {e}"
                return render_template('crearCita.html', error=error)

            return redirect(url_for('index'))

        return render_template('crearCita.html', error=error)


    # Editar pacientes
    @app.route('/<int:id>/editar', methods=('GET', 'POST'))
    def editar(id):
        paciente = PacienteControlador.obtener_por_id(id)
        if not paciente:
            return "Paciente no encontrado", 404

        if request.method == 'POST':
            nuevos_datos = {
                'nombre': request.form['nombre'],
                'cedula': request.form['cedula'],
                'telefono': request.form['telefono'],
                'direccion': request.form['direccion'],
                'email': request.form['email'],
                'aseguradora': request.form['aseguradora'],
                'num_aseguradora': request.form['num_aseguradora'],
                'nacimiento': request.form['nacimiento']
            }
            PacienteControlador.actualizar_paciente(id, nuevos_datos)
            return redirect(url_for('index'))

        return render_template('editar.html', pacientes=paciente)

# Editar Cita
    @app.route('/<int:id>/editarCita', methods=('GET', 'POST'))
    def editarCita(id):
        paciente = citaControlador.obtener_por_id(id)
        if not paciente:
            return "Cita no encontrado", 404

        if request.method == 'POST':
            fecha_original = request.form['fecha']
            anio, mes, dia = fecha_original.split('-')
            fecha_formateada = f"{dia}/{mes}/{anio}"

            hora_python = request.form['hora'].time()  # Convierte a datetime.time
            hora_formateada = hora_python.strftime("%H:%M")

            print(fecha_formateada)
            print(hora_formateada)
            nuevos_datos = {
                'pacienteId': request.form['pacienteId'],
                'doctorId': request.form['doctorId'],
                'fecha': fecha_formateada,
                'hora': hora_formateada,
            }
            citaControlador.actualizar_cita(id, nuevos_datos)
            return redirect(url_for('index'))

        return render_template('editarCita.html', pacientes=paciente)


    # Eliminar pacientes
    @app.route('/<int:id>/eliminar', methods=('POST',))
    def eliminar(id):
        PacienteControlador.eliminar_paciente(id)
        return redirect(url_for('index'))
    
    # Eliminar cita
    @app.route('/<int:id>/eliminarCita', methods=('POST',))
    def eliminarCita(id):
        citaControlador.eliminar_paciente(id)
        return redirect(url_for('indexCita'))

    # Detalle de un paciente
    @app.route('/paciente/<int:id>')
    def detalle_paciente(id):
        paciente = PacienteControlador.obtener_por_id(id)
        if not paciente:
            return "Paciente no encontrado", 404
        return render_template('detalle.html', paciente=paciente)
    
    # Detalle de Cita
    @app.route('/cita/<int:id>')
    def detalle_cita(id):
        paciente = citaControlador.obtener_por_id(id)
        if not paciente:
            return "Cita no encontrada", 404
        return render_template('detalleCita.html', paciente=paciente)