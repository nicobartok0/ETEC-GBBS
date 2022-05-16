
from click import password_option
from flask import Flask, render_template, request, session, url_for, jsonify, redirect
from flask_mysqldb import MySQL

#Se define la aplicación como un objeto de la clase Flask
app = Flask(__name__)
#Configuración de servidor MySQL (CAMBIAR AL GENERAR LA APLICACIÓN FINAL)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mbbs_db'
mysql = MySQL(app)

#Ruta index (Inicio de sesión)
@app.route('/')
def Index():
    return render_template('index.html')

#Ruta principal
@app.route('/principal')
def principal():
    print(sesion)
    return render_template('principal.html')

@app.route('/user/<sesion[0]>')
def user():
    return sesion


#Ruta de registro de contacto
@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario WHERE nombre_usuario = ' + '"' + username + '"')
        usuario_existente = cur.rowcount
        cur.execute('SELECT * FROM usuario WHERE email = ' + '"' + email + '"')
        email_existente = cur.rowcount
        if usuario_existente <= 0 and email_existente <= 0:
            
            cur.execute('INSERT INTO usuario (nombre_completo, email, contraseña, nombre_usuario) VALUES (%s, %s, %s, %s)', 
            (fullname, email, password, username))
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
        autor = request.form['autor']
        titulo = request.form['titulo']
        cuerpo = request.form['cuerpo']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO foro (autor, cuerpo, titulo) VALUES (%s, %s, %s)', (autor, cuerpo, titulo))
        mysql.connection.commit()
    return forums()


#Bucle principal. La aplicación se corre en el puerto 3000.
if (__name__) == '__main__':
    app.run(port=3000, debug=True)