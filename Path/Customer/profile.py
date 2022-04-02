from flask import render_template, request, session, Blueprint, redirect, url_for
from Database.database import db
import string
import re
from datetime import datetime
from datetime import timedelta
from bson import ObjectId
import Path.Auth.auth as auth

app = Blueprint('customer_profile', __name__)


@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if not auth.is_logged_in():
        return redirect(url_for('auth.auth_login'))
    customer_information = db.users.find_one({"username": str(session['username'])})
    return render_template("customer/profile.html", **locals())


@app.route('/profile/mobile/', methods=['GET', 'POST'])
def profile_mobile():
    if not auth.is_logged_in():
        return redirect(url_for('auth.auth_login'))
    customer_information = db.users.find_one({"username": str(session['username'])})
    return render_template("mobile/customer/profile.html", **locals())


@app.route('/personalized_info/<string:mobile>/', methods=['GET', 'POST'])
def personalized_info(mobile):
    if not auth.is_logged_in():
        return redirect(url_for('auth.auth_login'))
    user = db.users.find_one({"username": str(session['username'])})
    if request.method == 'POST':
        p_info = request.form.to_dict()
        p_info["mobile"] = mobile
        if user["mode"] == "doctor":
            p_info['status'] = "Verified"
        else:
            p_info['status'] = "Not verified"
        dbp_info = db.personalized_info.find_one({"mobile": mobile})
        if dbp_info is None:
            db.personalized_info.insert_one(p_info)
        else:
            p_info["_id"] = dbp_info["_id"]
            import Utils.utils as utils
            utils.register_activity(session['username'] + " has updated personalized information.")
            db.personalized_info.save(p_info)
            utils.send_pinfo(p_info)
    p_info = db.personalized_info.find_one({"mobile": mobile})
    if p_info is None:
        p_info = dict()
        p_info['visits'] = ""
        p_info['allergic_reactions'] = ""
        p_info['disability'] = ""
        p_info['previous_diseases'] = ""
        p_info['inheritance'] = ""
        p_info['status'] = "Not verified"

    return render_template("customer/personalized_info.html", **locals())


@app.route('/personalized_info/<string:mobile>/mobile/', methods=['GET', 'POST'])
def personalized_info_mobile(mobile):
    if not auth.is_logged_in():
        return redirect(url_for('auth.auth_login'))
    user = db.users.find_one({"username": str(session['username'])})
    if request.method == 'POST':
        p_info = request.form.to_dict()
        p_info["mobile"] = mobile
        if user["mode"] == "doctor":
            p_info['status'] = "Verified"
        else:
            p_info['status'] = "Not verified"
        dbp_info = db.personalized_info.find_one({"mobile": mobile})
        if dbp_info is None:
            db.personalized_info.insert_one(p_info)
        else:
            p_info["_id"] = dbp_info["_id"]
            import Utils.utils as utils
            utils.register_activity(session['username'] + " has updated personalized information.")
            db.personalized_info.save(p_info)
            utils.send_pinfo(p_info)
    p_info = db.personalized_info.find_one({"mobile": mobile})
    if p_info is None:
        p_info = dict()
        p_info['visits'] = ""
        p_info['allergic_reactions'] = ""
        p_info['disability'] = ""
        p_info['previous_diseases'] = ""
        p_info['inheritance'] = ""
        p_info['status'] = "Not verified"

    return render_template("mobile/customer/personalized_info.html", **locals())


@app.route('/update_profile/', methods=['GET', 'POST'])
def update_profile():
    if not auth.is_logged_in():
        return redirect(url_for('auth.auth_login'))
    msg = dict()
    data = dict()
    customer_information = db.users.find_one({"username": str(session['username'])})
    if request.method == 'POST':
        data = request.form.to_dict()
        flag = True
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

        #if match is None:
        #    flag = False
        #    msg['email'] = "Wrong email format"

        find = db.users.find_one({"email": str(email)})
        if find is not None and find['username'] != session['username']:
            flag = False
            msg['email'] = 'Email associated with another account'

        birthday = data['birthday']
        allowed_min_age = 15
        if datetime.now() - timedelta(days=365 * allowed_min_age) < datetime.strptime(birthday, '%Y-%m-%d'):
            flag = False
            msg['birthday'] = 'You must be at least 15 years old'

        if flag:
            customer_information['fullname'] = data['fullname']
            customer_information['password'] = data['password']
            customer_information['birthday'] = data['birthday']
            customer_information['gender'] = data['gender']
            customer_information['email'] = data['email']
            customer_information['degrees'] = data['degrees']
            customer_information['caddr'] = data['caddr']
            import Utils.utils as utils
            utils.register_activity(session['username'] + " has updated profile.")
            db.users.save(customer_information)
            return redirect('/profile/')
    title = 'Profile Information Update'
    return render_template("customer/update_profile.html", **locals())


@app.route('/update_profile/mobile/', methods=['GET', 'POST'])
def update_profile_mobile():
    if not auth.is_logged_in():
        return redirect(url_for('auth.auth_login'))
    msg = dict()
    data = dict()
    customer_information = db.users.find_one({"username": str(session['username'])})
    if request.method == 'POST':
        data = request.form.to_dict()
        flag = True
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

        #if match is None:
            #flag = False
            #msg['email'] = "Wrong email format"

        find = db.users.find_one({"email": str(email)})
        if find is not None and find['username'] != session['username']:
            flag = False
            msg['email'] = 'Email associated with another account'

        birthday = data['birthday']
        allowed_min_age = 15
        if datetime.now() - timedelta(days=365 * allowed_min_age) < datetime.strptime(birthday, '%Y-%m-%d'):
            flag = False
            msg['birthday'] = 'You must be at least 15 years old'

        if flag:
            customer_information['fullname'] = data['fullname']
            customer_information['password'] = data['password']
            customer_information['birthday'] = data['birthday']
            customer_information['gender'] = data['gender']
            customer_information['email'] = data['email']
            customer_information['degrees'] = data['degrees']
            customer_information['caddr'] = data['caddr']
            import Utils.utils as utils
            utils.register_activity(session['username'] + " has updated profile.")
            db.users.save(customer_information)
            return redirect('/profile/')
    title = 'Profile Information Update'
    return render_template("mobile/customer/update_profile.html", **locals())

