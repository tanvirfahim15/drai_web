from random import randint
from flask import render_template, request, session, Blueprint, redirect, url_for, flash
from Database.database import db
import string
import re
from datetime import datetime
from datetime import timedelta
from bson import ObjectId
import json

app = Blueprint('auth', __name__)


# validates the registration form data
def register_validation(data):
    flag = True
    msg = dict()

    if  data["captcha"] != data["captcha_text"]:
        flag = False
        msg['captcha'] = 'Captcha did not match.'

    username = data['username']
    if len(username) < 6:
        flag = False
        msg['username'] = 'Username must be atleast 6 characters.'

    find = db.users.find_one({"username": str(username)})
    if find is not None:
        flag = False
        msg['username'] = 'Username Exists'

    for ch in username:
        if ch not in string.ascii_letters and ch not in string.digits:
            flag = False
            msg['username'] = 'Username can contain [a-z][A-z][0-9] only.'

    password = data['password']
    if len(password) < 6:
        flag = False
        msg['password'] = 'Password length must be at least 6.'

    c_password = data['c_password']
    if password != c_password:
        flag = False
        msg['c_password'] = 'Password did not match.'

    fullname = data['fullname']
    for ch in fullname:
        if ch not in string.ascii_letters and ch != ' ':
            flag = False
            msg['fullname'] = 'Full Name can contain characters[a-z][A-z] only.'
    if len(fullname) < 5:
        flag = False
        msg['fullname'] = 'Full Name must be atleast 5 characters.'

    email = data['email']
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)

    if match is None:
        flag = False
        msg['email'] = "Wrong email format"

    find = db.users.find_one({"email": str(email)})
    if find is not None:
        flag = False
        msg['email'] = 'Email associated with another account'

    birthday = data['birthday']
    allowed_min_age = 20
    if datetime.now() - timedelta(days=365 * allowed_min_age) < datetime.strptime(birthday, '%Y-%m-%d'):
        flag = False
        msg['birthday'] = 'You must be at least 15 years old'

    if data['gender'] == '0':
        flag = False
        msg['gender'] = 'Choose your gender'

    mobile = data['mobile']
    try:
        p = int(mobile)
    except ValueError:
        flag = False
        msg['mobile'] = 'Mobile number must contain exactly 11 digits'
        phn_no = None

    if len(mobile) != 11:
        flag = False
        msg['mobile'] = 'Mobile number must contain exactly 11 digits'
    find = db.users.find_one({"mobile": str(mobile)})
    if find is not None:
        flag = False
        msg['mobile'] = 'Mobile number associated with another account'

    if 'terms' not in data.keys():
        flag = False
        msg['terms'] = 'You must agree to terms'


    if 'doctor' in data.keys():
        data.pop("doctor")
    if 'patient' in data.keys():
        data.pop("patient")
    return flag, msg, data


# generates random key for OTP
def random_key():
    import random
    ret = ""
    for x in range(6):
        ret += str(random.randint(0, 9))
    return ret


# handles user registrations
@app.route('/auth/register/', methods=['GET', 'POST'])
def auth_register():
    if is_logged_in():
        return redirect('/')
    msg = dict()
    data = dict()

    if request.method == 'POST':
        mode = None
        if 'doctor' in request.form.to_dict():
            mode = 'doctor'
        if 'patient' in request.form.to_dict():
            mode = 'patient'
        flag, msg, data = register_validation(request.form.to_dict())
        data["mode"] = mode
        if flag:
            data.pop('c_password')
            if 'terms' in data.keys():
                data.pop('terms')
            data["key"] = random_key()
            data["balance"] = 0
            #import Utils.utils as util
            #util.send_email(data['email'], "Your DoctorAI confirmation code is: "+data["key"])
            data["time"] = str(datetime.now())
            id = db.unapproved_users.insert_one(data).inserted_id

            from Utils import utils
            utils.send_email(utils.SERVER_EMAIL, "New registration on Doctor AI as " + mode + ": " + data["username"] + "<br/>Email:" + data["email"])
            return redirect(url_for('auth.auth_wait'))

    title = 'Register'
    captcha = dict()
    from Utils import utils
    url, txt = utils.captcha()
    captcha[txt] = url
    captcha_text = txt
    return render_template("auth/register.html", **locals())


