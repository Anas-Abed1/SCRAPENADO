from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import re
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous  import SignatureExpired,URLSafeTimedSerializer
from datetime import timedelta,datetime
from bs4 import BeautifulSoup
import requests
import json

app = Flask(__name__)
conn = mysql.connector.connect(
    host="localhost",
    database="flaskproject",
    user="root",
    password="" )
app.secret_key = "super secret key"
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'yusefamassi9@gmail.com'
app.config['MAIL_PASSWORD'] = 'nghknsbjqduubdfk'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#Creating a connection cursor
with app.app_context():
    cur = conn.cursor()


@app.route("/")
def home():
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM information_contact')
    information_contact = cur.fetchone()
    session['email'] =information_contact['email']
    session['phone'] =   information_contact['phone']
    session['Address'] = information_contact['Address']
    session['time_work'] = information_contact['time_work']

    return render_template("home.html")

@app.route('/home')
def home1():
    return redirect(url_for('home'))
@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/About")
def About():
    return render_template("About.html")


@app.route("/Pricing")
def Pricing():
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT * FROM plan')
    Allplan = cur.fetchall()
    cur.execute('SELECT * FROM featuresforplan')
    featuresforplan = cur.fetchall()
    cur.execute('SELECT * FROM features')
    features = cur.fetchall()
    return render_template("pricing.html",Allplan=Allplan,featuresforplan=featuresforplan,features=features)

@app.route('/Allusers', methods = ['POST', 'GET'])
def Allusers():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM users')
        Allusers = cur.fetchall()
        return render_template('dashAdmin/Allusers.html', Allusers=Allusers)
    else:
        return msg


@app.route('/Plans', methods = ['POST', 'GET'])
def AllPlan():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method=="GET":
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM plan')
            Allplan = cur.fetchall()
            cur.execute('SELECT * FROM featuresforplan')
            featuresforplan=cur.fetchall()
            cur.execute('SELECT * FROM features')
            features=cur.fetchall()
            return render_template('dashAdmin/Allplan.html',Allplan=Allplan,featuresforplan=featuresforplan,features=features)
        else:
            msg="the plans not showing because the request method is post change to get"
            return render_template('dashAdmin/Allplan.html',msg=msg)
    else:
        return msg

@app.route('/ShowMessages', methods = ['POST', 'GET'])
def ShowMessagesfromuser():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == "GET":
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM messages')
            Allmessages = cur.fetchall()
            return render_template('dashAdmin/ShowMessagesfromuser.html', Allmessages=Allmessages)
        else:
            msg = "the plans not showing because the request method is post change to get"
            return render_template('dashAdmin/Allplan.html', msg=msg)
    else:
        return msg

@app.route('/AddFeatureForPlan', methods = ['POST', 'GET'])
def AddFeatureForPlan():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method=="GET" and 'plan_id' in request.args:
            plan_id=request.args['plan_id']
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM features')
            features = cur.fetchall()
            return render_template('dashAdmin/AddFeatureForPlan.html',plan_id=plan_id ,features=features)
        if request.method == "POST" and 'plan_id' in request.form and 'plan_id' in request.form and "features" in request.form:
            plan_id=request.form['plan_id']
            features=request.form.getlist('features')
            for item in features:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO featuresforplan (feature_id, plan_id) VALUES (%s, %s)",
                    [item, plan_id]
                )

            msg = 'You have successfully Add new features for plan  !'

            return redirect(url_for('AllPlan', msg=msg, plan_id=plan_id))
    else:
        return msg


@app.route('/AddPlan', methods = ['POST', 'GET'])
def AddPlan():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == 'POST' and 'name' in request.form and 'price' in request.form and 'duration' in request.form :
            name = request.form['name']
            price = request.form['price']
            duration = request.form['duration']
            cur = conn.cursor()
            cur.execute('SELECT * FROM plan WHERE price =%s and duration=%s', (price, duration,))
            plan = cur.fetchone()
            if plan:
                msg = "this plan is already exists"
                return redirect(url_for('AllPlan', msg=msg))
            else:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO plan(name, price, duration) VALUES(%s, %s, %s)",
                    [name, price, duration,])
                plan_id=cur.getlastrowid()
                msg = 'You have successfully Add new plan !'
                return redirect(url_for('AddFeatureForPlan', msg=msg ,plan_id=plan_id))
        else:
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM features')
            features = cur.fetchall()
            return render_template('dashAdmin/AddPlan.html',features=features)
