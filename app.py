#Importamos las librerias de flask para poder ver el contenido de los archivos 
from flask import Flask
#render_template = poder visualizar los html. request = peticion de datos a travez del html,redirect = redireccionar, url_for = ver imagenes en edit, flash para enviar mensajes
from flask import render_template,request,redirect,url_for,flash
#Importamos libreria para trabajar con mySQL
from flaskext.mysql import MySQL
#para poder mostrar las fotos con flask
from flask import send_from_directory
#para cambiar el nombre de las fotos y no se repitan los nombres/crear un nuevo nombre diferente al anterior en funcion al tiempo
from datetime import datetime
#nos permite entrar a ls carpeta uploads para poder eliminar los archivos
import os



#creamos la primea aplicacion
app = Flask(__name__)
app.secret_key = "Crud_py"


#conexion a base de datos
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = "localhost"
app.config['MYSQL_DATABASE_USER'] = "usuario"
app.config['MYSQL_DATABASE_PASSWORD'] = "12345678"
app.config['MYSQL_DATABASE_DB'] = "crud_python"
mysql.init_app(app)



#creamos una referencia a la carpeta donde se suben las fotos para accedeer a ella
CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

#creamos acceso para la URL para ver imagenes
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)


#creamos routeo, recibe solicitudes mediante url
@app.route('/')
def index():
#Generamos instrucciones sql para hacer pruebas de conectivodad
    sql = "SELECT * FROM empleados;"
    #conexion a basa de datos
    conn = mysql.connect()
    #almacena informacion
    cursor = conn.cursor()
    #ejecuta la sentencia sql
    cursor.execute(sql)
#selecciona todos los registros 
    empleados = cursor.fetchall()
    #da por hecho que la sentencia fue exitosa 
    conn.commit()
    #envio de datos a travez de render template con la variable empleados
    return render_template('index.html', empleados = empleados)

@app.route('/empleados')
def empleados():
    sql = "SELECT * FROM empleados;"
    #conexion a basa de datos
    conn = mysql.connect()
    #almacena informacion
    cursor = conn.cursor()
    #ejecuta la sentencia sql
    cursor.execute(sql)
#selecciona todos los registros 
    empleados = cursor.fetchall()
    #da por hecho que la sentencia fue exitosa 
    conn.commit()
    #envio de datos a travez de render template con la variable empleados
    return render_template('empleados.html', empleados = empleados)

#ruta para eliminar elementos de la base de datos
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()
#eliminar fot de la carpeta
    cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
    fila = cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
    cursor.execute('DELETE FROM empleados WHERE id = %s',(id))
    conn.commit()
    return redirect('/empleados')

#enviar la informacion a editar 
@app.route('/edit/<int:id>')
def edit(id):

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM empleados WHERE id = %s', (id))
    empleados = cursor.fetchall()
    conn.commit()
    return render_template('edit.html', empleados = empleados)






@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id = request.form['txtID']

    sql = "UPDATE  empleados SET nombre = %s, correo = %s WHERE id = %s";

    datos = (_nombre,_correo,id)

    conn = mysql.connect()
    cursor = conn.cursor()

#para actualizar la foto
    now = datetime.now()
    tiempo = now.strftime('%Y%H%M%S')

    if _foto.filename != '':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save('app/uploads/' + nuevoNombreFoto)

#Buscamos como se llama esa foto para poder removerla si s necesario
        cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
        fila = cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto,id))
        conn.commit()



    cursor.execute(sql,datos)
    conn.commit()

    return redirect('empleados')

#llamamos a la vista del html con el render template
@app.route('/create')
def create():
    return render_template('create.html')

#ruta en donde llegara la informacion enviada a travez del metodo POST desde el formulario 
@app.route('/store', methods=['POST'])
def storage():
#Recepcionamos los datos que nos envia el create.html
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
#para el tipo de archivo imagen utilizamos .files
    _foto = request.files['txtFoto']
#validacion
    if _nombre == '' or _correo == '' or _foto == '':
        flash('Campos Obligatorios')
        return redirect(url_for('create'))
#concatenamos el tiempo al nombre de la foto
    #almacena el iempo actual
    now = datetime.now()
    #depende del tiempo y se convierte en formato determinado (años,horas,mes,segundos)
    tiempo = now.strftime('%Y%H%M%S')
    #si no esta vacio el input foto, obtenemos el nombre generado por la variable tiempo  
    if _foto.filename != '':
        #se la concatenamos al nombre de la foto con el fin de que no se sobreescriba una foto anterior
        nuevoNombreFoto = tiempo + _foto.filename
        #guardamos la foto en la carpeta pertinente(esta varia segun desde la carpeta que se abra) 
        _foto.save('app/uploads/' + nuevoNombreFoto)

#utilizamos una variable datos para realizar el remplazo de los datos en la sentencia sql, en img agregamos el nuevo nombre de la foto generadoa arriba
    datos = [_nombre,_correo,nuevoNombreFoto]

#insercion en base de datos de los valores solicitados, se utiliza un %s para indicar que los datos se agrgaran desde la vaiable datos
    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s)";
    conn = mysql.connect()
    cursor = conn.cursor()
    #agregamos la variable datos para que los tome en cuenta la sentencia sql
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/empleados')

#punto de entrada de la app, en modo debug para ver que pasa en tiempo real
if __name__ == "__main__":
    app.run(debug=True)