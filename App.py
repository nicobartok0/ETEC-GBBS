from click import password_option
from flask import Flask, render_template, request, url_for
from flask_mysqldb import MySQL

#Se define la aplicación como un objeto de la clase Flask
app = Flask(__name__)
#Configuración de servidor MySQL (CAMBIAR AL GENERAR LA APLICACIÓN FINAL)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mbbs_db'
mysql = MySQL(app)

#Ruta principal
@app.route('/')
def Index():
    return render_template('index.html')

#Ruta de registro de contacto
@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        password = request.form['password']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO usuario (nombre_usuario, email, contraseña) VALUES (%s, %s, %s)', 
        (fullname, email, password))
        mysql.connection.commit()
        return render_template('index.html')


    


#Bucle principal. La aplicación se corre en el puerto 3000.
if (__name__) == '__main__':
    app.run(port=3000, debug=True)