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
            cedula TEXT NOT NULL,
            telefono TEXT,
            direccion TEXT,
            nacimiento TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Listar todos los pacientes
@app.route('/')
def index():
    conn = get_db_connection()
    pacientes = conn.execute('SELECT * FROM pacientes').fetchall()
    conn.close()
    return render_template('index.html', pacientes=pacientes)

# crear nuevo paciente
@app.route('/crear', methods=('GET', 'POST'))
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        nacimiento = request.form['nacimiento']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO pacientes (nombre, cedula, telefono,direccion,nacimiento) VALUES (?, ?, ?, ?, ?)',
                     (nombre, cedula, telefono,direccion,nacimiento))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('crear.html')

# editar pacientes
@app.route('/<int:id>/editar', methods=('GET', 'POST'))
def editar(id):
    conn = get_db_connection()
    pacientes = conn.execute('SELECT * FROM pacientes WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        nacimiento = request.form['nacimiento']
        
        conn.execute('UPDATE pacientes SET nombre = ?, cedula = ?, telefono = ?, direccion = ?, nacimiento = ?,  = ? WHERE id = ?',
                     (nombre, cedula, telefono,direccion,nacimiento, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('editar.html', pacientes=pacientes)

# eliminar pacientes
@app.route('/<int:id>/eliminar', methods=('POST',))
def eliminar(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM pacientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)