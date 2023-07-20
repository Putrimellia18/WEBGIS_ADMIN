import numpy as np
from functools import wraps
from flask import Flask, request, render_template, session, redirect
from flask_mysqldb import MySQL
import pickle
import hashlib

app = Flask(__name__)
app.secret_key = '12nalnxniwemaa/zctwebcknxnsamcb'
# koneksi ke database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'kualitasair'
mysql = MySQL(app)

# model machine learning
with open("Modelknn.pkl", 'rb') as file:
    model = pickle.load(file)

with open("Scaler.pkl", 'rb') as file:
    scalerknn = pickle.load(file)

with open("Modelsvc.pkl", "rb") as file:
    model2 = pickle.load(file)
# model2 = {
#    "svc": svc,
#    "scaler": scaler
# }

with open("Modelrf.pkl", "rb") as file:
    model3 = pickle.load(file)

# model3 = {
#    "rfboost": rfboost,
#    "scaler": scaler
# }
# rf = pickle.load(open("rf.pkl", "rb"))
# svm = pickle.load(open("Modelsvm.pkl", "rb"))

# set session


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return route_function(*args, **kwargs)
        else:
            return redirect("/")  # Redirect ke halaman login jika belum login
    return wrapper


@app.route("/")
def awal():
    if 'logged_in' in session:
        return redirect("/home")  # Redirect ke halaman lain jika sudah login
    return render_template("loginadmin.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form['email']
    password = request.form['password']

    # cek data username
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM admin WHERE email=%s', (email, ))
    akun = cursor.fetchone()
    cursor.close()
    if akun:
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        if (hashed_password == akun[3]):
            session['logged_in'] = True
            session['name'] = akun[1]
            return redirect("/home")
        else:
            alert = True
            return render_template("loginadmin.html", alert="Password Anda salah")
    else:
        alert = True
        return render_template("loginadmin.html", alert="Email dan Password Anda salah")


@app.route("/home")
@login_required
def home():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) AS total_rows FROM knn WHERE kualitas = 1')
    result = cursor.fetchone()
    cursor.execute('SELECT COUNT(*) AS total_rows FROM knn WHERE kualitas = 2')
    result2 = cursor.fetchone()
    cursor.execute('SELECT COUNT(*) AS total_rows FROM knn WHERE kualitas = 3')
    result3 = cursor.fetchone()
    cursor.execute('SELECT COUNT(*) AS total_rows FROM knn WHERE kualitas = 4')
    result4 = cursor.fetchone()
    value = [result[0], result2[0], result3[0], result4[0]]
    cursor.close()
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) AS total_rows FROM svm WHERE kualitas = 1')
    result = cursor.fetchone()
    cursor.execute('SELECT COUNT(*) AS total_rows FROM svm WHERE kualitas = 2')
    result2 = cursor.fetchone()
    cursor.execute('SELECT COUNT(*) AS total_rows FROM svm WHERE kualitas = 3')
    result3 = cursor.fetchone()
    cursor.execute('SELECT COUNT(*) AS total_rows FROM svm WHERE kualitas = 4')
    result4 = cursor.fetchone()
    value2 = [result[0], result2[0], result3[0], result4[0]]
    cursor.close()
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT COUNT(*) AS total_rows FROM random WHERE kualitas = 1')
    result = cursor.fetchone()
    cursor.execute(
        'SELECT COUNT(*) AS total_rows FROM random WHERE kualitas = 2')
    result2 = cursor.fetchone()
    cursor.execute(
        'SELECT COUNT(*) AS total_rows FROM random WHERE kualitas = 3')
    result3 = cursor.fetchone()
    cursor.execute(
        'SELECT COUNT(*) AS total_rows FROM random WHERE kualitas = 4')
    result4 = cursor.fetchone()
    value3 = [result[0], result2[0], result3[0], result4[0]]
    cursor.close()
    return render_template("home.html", data=value, data2=value2, data3=value3)


@app.route("/stasiun")
@login_required
def stasiun():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM titikpantau')
    result = cursor.fetchall()
    cursor.close()
    return render_template("stasiun.html", data=result)


@app.route("/kualitasknn")
@login_required
def kualitasknn():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM titikpantau LEFT JOIN knn ON knn.id=titikpantau.id")
    result = cursor.fetchall()
    cursor.close()
    return render_template("kualitasknn.html", data=result)


