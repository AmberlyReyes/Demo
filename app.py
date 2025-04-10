from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# conectar a la base de datos
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear la tabla si no existe
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT NOT NULL UNIQUE,
            telefono TEXT,
            direccion TEXT,
            email TEXT,
            aseguradora TEXT,
            num_aseguradora TEXT,
            nacimiento TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Listar todos los pacientes
@app.route('/')
def mainpage():
    return render_template('mainpage.html')

# Listar todos los pacientes en "index.html"
@app.route('/pacientes')
def index():
    conn = get_db_connection()
    pacientes = conn.execute('SELECT * FROM pacientes').fetchall()
    conn.close()
    return render_template('index.html', pacientes=pacientes)



# crear nuevo paciente
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

        conn = get_db_connection()
        cedula_existente = conn.execute(
            'SELECT * FROM pacientes WHERE cedula = ?', (cedula,)
        ).fetchone()

        if cedula_existente:
            error = f"La cédula '{cedula}' ya está registrada."
            conn.close()
            return render_template('crear.html', error=error)

        try:
            conn.execute('''
                INSERT INTO pacientes (nombre, cedula, telefono, direccion, email, aseguradora, num_aseguradora, nacimiento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, cedula, telefono, direccion, email, aseguradora, num_aseguradora, nacimiento))
            conn.commit()
        except sqlite3.IntegrityError:
            error = f"La cédula '{cedula}' ya existe."
            return render_template('crear.html', error=error)
        finally:
            conn.close()

        return redirect(url_for('index'))

    return render_template('crear.html', error=error)



# editar pacientes
@app.route('/<int:id>/editar', methods=('GET', 'POST'))
def editar(id):
    conn = get_db_connection()
    paciente = conn.execute('SELECT * FROM pacientes WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        nombre          = request.form['nombre']
        cedula          = request.form['cedula']
        telefono        = request.form['telefono']
        direccion       = request.form['direccion']
        email           = request.form['email']
        aseguradora     = request.form['aseguradora']
        num_aseguradora = request.form['num_aseguradora']
        nacimiento      = request.form['nacimiento']
        
        conn.execute('''
            UPDATE pacientes
            SET nombre = ?,
                cedula = ?,
                telefono = ?,
                direccion = ?,
                email = ?,
                aseguradora = ?,
                num_aseguradora = ?,
                nacimiento = ?
            WHERE id = ?
        ''', (nombre, cedula, telefono, direccion, email, aseguradora, num_aseguradora, nacimiento, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('editar.html', pacientes=paciente)

# eliminar pacientes
@app.route('/<int:id>/eliminar', methods=('POST',))
def eliminar(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM pacientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/paciente/<int:id>')
def detalle_paciente(id):
    conn = get_db_connection()
    paciente = conn.execute('SELECT * FROM pacientes WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    # Si deseas manejar el caso de paciente inexistente
    if not paciente:
        return "Paciente no encontrado", 404
    
    return render_template('detalle.html', paciente=paciente)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)