# handles user registrations from mobile
@app.route('/auth/register/mobile/', methods=['GET', 'POST'])
def auth_register_mobile():
    if is_logged_in():
        return redirect('/')
    msg = dict()
    data = dict()

    if request.method == 'POST':
        mode = None
        if 'doctor' in request.form.to_dict():
            mode = 'doctor'
        if 'patient' in request.form.to_dict():
            mode = 'patient'
        flag, msg, data = register_validation(request.form.to_dict())
        if flag:
            data.pop('c_password')
            data.pop('phn_operator')
            data.pop('phn_no')
            if 'terms' in data.keys():
                data.pop('terms')
            data["key"] = random_key()
            data["balance"] = 0
            data["mode"] = mode
            #import Utils.utils as util
            #util.send_email(data['email'], "Your DoctorAI confirmation code is: "+data["key"])
            data["time"] = str(datetime.now())
            id = db.unapproved_users.insert_one(data).inserted_id

            from Utils import utils
            utils.send_email(utils.SERVER_EMAIL,
                             "New registration on Doctor AI as " + mode + ": " + data["username"] + "<br/>Email:" +
                             data["email"])
            return redirect(url_for('auth.auth_wait'))

    title = 'Register'
    captcha = dict()
    captcha["dfver"] = "https://i.imgbun.com/DfLCw.png"
    captcha["df234"] = "https://i.imgbun.com/eEGMgamIjaKQx.png"
    captcha["2fdg234"] = "https://i.imgbun.com/8d14oKgHeORhKNo.png"
    captcha["er$drf"] = "https://i.imgbun.com/Rj7ZL.png"
    captcha["dw#$34f"] = "https://i.imgbun.com/XC39vlPnFw3XP.png"
    import random
    captcha_text = random.choice(list(captcha.keys()))
    return render_template("mobile/auth/register.html", **locals())


# shows post registration waiting message
@app.route('/auth/wait/', methods=['GET', 'POST'])
def auth_wait():
    title = 'Verify Account'
    return render_template('auth/wait.html', **locals())


# verifies approved users
@app.route('/auth/verify/', methods=['GET', 'POST'])
def auth_verify():
    msg = ''
    if request.method == 'POST':
        code = request.form.to_dict()['code']
        data = db.unverified_users.find_one({"mobile": request.form.to_dict()['phone']})
        if data is None:
            msg = "Phone number did not match"
        elif data["key"] != code:
            msg = "Code unmatched"
        else:
            flag = True
            find = db.users.find_one({"username": data["username"]})
            if find is not None:
                flag = False
                msg = 'Username Exists'
            find = db.users.find_one({"email": data["email"]})
            if find is not None:
                flag = False
                msg = 'Email associated with another account'
            if flag:
                data.pop('key')
                db.unverified_users.delete_one({"mobile": request.form.to_dict()['phone']})
                db.users.insert_one(data)
                return redirect('/auth/login/')
    title = 'Verify Account'
    return render_template('auth/verify.html', **locals())


# verifies approved users mobile
@app.route('/auth/verify/mobile/', methods=['GET', 'POST'])
def auth_verify_mobile():
    msg = ''
    if request.method == 'POST':
        code = request.form.to_dict()['code']
        data = db.unverified_users.find_one({"mobile": request.form.to_dict()['phone']})
        if data is None:
            msg = "Phone number did not match"
        elif data["key"] != code:
            msg = "Code unmatched"
        else:
            flag = True
            find = db.users.find_one({"username": data["username"]})
            if find is not None:
                flag = False
                msg = 'Username Exists'
            find = db.users.find_one({"email": data["email"]})
            if find is not None:
                flag = False
                msg = 'Email associated with another account'
            if flag:
                data.pop('key')
                db.unverified_users.delete_one({"mobile": request.form.to_dict()['phone']})
                db.users.insert_one(data)
                return redirect('/auth/login/')
    title = 'Verify Account'
    return render_template('mobile/auth/verify.html', **locals())


# returns if a user is logged in or not
def is_logged_in():
    if 'logged_in' not in session.keys():
        return False
    if not session['logged_in']:
        return False
    user = db.users.find_one({"username": str(session['username'])})
    id = session['userid']
    if str(user['_id']) != id:
        return False
    return True