@app.route("/editkualitasknn/<id>")
@login_required
def editkualitasknn(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO knn (id) VALUES (%s)', (id,))
        mysql.connection.commit()
        cursor.close()
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM knn WHERE id=%s', (id,))
        result = cursor.fetchone()
        cursor.close()
        return render_template("formeditkualitasknn.html", data=result)
    except Exception as e:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM knn WHERE id=%s', (id, ))
        result = cursor.fetchone()
        cursor.close()
        return render_template("formeditkualitasknn.html", data=result)


@app.route("/successeditkualitasknn", methods=["POST"])
@login_required
def successeditkualitasknn():
    id = request.form['id']
    ph = request.form['ph']
    tss = request.form['tss']
    do = request.form['do']
    bod = request.form['bod']
    cod = request.form['cod']
    nitrat = request.form['nitrat']
    fecal = request.form['fecal']
    fosfat = request.form['fosfat']
    features = np.array([[ph, tss, do, bod, cod, nitrat, fecal, fosfat]])
    data = scalerknn.transform(features)
    prediction = model.predict(data)
    result = int(prediction)
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE knn SET kualitas=%s WHERE id=%s", (result, id))
    mysql.connection.commit()
    cursor.close()
    return redirect("/kualitasknn")


@app.route("/kualitassvm")
@login_required
def kualitassvm():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM titikpantau LEFT JOIN svm ON svm.id=titikpantau.id")
    result = cursor.fetchall()
    cursor.close()
    return render_template("kualitassvm.html", data=result)


@app.route("/editkualitassvm/<id>")
@login_required
def editkualitassvm(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO svm (id) VALUES (%s)', (id,))
        mysql.connection.commit()
        cursor.close()
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM svm WHERE id=%s', (id,))
        result = cursor.fetchone()
        cursor.close()
        return render_template("formeditkualitassvm.html", data=result)
    except Exception as e:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM svm WHERE id=%s', (id, ))
        result = cursor.fetchone()
        cursor.close()
        return render_template("formeditkualitassvm.html", data=result)


@app.route("/successeditkualitassvm", methods=["POST"])
@login_required
def successeditkualitassvm():
    id = request.form['id']
    ph = request.form['ph']
    tss = request.form['tss']
    do = request.form['do']
    bod = request.form['bod']
    cod = request.form['cod']
    nitrat = request.form['nitrat']
    fecal = request.form['fecal']
    fosfat = request.form['fosfat']
    features = np.array([[ph, tss, do, bod, cod, nitrat, fecal, fosfat]])
    data = scalerknn.transform(features)
    prediction = model2.predict(data)
    result = int(prediction)
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE svm SET kualitas=%s WHERE id=%s", (result, id))
    mysql.connection.commit()
    cursor.close()
    return redirect("/kualitassvm")


@app.route("/kualitasrf")
@login_required
def kualitasrf():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM titikpantau LEFT JOIN random ON random.id=titikpantau.id")
    result = cursor.fetchall()
    cursor.close()
    return render_template("kualitasrf.html", data=result)


@app.route("/editkualitasrf/<id>")
@login_required
def editkualitasrf(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO random (id) VALUES (%s)', (id,))
        mysql.connection.commit()
        cursor.close()
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM random WHERE id=%s', (id,))
        result = cursor.fetchone()
        cursor.close()
        return render_template("formeditkualitasrf.html", data=result)
    except Exception as e:
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM random WHERE id=%s', (id, ))
        result = cursor.fetchone()
        cursor.close()
        return render_template("formeditkualitasrf.html", data=result)


@app.route("/successeditkualitasrf", methods=["POST"])
@login_required
def successeditkualitasrf():
    id = request.form['id']
    ph = request.form['ph']
    tss = request.form['tss']
    do = request.form['do']
    bod = request.form['bod']
    cod = request.form['cod']
    nitrat = request.form['nitrat']
    fecal = request.form['fecal']
    fosfat = request.form['fosfat']
    features = np.array([[ph, tss, do, bod, cod, nitrat, fecal, fosfat]])
    data = scalerknn.transform(features)
    prediction = model3.predict(data)
    result = int(prediction)
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE random SET kualitas=%s WHERE id=%s", (result, id))
    mysql.connection.commit()
    cursor.close()
    return redirect("/kualitasrf")


@app.route("/formknn")
@login_required
def formknn():
    return render_template("knnpredict.html")


@app.route("/knnpredict", methods=["POST"])
@login_required
def knnpredict():
    float_features = [float(x) for x in request.form.values()]
    features = np.array([float_features])
    data = scalerknn.transform(features)
    prediction = model.predict(data)
    hasil = int(prediction)
    return render_template("knnpredict.html", hasil=hasil)


@app.route("/formsvm")
@login_required
def formsvm():
    return render_template("svmpredict.html")


@app.route("/svmpredict", methods=["POST"])
@login_required
def svmpredict():
    float_features = [float(x) for x in request.form.values()]
    features = np.array(float_features)
    data = scalerknn.transform(features)
    prediction = model2.predict(data)
    hasil = int(prediction)
    return render_template("svmpredict.html", hasil=hasil)


@app.route("/formrf")
@login_required
def formrf():
    return render_template("rfpredict.html")


@app.route("/rfpredict", methods=["POST"])
@login_required
def rfpredict():
    float_features = [float(x) for x in request.form.values()]
    features = [np.array(float_features)]
    data = scalerknn.transform(features)
    prediction = model3.predict(data)
    hasil = int(prediction)
    return render_template("rfpredict.html", hasil=hasil)


@app.route("/tambahdata")
@login_required
def tambahdata():
    return render_template("formcreate.html")


@app.route("/create", methods=["POST"])
@login_required
def create():
    sungai = request.form['sungai']
    stasiun = request.form['stasiun']
    alamat = request.form['alamat']
    lon = request.form.get('longitude')
    lat = request.form.get('latitude')

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO titikpantau (nama_sungai, nama_stasiun, alamat, longitude, latitude ) VALUES (%s, %s, %s, %s, %s)",
                   (sungai, stasiun, alamat, lon, lat))
    mysql.connection.commit()
    cursor.close()
    return redirect("/stasiun")


@app.route("/delete/<id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM titikpantau WHERE titikpantau.id =%s ", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect("/stasiun")


@app.route("/formedit")
@login_required
def formedit():
    return render_template("formedit.html")


@app.route("/edit/<id>")
@login_required
def edit(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM titikpantau WHERE id=%s', (id,))
    result = cursor.fetchone()
    cursor.close()
    return render_template("formedit.html", data=result)


@app.route("/successedit", methods=["POST"])
@login_required
def successedit():
    id = request.form['id']
    sungai = request.form['sungai']
    stasiun = request.form['stasiun']
    alamat = request.form['alamat']
    lon = request.form.get('longitude')
    lat = request.form.get('latitude')

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE `titikpantau` SET nama_sungai=%s, nama_stasiun =%s, alamat = %s, longitude= %s, latitude= %s WHERE id=%s",
                   (sungai, stasiun, alamat, lon, lat, id))
    mysql.connection.commit()
    cursor.close()
    return redirect("/stasiun")


@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
