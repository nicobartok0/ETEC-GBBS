
from fileinput import filename
from click import password_option
import os
from flask_socketio import SocketIO, send
from flask import Flask, render_template, request, session, url_for, jsonify, redirect
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename

#Se define la aplicación como un objeto de la clase Flask
app = Flask(__name__)
#Se define la carpeta donde se pueden subir archivos de imagen para las fotos de perfil
app.config['UPLOAD_FOLDER'] = './static/img'
#Configuración de servidor MySQL (CAMBIAR AL GENERAR LA APLICACIÓN FINAL)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gbbs_db'
mysql = MySQL(app)
socketio = SocketIO(app)

#Ruta index (Inicio de sesión)
@app.route('/')
def Index():
    return render_template('index.html')

#Ruta principal
@app.route('/principal')
def principal():
    print(sesion)
    return render_template('principal.html')

@app.route('/user') 
def usuario_():
    cur = mysql.connection.cursor()
    cur.execute('SELECT foto_perfil FROM usuario WHERE nombre_usuario = ' + '"' + sesion[4] + '"')
    filename = cur.fetchone()
    foto_perfil = filename[0]
    print(foto_perfil)
    return render_template('usuario.html', nombre = sesion[1], email = sesion[2], nombre_usuario = sesion[4], foto_perfil = foto_perfil )

@app.route('/users')
def usuarios_():
    cur = mysql.connection.cursor()
    cur.execute('SELECT nombre_usuario FROM usuario')
    nombres = cur.fetchall()
    cur.execute('SELECT foto_perfil FROM usuario')
    fotos = cur.fetchall()
    print(fotos)
    return render_template("usuarios.html", nombres = nombres, fotos = fotos)


@app.route('/subir_foto_de_perfil', methods=['POST'])
def subir_foto_de_perfil():
    if request.method == 'POST':
        # obtenemos el archivo del input "archivo"
        f = request.files['archivo']
        filename = secure_filename(f.filename)
        # Guardamos el archivo en el directorio "/static/img"
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #Guardamos la ruta del archivo en una variable global llamada foto_perfil.
        global foto_perfil
        foto_perfil = url_for('static', filename='img/' + filename)
        cur = mysql.connection.cursor()
        cur.execute('UPDATE usuario SET foto_perfil = ' + '"' + foto_perfil + '"' + ' WHERE nombre_usuario = ' + '"' + sesion[4] + '"')
        mysql.connection.commit()
        print(filename)
        print(foto_perfil)
        
        # Retornamos una respuesta satisfactoria
        return render_template('usuario.html', nombre = sesion[1], email = sesion[2], nombre_usuario = sesion[4], foto_perfil = foto_perfil)
        

#Ruta de registro de contacto
@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        default_pfp = url_for('static', filename='img/default-A.png')
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario WHERE nombre_usuario = ' + '"' + username + '"')
        usuario_existente = cur.rowcount
        cur.execute('SELECT * FROM usuario WHERE email = ' + '"' + email + '"')
        email_existente = cur.rowcount
        if usuario_existente <= 0 and email_existente <= 0:
            
            cur.execute('INSERT INTO usuario (nombre_completo, email, contraseña, nombre_usuario, foto_perfil) VALUES (%s, %s, %s, %s, %s)', 
            (fullname, email, password, username, default_pfp))
            mysql.connection.commit()
            return render_template('index.html')
        else:
            return render_template('ex_user_already_exists.html')

#Ruta de inicio de sesión
@app.route('/sign_in', methods=['POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario WHERE nombre_usuario =' + '"' + username + '"' + "AND contraseña =" + '"' + password + '"')
        usuario_existente = cur.rowcount
        if usuario_existente <= 0:
            return render_template('ex_user_doesnt_exist.html')
        else:
            cur.execute('SELECT * FROM usuario WHERE nombre_usuario=' + '"' + username + '"')
            global sesion
            sesion = cur.fetchone()
            cur.execute('SELECT foto_perfil FROM usuario WHERE nombre_usuario=' + '"' + username + '"')
            global foto_perfil
            foto_perfil = cur.fetchall()
            print(foto_perfil, "test")
            return redirect(url_for('principal'))

#Ruta para mostrar todos los foros
@app.route('/forums')
def forums():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM foro')
    data = cur.fetchall()
    return render_template('foros.html', foros = data)

#Ruta para mostrar un foro específico
@app.route('/forum/<id>')
def forum(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM foro WHERE id =' + '"' + id + '"')
    data = cur.fetchone()
    return render_template('plantilla_foro.html', titulo_foro = data[3], cuerpo_foro = data[2])

#Ruta para añadir un foro
@app.route('/add_forums', methods=['POST'])
def add_forums():
    if request.method == 'POST':
        autor = sesion[4]
        titulo = request.form['titulo']
        cuerpo = request.form['cuerpo']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO foro (autor, cuerpo, titulo) VALUES (%s, %s, %s)', (autor, cuerpo, titulo))
        mysql.connection.commit()
    return forums()

#Ruta de Correo
@app.route('/correo')
def usuario():
    return render_template('correo.html')


@app.route('/chat', methods=['GET', 'POST'])
def sessions():
    return render_template('session.html', nombre_usuario = sesion[4])

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)


#Bucle principal. La aplicación se corre en el puerto 3000.
if (__name__) == '__main__':
    app.run(port=3000, debug=True)
    socketio.run(app, debug=True)