# handles user logins
@app.route('/auth/login/', methods=['GET', 'POST'])
def auth_login():
    msg = dict()
    if is_logged_in():
        return redirect('/')
    if request.method == 'POST':
        data = request.form
        username= data['username']
        user = db.users.find_one({"username": str(username)})
        if user is not None:
            password = str(user["password"])
            if data['password'] == password and data["captcha"] == data["captcha_text"]:
                session['logged_in'] = True
                session['username'] = username
                import Utils.utils as utils
                utils.register_activity(username + " has been logged in")
                session['userid'] = str(user["_id"])
                return redirect('/')
        else:
            error = 'Invalid Username'
        if data['password'] != password:
            error = 'Wrong Password'
        if data["captcha"] != data["captcha_text"]:
            msg['captcha'] = 'Captcha did not match.'
    captcha = dict()
    from Utils import utils
    url, txt = utils.captcha()
    captcha[txt] = url
    captcha_text = txt
    return render_template('auth/login.html', **locals())


# handles user logins mobile
@app.route('/auth/login/mobile/', methods=['GET', 'POST'])
def auth_login_mobile():
    if is_logged_in():
        return redirect('/')
    if request.method == 'POST':
        data = request.form
        username= data['username']
        user = db.users.find_one({"username": str(username)})
        if user is not None:
            password = str(user["password"])
            if data['password'] == password:
                session['logged_in'] = True
                session['username'] = username
                session['order'] = []
                session['userid'] = str(user["_id"])
                import Utils.utils as utils
                utils.register_activity(username + " has been logged in")
                return redirect('/')
            else:
                error = 'Wrong Password'
        else:
            error = 'Invalid Username'
    return render_template('mobile/auth/login.html', **locals())


# logout for user
@app.route('/auth/logout/')
def logout():
    session.clear()
    return redirect(url_for('home'))


# handles forget password for users
@app.route('/auth/forgot/', methods=['GET', 'POST'])
def auth_forgot():
    msg = dict()
    if request.method == 'POST':
        input = request.form['username']
        user = db.users.find_one({'username': input})
        if user is None:
            user = db.users.find_one({'email': input})
        if user is None:
            msg['username'] = "Username or Email Not Found."
        else:
            msg['done'] = "true"
            import Utils.utils as util
            import random
            link_text = ""
            for i in user['username']:
                link_text += i
                for j in range(5):
                    link_text += random.choice(string.ascii_letters)
            util.send_email(user["email"], "Your DoctorAI Password reset link is: "+util.SERVER+"auth/reset/"+link_text + "/")
    return render_template('auth/forgot.html', **locals())


# handles forget password for users mobile
@app.route('/auth/forgot/mobile/', methods=['GET', 'POST'])
def auth_forgot_mobile():
    msg = dict()
    if request.method == 'POST':
        input = request.form['username']
        user = db.users.find_one({'username': input})
        if user is None:
            user = db.users.find_one({'email': input})
        if user is None:
            msg['username'] = "Username or Email Not Found."
        else:
            msg['done'] = "true"
            import Utils.utils as util
            import random
            link_text = ""
            for i in user['username']:
                link_text += i
                for j in range(5):
                    link_text += random.choice(string.ascii_letters)
            util.send_email(user["email"], "Your DoctorAI Password reset link is: " + util.SERVER + "auth/reset/" + link_text +"/")
    return render_template('mobile/auth/forgot.html', **locals())


# reset link for forgotten user password
@app.route('/auth/reset/<string:id>/', methods=['GET', 'POST'])
def auth_reset(id):
    msg = dict()
    username = ""
    for i in range(len(id)):
        if i%6 == 0:
            username += id[i]
    if request.method == 'POST':
        password = request.form["password"]
        if len(password) < 6:
            msg["password"] = 'Password length must be at least 6.'
            return render_template('auth/reset.html', **locals())
        user = db.users.find_one({'username': username})
        user["password"] = password
        db.users.save(user)
        return redirect(url_for('auth.auth_login'))
    return render_template('auth/reset.html', **locals())


# reset link for forgotten user password mobile
@app.route('/auth/reset/<string:id>/mobile', methods=['GET', 'POST'])
def auth_reset_mobile(id):
    msg = dict()
    username = ""
    for i in range(len(id)):
        if i%6 == 0:
            username += id[i]
    if request.method == 'POST':
        password = request.form["password"]
        if len(password) < 6:
            msg["password"] = 'Password length must be at least 6.'
            return render_template('mobile/auth/reset.html', **locals())
        user = db.users.find_one({'username': username})
        user["password"] = password
        db.users.save(user)
        return redirect(url_for('auth.auth_login'))
    return render_template('mobile/auth/reset.html', **locals())