@app.route('/EditPlan', methods = ['POST', 'GET'])
def EditPlan():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == 'POST' and 'name' in request.form and 'price' in request.form and 'duration' in request.form and 'plan_id' in request.form :
            plan_id=request.form['plan_id']
            name = request.form['name']
            price = request.form['price']
            duration = request.form['duration']
            cur = conn.cursor()
            cur.execute("UPDATE plan SET name =%s, price =%s ,duration=%s WHERE plan_id =%s",
                        (name, price, duration, plan_id,))
            msg="the plan edited successfully"
            return redirect(url_for('AddFeatureForPlan', msg=msg, plan_id=plan_id))
        else:
            cur = conn.cursor(dictionary=True)
            plan_id=request.args['plan_id']
            cur.execute('SELECT * FROM plan WHERE plan_id =%s ', (plan_id,))
            plan = cur.fetchone()
            return render_template('dashAdmin/EditPlan.html', plan=plan)
@app.route('/Deleteplan', methods = ['POST', 'GET'])
def Deleteplan():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == "POST" and 'plan_id' in request.form :
            plan_id = request.form['plan_id']
            cur = conn.cursor(dictionary=True)
            cur.execute('Delete  FROM plan where plan_id=%s', (plan_id,))
            cur.execute('Delete  FROM featuresforplan where plan_id=%s', (plan_id,))
            msg="the plan deleted successfully"
            return redirect(url_for('AllPlan', msg=msg))
        else:
            msg="the plan not deleted successfully"
            return redirect(url_for('AllPlan', msg=msg))
@app.route('/Addusers', methods = ['POST', 'GET'])
def Addusers():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'confirmPassword' in request.form and 'picture' in request.files  :
            name = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirmPassword = request.form['confirmPassword']
            file = request.files['picture']
            if file.filename == '':
                msg='No image selected for uploading'
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur = conn.cursor()
            cur.execute('SELECT * FROM users WHERE email = %s', (email, ))
            account = cur.fetchone()
            if account :
                msg = 'Account already exists !'
                return render_template('register.html',msg=msg)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
                return render_template('register.html', msg=msg)
            elif not re.match(r'[A-Za-z0-9]+', name):
                msg = 'Username must contain only characters and numbers !'
                return render_template('register.html', msg=msg)
            elif not name or not password or not email:
                msg = 'Please fill out the form !'
                return render_template('dashAdmin/Adduser.html', msg=msg)
            else:
                cur.execute("INSERT INTO users(username, email, image,password, confirmPassword) VALUES(%s, %s, %s, %s, %s,)",
                            [name, email, filename, password, confirmPassword])
                conn.commit()
                msg = 'You have successfully Add new user !'
                cur.close()
                return redirect(url_for('Allusers',msg=msg))
        else:
            return render_template('dashAdmin/Adduser.html')
    else:
        msg='You need to log in '
        return msg



@app.route('/Editusers', methods = ['POST', 'GET'])
def Editusers():
    msg="you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == "GET" and 'user_id' in request.args :
            user_id = request.args['user_id']
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM users where user_id=%s', (user_id,))
            oneuser = cur.fetchone()
            return render_template('dashAdmin/EditUser.html',oneuser=oneuser)
        if request.method == "POST" and 'email' in request.form and 'username' in request.form and 'user_id' in request.form and 'picture' in request.files:
            cur = conn.cursor(dictionary=True)
            user_id = request.form['user_id']
            username = request.form['username']
            email = request.form['email']
            file = request.files['picture']
            if file.filename == '':
                msg = 'No image selected for uploading'
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("UPDATE users SET email = %s, username = %s ,image=%s WHERE user_id = %s",
               (email, username, filename, user_id,))
            return redirect(url_for('Allusers'))
    else:
        msg = "the user not edited successfully"
        return redirect(url_for('AllPlan', msg=msg))


