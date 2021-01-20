from flask import Flask, render_template, url_for, request, redirect, flash,session
from flask_mysqldb import MySQL,MySQLdb
import bcrypt
from datetime import datetime
from flask_mail import Mail, Message
import random 
import os
from werkzeug.utils import secure_filename

# client = vimeo.Client(key=YOUR_CONSUMER_KEY, secret=pHUQDGdNmCuuc3rc3/kNLwUwpS0sKTnFtJ/Koj7oUBkEwVzn9nEthf8HF4gr166536A3jHmdH5TzOrjSUaPjilD4BrKV2BiMfjoeQZ4/7T1V3DiyM87a/bg8lpoLRUzy, callback=YOUR_CALLBACK_URL)

UPLOAD_FOLDER = r'./static/img'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12300321mk'
app.config['MYSQL_DB'] = 'newdb'
mysql= MySQL(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'noreply.booksharingplatform@gmail.com'
app.config['MAIL_PASSWORD'] = '12300321mk'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
value = "global"


app.secret_key='booksharing'


@app.route('/')
def index():
    if 'username' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM category")
        category = cur.fetchall()
        return render_template("home.html",category=category)
    else:
        return redirect(url_for('home'))

@app.route('/home')
def home():
    if 'username' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM category")
        category = cur.fetchall()
        cur.execute("SELECT * FROM product ORDER BY idproduct DESC limit 3")
        products = cur.fetchall()
        flag = "false"
        user = []
        productdetails = []
        for item in products:
            cur.execute("SELECT * FROM productdetails where product_idproduct=%s",(item[0],))
            productdetails.append(cur.fetchone())
            cur.execute("SELECT * FROM user where iduser=%s",(item[5],))
            users = cur.fetchone()
            for userid in user:
                if users == userid:
                    flag="true"
            if flag == "false":
                user.append(users)
            flag="false"
        return render_template("home.html",products=products,productdetails=productdetails,user=user,category=category)
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
        isadmin = 0
        if user[1] == "kaan":
            isadmin = 1
        code = request.form['code']
        if  str(value) == str(code):
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO user (fullname,username,email,password,isadmin) VALUES(%s,%s,%s,%s,%s)',
            (user[0],user[1],user[2],user[3],isadmin))
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
                session['id'] = user['iduser']
                session['isadmin'] = user['isadmin']
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
    cur.execute("DELETE FROM comment WHERE user_iduser={0}".format(id))
    cur.execute("DELETE FROM request WHERE user_iduser={0}".format(id))
    mysql.connection.commit()
    cur.execute("SELECT *FROM product WHERE user_iduser={0}".format(id))
    product = cur.fetchall()
    for item in product:
        cur.execute("DELETE FROM comment WHERE product_idproduct=%s",(item[0],))
        cur.execute("DELETE FROM product_has_category WHERE product_idproduct=%s",(item[0],))
        mysql.connection.commit()
        cur.execute("DELETE FROM productdetails WHERE product_idproduct=%s",(item[0],))
        mysql.connection.commit()
        cur.execute("DELETE FROM product WHERE idproduct=%s",(item[0],))
        mysql.connection.commit()
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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM category")
    category = cur.fetchall()
    cur.execute("SELECT * FROM product")
    products = cur.fetchall()
    username=[]
    flag = "false"
    for item in products:
        userid = item[5]
        cur.execute("SELECT * FROM user WHERE iduser=%s",(userid,))
        user = cur.fetchone()
        if username:
            for ctrl in username:
                if user == ctrl:
                    flag = "true"
        if flag == "false":
            username.append(user)
        flag = "false"
    cur.execute("SELECT * FROM productdetails")
    productdetails = cur.fetchall()
    return render_template("product.html",category=category,products=products,productdetails=productdetails,user=username)

