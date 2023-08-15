from flask import Flask
from flask import render_template, request, redirect, send_from_directory, url_for, flash
from flaskext.mysql import MySQL
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key="Develoteca"

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='127.0.0.1'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='r00t'
app.config['MYSQL_DATABASE_DB']='empleados'

mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA


@app.route('/')
def index(): 
    sql = "SELECT * FROM empleado;"
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    empleados=cursor.fetchall()
    print(empleados)
    conn.commit()
    return render_template('empleados/index.html', empleados=empleados)

@app.route('/create')
def create():    
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtcorreo']
    _foto = request.files['txtfoto']

    if _nombre == '' or _correo == '' or _foto == '' : 
        flash('Favor de llenar todos los campos')
        return redirect(url_for('create'))


    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if _foto.filename!="":  
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    sql = "INSERT INTO empleado (nombre, correo, foto) VALUES (%s, %s, %s);"
    datos=(_nombre, _correo, nuevoNombreFoto)
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql, datos)
    conn.commit() 
    return redirect('/')

@app.route('/destroy/<int:id>')
def destroy(id): 
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT foto FROM empleado WHERE id=%s", id)
    fila=cursor.fetchall() 
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
    
    cursor.execute("delete FROM empleado where id=%s", (id)) 
    conn.commit()
    return redirect('/')


@app.route('/edit/<int:id>')
def edit(id):
    sql = "SELECT * FROM empleado where id=%s"
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql, (id))
    empleados=cursor.fetchall()
    conn.commit()
    return render_template('empleados/edit.html', empleados= empleados)

@app.route('/update', methods=['POST'])
def update():
    id = request.form['txtid']
    _nombre = request.form['txtNombre']
    _correo = request.form['txtcorreo']

    _foto = request.files['txtfoto']

   
    conn = mysql.connect()
    cursor=conn.cursor()  

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if _foto.filename!="":  
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
 
        cursor.execute("SELECT foto FROM empleado WHERE id=%s", id)
        fila=cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
 
        cursor.execute("UPDATE empleado SET foto=%s WHERE id=%s", (nuevoNombreFoto, id))

    sqlUpdate = "UPDATE empleado SET nombre=%s, correo=%s  WHERE id=%s"
    datos=(_nombre, _correo, id)
    cursor.execute(sqlUpdate, datos)
    conn.commit() 
    return redirect('/')

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

if __name__ == '__main__':
    app.run(debug=True)