@app.route('/Deleteuser', methods = ['POST', 'GET'])
def Deleteusers():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == "POST" and 'user_id' in request.form :
            user_id = request.form['user_id']
            cur = conn.cursor(dictionary=True)
            cur.execute('Delete  FROM users where user_id=%s', (user_id,))
            return redirect(url_for('Allusers'))
        else:
            msg = "the user not deleted successfully"
            return redirect(url_for('Allusers', msg=msg))
    else:
        return msg

@app.route("/login", methods = ['POST', 'GET'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM users WHERE email = %s ', (email, ))
        account = cur.fetchone()

        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['user_id']
            session['username'] = account['username']
            session['image'] = account['image']
            session['type'] = account['type']
            msg = 'Logged in successfully !'
            if  'type' in session and session['type'] == "ADM":
                return redirect(url_for('Allusers', msg=msg))
            else:
                return redirect(url_for('Dashboard', msg=msg))
        else:
            msg = 'Incorrect username / password !'
            return render_template('login.html', msg=msg)
    if request.method == 'GET' and 'loggedin' in session:
        if  'type' in session and session['type'] == "ADM":
                return redirect(url_for('Allusers', msg=msg))
        else:
                return redirect(url_for('Dashboard', msg=msg))
    elif request.method == 'GET'  :
        return render_template('login.html')


@app.route('/logout',methods = ['POST'])
def logout():
    session.pop('loggedin', False)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register')
def form():
    return render_template('register.html')

@app.route('/register', methods = ['POST', 'GET'])
def register():
    msg = ''
    if request.method == 'GET' :
        return "register via the register Form"
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'confirmPassword' in request.form  :
        name = request.form['username']
        email = request.form['email']
        password =generate_password_hash(request.form['password'])
        confirmPassword = generate_password_hash(request.form['confirmPassword'])
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE email = %s', (email, ))
        account = cur.fetchone()
        if account :
            msg = 'Account already exists !'
            return render_template('register.html',msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
            return render_template('register.html', msg=msg)
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Username must contain only characters and numbers !'
            return render_template('register.html', msg=msg)
        elif not name or not password or not email:
            msg = 'Please fill out the form !'
            return render_template('register.html', msg=msg)
        else:
            cur.execute("INSERT INTO users(username, email, password, confirmPassword,plan_id) VALUES(%s, %s, %s, %s,%s)",
                        [name, email, password, confirmPassword,1])
            conn.commit()
            msg = 'You have successfully registered !'
            cur.close()
            return redirect(url_for('login',msg=msg))


@app.route('/Contact', methods = ['POST', 'GET'])
def ActionContact():

    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'subject' in request.form and 'message' in request.form  :
        name=request.form['name']
        email=request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        cur = conn.cursor()
        cur.execute("INSERT INTO messages(name, email, subject, message) VALUES(%s, %s, %s, %s)",
                    [name, email, subject, message])
        conn.commit()
        msg = 'You have sent message successfully !'
        cur.close()
        return render_template('home.html',msg=msg)
    else:
        msg='There is an error message was not sent !'
        return render_template('home.html',msg=msg)
@app.route('/sendmessage', methods = ['POST', 'GET'])
def sendmessagetouser():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == "GET" and 'email' in request.args :
            email=request.args['email']
            return render_template("dashAdmin/sendmessagetouser.html",email=email)
        if request.method == "POST" and "title" in request.form and "body" in request.form and "email" in request.form:
            title=request.form['title']
            body=request.form['body']
            email=request.form['email']
            msg = Message(title, sender='yusefamassi@gmail.com', recipients=[email])
            msg.body = body
            mail.send(msg)
            return render_template("dashAdmin/messagesendsuccsess.html")
    else:
        return msg
@app.route('/information_contact', methods = ['GET','POST'])
def information_contact():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == "GET":
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM information_contact')
            information_contact = cur.fetchall()
            return render_template('dashAdmin/information_contact.html',information_contact=information_contact)
        else:
            msg = "the plans not showing because the request method is post change to get"
            return render_template('dashAdmin/Allplan.html', msg=msg)
    else:
        return msg
@app.route('/Actioninformation_contact', methods = ['POST', 'GET'])
def ActionInfor_contact():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == "POST" and "email" in request.form and "phone" in request.form and "Address" in request.form and "time_work" in request.form:
            email=request.form['email']
            phone = request.form['phone']
            Address = request.form['Address']
            time_work=request.form['time_work']
            cur = conn.cursor()
            cur.execute("INSERT INTO information_contact(email, phone,Address, time_work) VALUES(%s, %s, %s, %s)",
                        [email, phone,  Address, time_work])
            conn.commit()
            msg = 'You have sent message successfully !'
            cur.close()
            return render_template('dashAdmin/information_contact.html', msg=msg)
        else:
            return render_template('dashAdmin/AddInforContact.html')
    else:
        return msg
@app.route('/features', methods = ['POST', 'GET'])
def Allfeatures():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method=="GET":
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM features')
            features = cur.fetchall()
            return  render_template('dashAdmin/Features.html',features=features)
        if request.method=="POST":
            return "This page need get method"

@app.route('/AddNewfeature', methods = ['POST', 'GET'])
def AddNewfeature():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == "POST" and "feature_name" in request.form:
            feature_name=request.form['feature_name']
            cur = conn.cursor()
            cur.execute('Insert into features (feature_name) VALUES(%s)', (feature_name,))
            conn.commit()
            msg = 'You have sent message successfully !'
            cur.close()
            return redirect(url_for('Allfeatures'))
        else:
            return render_template('dashAdmin/AddNewfeature.html')
    else:
        return msg


@app.route('/Editfeature', methods = ['POST', 'GET'])
def Editfeature():
    msg="you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == "GET" and 'feature_id' in request.args :
            feature_id = request.args['feature_id']
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM features where feature_id=%s', (feature_id,))
            feature = cur.fetchone()
            return render_template('dashAdmin/Editfeature_id.html',feature=feature)
        if request.method == "POST" and 'feature_name' in request.form and 'feature_id' in request.form:
            cur = conn.cursor(dictionary=True)
            feature_id = request.form['feature_id']
            feature_name = request.form['feature_name']

            cur.execute("UPDATE features SET feature_name = %s WHERE feature_id = %s",
               (feature_name, feature_id, ))
            return redirect(url_for("Allfeatures"))
        else:
            msg = "the feature not edited successfully"
            return msg
    else:
        return msg

@app.route('/Deletefeature', methods = ['POST', 'GET'])
def Deletefeature():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method == "POST" and 'feature_id' in request.form :
            feature_id = request.form['feature_id']
            cur = conn.cursor(dictionary=True)
            cur.execute('Delete  FROM features where feature_id=%s', (feature_id,))
            msg="the feature deleted successfully"
            return redirect(url_for('Allfeatures', msg=msg))
        else:
            msg="the plan not deleted successfully"
            return redirect(url_for('Allfeatures', msg=msg))
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cur.fetchone()
        if account:
            expiration_time = timedelta(hours=1)
            now = datetime.utcnow()
            expiration_timestamp = now + expiration_time
            expiration_str = expiration_timestamp.isoformat()
            token_data = {'email': email, 'exp': expiration_str}
            token = serializer.dumps(token_data)
            reset_link = f"http://127.0.0.1:5000/reset-password/{token}"
            msg = Message("Password Reset", sender='yusefamassi@gmail.com', recipients=[email])
            msg.body = f"Click the following link to reset your password: {reset_link}"
            message = "Password reset email sent"
            mail.send(msg)
            return render_template('forgot_password.html',msg=message)
            # Validate email and generate token
            # Store token and email in the database
            # Send password reset email
        else:
            msg="this account not registered"
            return render_template('forgot_password.html',msg=msg)
    return render_template('forgot_password.html')
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if 'loggedin' not in session:
        if request.method=="GET":
            try:
                token_data = serializer.loads(token)
                email = token_data['email']
                expiration_str = token_data['exp']
                expiration_timestamp = datetime.fromisoformat(expiration_str)
                if expiration_timestamp < datetime.utcnow():
                    raise SignatureExpired('Token has expired')
                return render_template('resetNewPassword.html',token=token)
            except SignatureExpired:
                return "Token has expired"
        if request.method=="POST" and "password" in request.form:
            try:
                token_data = serializer.loads(token)
                email = token_data['email']
                expiration_str = token_data['exp']
                expiration_timestamp = datetime.fromisoformat(expiration_str)
                if expiration_timestamp < datetime.utcnow():
                    raise SignatureExpired('Token has expired')
                cur = conn.cursor()
                password=generate_password_hash(request.form['password'])

                cur.execute("UPDATE users SET password = %s WHERE email = %s",
                            (password, email,))
                return redirect(url_for("login"))

            except SignatureExpired:
                return "Token has expired"
    else:
        return "You need to logout to reach for this page "


@app.route('/stores', methods = ['POST', 'GET'])
def stores():
    msg = "you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session and 'type' in session and session['type'] == "ADM":
        if request.method=="GET":
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM stores')
            stores = cur.fetchall()
            return  render_template('dashAdmin/Stores.html',stores=stores)
            
        elif request.method=="POST":
            return "This page need get method"
        else:
            msg="you need to login"
            return msg
    else:
        return msg



@app.route('/Dashboard', methods = ['POST', 'GET'])
def Dashboard():
    msg="you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session:
        if request.method == "GET":
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM stores')
            stores = cur.fetchall()
            return render_template('DashboardUser/Dashboard.html',stores=stores)
        elif request.method=="POST" and request.form['search'] and request.form['page'] and request.form['store']:
            name=request.form['store']
            if name == "ebay":
                 products=[]
                 URL = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=' + request.form['search'] + '&_sacat=2&_pgn='
                 for p in range(int(request.form['page'])):
                        page = requests.get(URL + str(p))
                        soup = BeautifulSoup(page.content, 'html.parser')
                        arr = soup.find_all('li', {'class': "s-item s-item__pl-on-bottom"})
                        for i in arr:
                            title_element = i.find('div', {'class': "s-item__title"})
                            price_element = i.find('span', {'class': "s-item__price"})
                            rate_element = i.find('div', {'class': "x-star-rating"})
                            img_element = i.find('img')

                            title = title_element.text[:20] if title_element else None
                            price = price_element.text if price_element else None
                            rate = rate_element.text[:3] if rate_element else None
                            img = img_element.get("src") if img_element else None

                            product={
                                'title': title,
                                'price': price,
                                'rate': rate,
                                'img': img
                                }
                            products.append(product)
                 return render_template("DashboardUser/home.html", products=products)
            elif name=="namshi":
                products=[]
                URL = 'https://en-ae.namshi.com/' + 'page-' + '/?q=' + request.form['search']
                for p in range(int(request.form['page'])):
                    page = requests.get(URL + str(p))
                    soup = BeautifulSoup(page.content, 'html.parser')
                    arr = soup.find_all('li', {'class': "listing closed"})
                    for i in arr:
                        title_element = i.find('p', {'class': "description"})
                        price_element1=i.find('span', {'class': "specialPrice"})
                        price_element = i.find('span', {'class': "original_price"})
                        rate_element = i.find('p', {'class': "product-ratings__avg"})
                        img_element = i.find('img').get("data-src")
                        title = title_element.text[:20] if title_element else None
                        if price_element:
                            price = price_element.text
                        elif price_element1:
                            price = price_element1.text
                        else:
                            price=None
                        rate = rate_element.text[:3] if rate_element else None
                        
                        product ={
                                        'title': title,
                                        'price': price,
                                        'rate': rate,
                                        'img': img_element
                                        }
                        products.append(product)
                return render_template("DashboardUser/home.html", products=products)
            elif name=="next":
                  URL = 'https://www.next.co.uk/search?w=' + request.form['search'] + '&p='
                  products=[]
                  for p in range(int(request.form['page'])):
                        page = requests.get(URL + str(p))
                        soup = BeautifulSoup(page.content, 'html.parser')
                        arr = soup.find_all('div', {
                            'class': "MuiGrid-root MuiGrid-item MuiGrid-grid-xs-6 MuiGrid-grid-md-4 MuiGrid-grid-lg-4 MuiGrid-grid-xl-3 plp-i98d96"})
                        
                        for i in arr:
                            title_element = i.find('p', {'class': "MuiTypography-root MuiTypography-body1 produc-m0yv3o"})
                            price_element = i.find('span')
                            rate_element=i.find('span',{'class':'MuiRating-root'})
                            img_element = i.find('img')
                            
                            title = title_element.text[:20] if title_element else None
                            price = price_element.text if price_element else None
                            rate = None
                            if rate_element:
                                aria_label = rate_element.get('aria-label')
                                match = re.search(r'\d+(\.\d+)?', aria_label)
                                rate = float(match.group()) if match else None
                            img = img_element.get("src") if img_element else None

                            product={
                                'title': title,
                                'price': price,
                                'rate': rate,
                                'img': img
                                }
                            products.append(product)
                  return render_template("DashboardUser/home.html", products=products)
            elif name=="abebooks":
                URL = 'https://www.abebooks.com/servlet/SearchResults?kn=' + request.form['search'] + '&sts=t&cm_sp=SearchF-_-topnav-_-Results&ds='
                products=[]
                for p in range(int(request.form['page'])):
                    page = requests.get(URL + str(p))
                    soup = BeautifulSoup(page.content, 'html.parser')
                    arr = soup.find_all('li', {'class': "cf result-item"})
                    for i in arr:
                        title_element = i.find('h2', {'class': "title"})
                        price_element = i.find('p', {'class': "item-price"})
                        img_element = i.find('img')
                        rate_element=i.find('span',{'class':'MuiRating-root'})
                        
                        title = title_element.text[:20] if title_element else None
                        price = price_element.text if price_element else None
                        img = img_element.get("src") if img_element else None
                        rate = rate_element.text if rate_element else None
                        product={
                                'title': title,
                                'price': price,
                                'rate': rate,
                                'img': img
                                }
                        products.append(product)
                return render_template("DashboardUser/home.html", products=products)
            else:
                msg="the Store not added yet"
                return msg
        else:
            return msg
    else:
        return msg
@app.route('/Save_product', methods = ['POST', 'GET'])
def Save_product():
    msg="you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session :
        if request.method == "POST" and 'image' in request.form and 'title' in request.form and 'price' in request.form and 'rate' in request.form:
            image=request.form['image']
            title = request.form['title']
            price = request.form['price']
            rate=request.form['rate']
            user_id=session['id']

            cur = conn.cursor()
            cur.execute('SELECT * FROM products WHERE product_name =%s and user_id=%s', (title, user_id,))
            product = cur.fetchone()
            if product:
                msg = "this product is already exists"
                return redirect(request.referrer)
            else:
                cur = conn.cursor()
                cur.execute("INSERT INTO products(product_image, product_name,product_price, product_rate, user_id) VALUES(%s, %s, %s, %s, %s)",
                            [image, title,  price, rate, user_id])
                conn.commit()
                msg = 'You have saved product successfully !'
                cur.close()
                return redirect(request.referrer)
        else:
            msg="you cant save product using get methoed or not logged in"
            return msg
    else:
        msg="you need to login to access for this page or can not access for this page because you are not the admin"
        return msg
@app.route('/Compare_product', methods = ['POST', 'GET'])
def CompareProduct():
    msg="you need to login to access for this page or can not access for this page because you are not the admin"
    if 'loggedin' in session :
        if request.method == "GET":
             user_id=session['id']
             cur = conn.cursor(dictionary=True)
             cur.execute('SELECT * FROM products WHERE user_id=%s', (user_id,))
             json_data = cur.fetchall()
             products = json.dumps(json_data)

             return render_template('DashboardUser/CompareProduct.html',products=products)
        else:
            msg="this method post not supported"
            return msg

