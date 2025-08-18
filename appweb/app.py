from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from datetime import datetime, date
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gestion_asistencia'
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

mysql = MySQL(app)

# Rutas principales
@app.route('/')
def index():
    if 'profesor_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM profesores WHERE email = %s", (email,))
        profesor = cur.fetchone()
        cur.close()
        
        if profesor and check_password_hash(profesor[4], password):
            session['profesor_id'] = profesor[0]
            session['profesor_nombre'] = f"{profesor[1]} {profesor[2]}"
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        
        # Verificar si el email ya existe
        cur.execute("SELECT id FROM profesores WHERE email = %s", (email,))
        if cur.fetchone():
            flash('El email ya está registrado', 'error')
            cur.close()
            return render_template('registro.html')
        
        # Crear nuevo profesor
        hashed_password = generate_password_hash(password)
        cur.execute(
            "INSERT INTO profesores (nombre, apellido, email, password) VALUES (%s, %s, %s, %s)",
            (nombre, apellido, email, hashed_password)
        )
        mysql.connection.commit()
        cur.close()
        
        flash('Registro exitoso. Puedes iniciar sesión ahora.', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/dashboard')
def dashboard():
    if 'profesor_id' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    
    # Obtener materias del profesor
    cur.execute("""
        SELECT m.nombre FROM materias m
        JOIN profesor_materia pm ON m.id = pm.materia_id
        WHERE pm.profesor_id = %s
    """, (session['profesor_id'],))
    materias = [row[0] for row in cur.fetchall()]
    
    # Obtener asistencia del día
    hoy = date.today()
    cur.execute("""
        SELECT a.fecha, a.hora_llegada, a.hora_clase, a.estado, 
               m.nombre as materia, CONCAT(c.año, '°', c.division) as curso
        FROM asistencia a
        JOIN materias m ON a.materia_id = m.id
        JOIN cursos c ON a.curso_id = c.id
        WHERE a.profesor_id = %s AND a.fecha = %s
        ORDER BY a.hora_clase
    """, (session['profesor_id'], hoy))
    asistencia_hoy = cur.fetchall()
    
    cur.close()
    
    return render_template('dashboard.html', 
                         materias=materias, 
                         asistencia_hoy=asistencia_hoy,
                         profesor_nombre=session['profesor_nombre'])

@app.route('/registrar_asistencia', methods=['GET', 'POST'])
def registrar_asistencia():
    if 'profesor_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        materia_id = request.form['materia']
        curso_id = request.form['curso']
        hora_clase = request.form['hora_clase']
        hora_llegada = request.form['hora_llegada']
        observaciones = request.form.get('observaciones', '')
        
        # Determinar si llegó temprano o tarde
        hora_clase_obj = datetime.strptime(hora_clase, '%H:%M').time()
        hora_llegada_obj = datetime.strptime(hora_llegada, '%H:%M').time()
        
        if hora_llegada_obj <= hora_clase_obj:
            estado = 'temprano'
        else:
            estado = 'tarde'
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO asistencia (profesor_id, materia_id, curso_id, fecha, 
                                   hora_llegada, hora_clase, estado, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['profesor_id'], materia_id, curso_id, date.today(),
              hora_llegada, hora_clase, estado, observaciones))
        mysql.connection.commit()
        cur.close()
        
        flash('Asistencia registrada exitosamente', 'success')
        return redirect(url_for('dashboard'))
    
    # Obtener materias y cursos para el formulario
    cur = mysql.connection.cursor()
    
    # Materias del profesor
    cur.execute("""
        SELECT m.id, m.nombre FROM materias m
        JOIN profesor_materia pm ON m.id = pm.materia_id
        WHERE pm.profesor_id = %s
    """, (session['profesor_id'],))
    materias = cur.fetchall()
    
    # Todos los cursos
    cur.execute("SELECT id, año, division FROM cursos ORDER BY año")
    cursos = cur.fetchall()
    
    cur.close()
    
    return render_template('registrar_asistencia.html', 
                         materias=materias, 
                         cursos=cursos)

@app.route('/reportes')
def reportes():
    if 'profesor_id' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    
    # Estadísticas generales
    cur.execute("""
        SELECT 
            COUNT(*) as total_clases,
            SUM(CASE WHEN estado = 'temprano' THEN 1 ELSE 0 END) as llegadas_temprano,
            SUM(CASE WHEN estado = 'tarde' THEN 1 ELSE 0 END) as llegadas_tarde,
            SUM(CASE WHEN estado = 'ausente' THEN 1 ELSE 0 END) as ausencias
        FROM asistencia 
        WHERE profesor_id = %s
    """, (session['profesor_id'],))
    stats = cur.fetchone()
    
    # Asistencia por materia
    cur.execute("""
        SELECT m.nombre, COUNT(*) as total_clases,
               SUM(CASE WHEN a.estado = 'temprano' THEN 1 ELSE 0 END) as temprano,
               SUM(CASE WHEN a.estado = 'tarde' THEN 1 ELSE 0 END) as tarde
        FROM asistencia a
        JOIN materias m ON a.materia_id = m.id
        WHERE a.profesor_id = %s
        GROUP BY m.id, m.nombre
        ORDER BY m.nombre
    """, (session['profesor_id'],))
    asistencia_materias = cur.fetchall()
    
    cur.close()
    
    return render_template('reportes.html', 
                         stats=stats, 
                         asistencia_materias=asistencia_materias)

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

# Ruta para administradores (asignar materias a profesores)
@app.route('/admin/asignar_materias', methods=['GET', 'POST'])
def asignar_materias():
    if 'profesor_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        profesor_id = request.form['profesor']
        materias = request.form.getlist('materias')
        
        cur = mysql.connection.cursor()
        
        # Eliminar asignaciones anteriores
        cur.execute("DELETE FROM profesor_materia WHERE profesor_id = %s", (profesor_id,))
        
        # Asignar nuevas materias
        for materia_id in materias:
            cur.execute("INSERT INTO profesor_materia (profesor_id, materia_id) VALUES (%s, %s)",
                       (profesor_id, materia_id))
        
        mysql.connection.commit()
        cur.close()
        
        flash('Materias asignadas exitosamente', 'success')
        return redirect(url_for('asignar_materias'))
    
    cur = mysql.connection.cursor()
    
    # Obtener todos los profesores
    cur.execute("SELECT id, nombre, apellido FROM profesores ORDER BY apellido, nombre")
    profesores = cur.fetchall()
    
    # Obtener todas las materias
    cur.execute("SELECT id, nombre FROM materias ORDER BY nombre")
    materias = cur.fetchall()
    
    cur.close()
    
    return render_template('admin_asignar_materias.html', 
                         profesores=profesores, 
                         materias=materias)

if __name__ == '__main__':
    app.run(debug=True)