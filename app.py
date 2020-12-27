from flask import Flask, render_template, url_for, request, redirect, flash,session
from flask_mysqldb import MySQL,MySQLdb
import bcrypt
from flask_mail import Mail, Message
import random 
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '*'
app.config['MYSQL_DB'] = 'newdb'
mysql= MySQL(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'noreply.booksharingplatform@gmail.com'
app.config['MAIL_PASSWORD'] = '*'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
value = "global"


app.secret_key='booksharing'

@app.route('/')
def index():
    if 'username' in session:
        return render_template("home.html")
    else:
        return render_template("index.html")

@app.route('/home')
def home():
    if 'username' in session:
        return render_template("home.html")
    else:
        return render_template("index.html")


@app.route('/sign_up',methods=['GET','POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('sign_up.html')
    else:
        fullname=request.form['fullname']
        username=request.form['username']
        emailitü=request.form['email']
        mailtag="@itu.edu.tr"
        email=emailitü+mailtag
        msg = Message('BookSharing Platform', sender = 'noreply.booksharingplatform@gmail.com', recipients = [email])
        global value
        value = random.randint(1000,9999)
        msg.body = str(value)
        mail.send(msg)
        password=request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password,bcrypt.gensalt())
        user = [fullname,username,email,hash_password]
        session['user'] = user
        return redirect(url_for('confirmation'))

@app.route('/confirmation',methods=['GET','POST'])
def confirmation():
    if request.method == 'GET':
        return render_template('confirmation.html')
    else:
        user = session['user']
        code = request.form['code']
        if  str(value) == str(code):
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO user (fullname,username,email,password) VALUES(%s,%s,%s,%s)',
            (user[0],user[1],user[2],user[3]))
            mysql.connection.commit()
            flash('You were successfully registered',"success")
            session.clear()
            return redirect(url_for('sign_in'))
        else:
            flash('You entered the verification code incorrectly',"danger")
            return render_template('sign_up.html')

@app.route('/sign_in',methods=['GET','POST'])
def sign_in():
    if request.method == 'GET':
        return render_template('sign_in.html')
    else:
        error = None
        error2 = None
        user = None
        session.permanent = True
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM user WHERE username=%s",(username,))
        user = cur.fetchone()
        cur.close()
        if  user:
            if bcrypt.hashpw(password,user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
                session['username'] = user['username']
                flash('You were successfully logged in',"success")
                return redirect(url_for('home'))
            else:
                error2 = 'Invalid password'
                flash('Wrong password',"danger")
                return render_template("sign_in.html",error2=error2,username=username)
        else:
            error = 'Invalid username'
            flash('Wrong username',"danger")
            return render_template("sign_in.html",error=error,username=username)

@app.route('/log_out') 
def log_out():
    session.clear()
    flash('You were successfully logged out',"success")
    return redirect(url_for('index'))  

@app.route('/profile',methods=['GET','POST'])
def profile():
    username=session['username']
    cur = mysql.connection.cursor()
    cur.execute("SELECT *FROM user WHERE username=%s",(username,))
    data = cur.fetchone()
    return render_template('profile.html', datas=data)

@app.route('/delete/<string:id>')
def delete(id):
    cur=mysql.connection.cursor()
    cur.execute('DELETE FROM user WHERE iduser={0}'.format(id))
    mysql.connection.commit()
    session.clear()
    flash('You were successfully deleted account',"success")
    return redirect(url_for('index'))

@app.route('/edit/<id>')
def edit(id):
    cur=mysql.connection.cursor()
    cur.execute('SELECT *FROM user WHERE iduser=%s',(id))
    data = cur.fetchall()
    return render_template('edit.html',datas=data[0])

@app.route('/update_account/<id>',methods=['POST'])
def update_account(id):
    if request.method == 'POST':
        fullname=request.form['fullname']
        username=request.form['username']
        email=request.form['email']
        password=request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password,bcrypt.gensalt())
        cur=mysql.connection.cursor()
        cur.execute("""
        UPDATE user 
        SET fullname=%s,
            username=%s,
            email=%s,
            password=%s 
            WHERE iduser=%s """,
        (fullname,username,email,hash_password,id))
        mysql.connection.commit()
        flash('You were successfully updated account',"success")
        session['username']=username
        return redirect(url_for('profile'))

@app.route('/product',methods=['GET','POST'])
def product():
    return render_template("product.html")

if __name__ == "__main__":
    app.run(debug=True)
