from flask import flash, render_template, request, redirect, url_for
from sisdental import db
from sisdental.controladores.PacienteControlador import PacienteControlador
from sisdental.controladores.citaControlador import citaControlador
from sisdental.modelos import Persona


def register_routes(app):
 

    # Ruta principal
    @app.route('/')
    def mainpage():
        return render_template('mainpage.html')
    
        
    # Listar todos los pacientes
    @app.route('/pacientes')
    def index():
        pacientes = PacienteControlador.obtener_todos()
        return render_template('index.html', pacientes=pacientes)
    
    
    # Listar Citas
    @app.route('/citas')
    def indexCita():
        fecha_str = request.args.get('fecha')
        patient_id = request.args.get('patientId')

        # 1 Si hay patient_id, filtra solo por ese paciente
        # 2 Si también hay fecha, filtra adicionalmente por la fecha
        # 3 Si no hay patient_id, muestra todas las citas
        if patient_id:
            if fecha_str:
                citas = citaControlador.obtener_por_paciente_y_fecha(patient_id, fecha_str)
            else:
                citas = citaControlador.obtener_por_paciente(patient_id)
        else:
            if fecha_str:
                try:
                    citas = citaControlador.obtener_por_fecha(fecha=fecha_str).all()
                except ValueError:
                    flash("Formato de fecha inválido. Use YYYY-MM-DD", 'error')
                    return redirect(url_for('indexCita'))
            else:
                citas = citaControlador.obtener_todos()

        return render_template('indexCita.html', pacientes=citas)
   

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

            return redirect(url_for('indexCita'))

        return render_template('crearCita.html', error=error)
    
    #@app.route('/gestionPaciente')
    #def gestion_paciente():
    # return render_template('gestionPaciente.html')
    @app.route('/gestionPaciente')
    def gestion_paciente():
        patient_id = request.args.get('patientId')
        paciente = PacienteControlador.obtener_por_id(patient_id)
        if not paciente:
            return "Paciente no encontrado", 404
        return render_template('gestionPaciente.html', paciente=paciente)
    
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
            return redirect(url_for('gestion_paciente',patientId=id))

        return render_template('editar.html', pacientes=paciente)

    # Editar Cita
    @app.route('/<int:id>/editarCita', methods=('GET', 'POST'))
    def editarCita(id):
        paciente = citaControlador.obtener_por_id(id)
        if not paciente:
            return "Cita no encontrado", 404

        if request.method == 'POST':
            fecha_original = request.form['fecha']  # Ej. "31/01/2025"
            # Separa por '/'
            dia, mes, anio = fecha_original.split('/')

            # Ajusta al formato "YYYY-MM-DD" (si es el que usas en DB)
            fecha_formateada = f"{anio}-{mes}-{dia}"

            # Convierte la hora en objeto time
            from datetime import datetime
            hora_str = request.form['hora']  # Ej. "13:30"
            hora_python = datetime.strptime(hora_str, '%H:%M').time()
            hora_formateada = hora_python.strftime("%H:%M")

            nuevos_datos = {
                'paciente_id': request.form['paciente_id'],
                'doctor_id': request.form['doctor_id'],
                'fecha': fecha_formateada,  # Ahora en "YYYY-MM-DD"
                'hora': hora_formateada
            }
            citaControlador.actualizar_cita(id, nuevos_datos)
            return redirect(url_for('indexCita'))

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

    @app.route('/buscarPaciente', methods=['GET', 'POST'])
    def buscarPaciente():
        if request.method == 'GET':
            # Muestra solo la plantilla vacía
            return render_template('buscarPaciente.html', pacientes=None)

        
        valor = request.form.get('valor', '').strip()
        if not valor:
            
            return render_template('buscarPaciente.html', pacientes=[])

       
        personas = Persona.query.filter(
            (Persona.nombre.ilike(f"%{valor}%") | Persona.cedula.ilike(f"%{valor}%")),
            Persona.tipo == 'paciente'
        ).all()

        return render_template('buscarPaciente.html', pacientes=personas)

    @app.route('/api/paciente/<int:paciente_id>', methods=['GET'])
    def get_paciente_api(paciente_id):
        paciente = PacienteControlador.obtener_por_id(paciente_id)
        if not paciente:
            return {"error": "Paciente no encontrado"}, 404

        return {
            "id": paciente.id,
            "nombre": paciente.nombre,
            "cedula": paciente.cedula,
            "telefono": paciente.telefono,
            "email": paciente.email,
            "direccion": paciente.direccion,
            "aseguradora": paciente.aseguradora,
            "nacimiento": paciente.nacimiento
        }, 200