@app.route('/product/<id>',methods=['GET','POST'])   #category section
def products(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM category")
    category = cur.fetchall()
    
    cur.execute("SELECT * FROM product_has_category WHERE category_idcategory=%s",(id,))
    idproducts = cur.fetchall()
    products=[]
    productdetails=[]
    for item in idproducts:
        cur.execute("SELECT * FROM product Where idproduct=%s",(item[0],))
        products.append(cur.fetchone())
        cur.execute("SELECT * FROM productdetails Where product_idproduct=%s",(item[0],))
        productdetails.append(cur.fetchone())
    
    username=[]
    flag = "false"
    for item in products:
        userid = item[5]
        cur.execute("SELECT * FROM user WHERE iduser=%s",(userid,))
        user = cur.fetchone()
        if username:
            for ctrl in username:
                if user == ctrl:
                    flag = "true"
        if flag == "false":
            username.append(user)
        flag = "false"

    return render_template("product.html",category=category,products=products,productdetails=productdetails,user=username)

@app.route('/category/<id>',methods=['GET','POST'])
def category():
    cur=mysql.connection.cursor()
    cur.execute('SELECT *FROM user WHERE iduser=%s',(id))
    data = cur.fetchall()
    return "8"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/addProduct',methods=['GET','POST'])
def addProduct():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM category")
        category = cur.fetchall()
        return render_template("addProduct.html",category=category)
    else:
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        productName = request.form['ProductName']
        productPrice = request.form['ProductPrice']
        productCategory = request.form.getlist('mCategory')
        productDescription = request.form['ProductDescription']
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename1 = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            username = session['username']
            cur=mysql.connection.cursor()
            cur.execute("SELECT * FROM user WHERE username=%s",(username,))
            data = cur.fetchone()
            iduser = data[0]

            cur.execute('INSERT INTO product (name,price,image,status,user_iduser) VALUES(%s,%s,%s,%s,%s)',
            (productName,productPrice,filename1,"open",iduser))
            mysql.connection.commit()

            cur.execute("SELECT * FROM product  WHERE user_iduser=%s ORDER BY idproduct DESC limit 1",(iduser,))
            data1 = cur.fetchone()
            idproduct = data1[0]

            cur.execute('INSERT INTO productdetails (date,description,product_idproduct) VALUES(%s,%s,%s)',
            (formatted_date,productDescription,idproduct))
            mysql.connection.commit()

            for item in productCategory:
                cur.execute("SELECT * FROM category WHERE name=%s",(item,))
                category = cur.fetchone()
                idcategory = category[0]
                cur.execute('INSERT INTO product_has_category (product_idproduct,category_idcategory) VALUES(%s,%s)',
                (idproduct,idcategory))
                mysql.connection.commit()
            return redirect(url_for('product'))
        return "Error"

@app.route('/comment/<id>',methods=['GET','POST'])
def comment(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE idproduct=%s",(id,))
    product = cur.fetchone()
    cur.execute("SELECT * FROM user WHERE iduser=%s",(product[5],))
    user = cur.fetchone()
    cur.execute("SELECT * FROM productdetails WHERE product_idproduct=%s",(id,))
    productdetails = cur.fetchone()
    cur.execute("SELECT * FROM comment WHERE product_idproduct=%s",(id,))
    comment = cur.fetchall()
    cur.execute("SELECT * FROM user")
    users = cur.fetchall()
    return render_template('comment.html',products=product,productdetails=productdetails,user=user,comment=comment,users=users)

@app.route('/addComment/<id>',methods=['GET','POST'])
def addComment(id):
    if request.method == 'POST':
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        cur = mysql.connection.cursor()
        comment = request.form['comment']
        cur.execute("SELECT * FROM product WHERE idproduct=%s",(id))
        product = cur.fetchone()
        productparameter=product[0]
        username=session['username']
        cur.execute("SELECT * FROM user WHERE username=%s",(username,))
        user = cur.fetchone()
        cur.execute("SELECT * FROM productdetails WHERE product_idproduct=%s",(id))
        productdetails = cur.fetchone()
        cur.execute("SELECT * FROM user WHERE iduser=%s",(product[5],))
        user1 = cur.fetchone()
        cur.execute('INSERT INTO comment (commentext,date,user_iduser,product_idproduct) VALUES(%s,%s,%s,%s)',
        (comment,formatted_date,user[0],product[0]))
        mysql.connection.commit()
        return redirect(url_for('comment',id=productparameter))

@app.route('/request',methods=['GET','POST'])
def requ():
    if request.method == 'GET':
        return render_template("request.html")
    else:
        cur = mysql.connection.cursor()
        comment = request.form['request']
        username=session['username']
        cur.execute("SELECT * FROM user WHERE username=%s",(username,))
        user = cur.fetchone()
        cur.execute('INSERT INTO request (messagetext,user_iduser) VALUES(%s,%s)',
        (comment,user[0]))
        mysql.connection.commit()
        return redirect(url_for('home'))

@app.route('/requestList',methods=['GET','POST'])
def requestList():
    print("selam")
    arr=[]
    packet=[]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM request  ")
    req = cur.fetchall()
    for item in req:
        cur.execute("SELECT * FROM user WHERE iduser=%s",(item[2],))
        user = cur.fetchone()
        packet.append(item)
        packet[0] = packet[0] + user
        arr.append(packet)
        packet=[]
    for item in arr:
        print(item[0])
    return render_template('requestList.html',arr=arr)

if __name__ == "__main__":
    app.run(debug=True)