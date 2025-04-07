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
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Listar todos los productos
@app.route('/')
def index():
    conn = get_db_connection()
    productos = conn.execute('SELECT * FROM productos').fetchall()
    conn.close()
    return render_template('index.html', productos=productos)

# crear nuevo producto
@app.route('/crear', methods=('GET', 'POST'))
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        descripcion = request.form['descripcion']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO productos (nombre, precio, descripcion) VALUES (?, ?, ?)',
                     (nombre, precio, descripcion))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('crear.html')

# editar producto
@app.route('/<int:id>/editar', methods=('GET', 'POST'))
def editar(id):
    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        descripcion = request.form['descripcion']
        
        conn.execute('UPDATE productos SET nombre = ?, precio = ?, descripcion = ? WHERE id = ?',
                     (nombre, precio, descripcion, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('editar.html', producto=producto)

# eliminar producto
@app.route('/<int:id>/eliminar', methods=('POST',))
def eliminar(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM productos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)