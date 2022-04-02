from random import randint
from flask import render_template, request, session, Blueprint, redirect, url_for, flash
from Database.database import db
import string
import re
from datetime import datetime
from datetime import timedelta
from bson import ObjectId
import json
import math
app = Blueprint('admin', __name__)

# admin panel home
@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if 'admin' not in session:
        return redirect("/admin/login")
    users = len(list(db.users.find()))
    blocked_users = len(list(db.blocked_users.find()))
    doctors = len(list(db.users.find({"mode":"doctor"})))
    patients = len(list(db.users.find({"mode":"patient"})))
    prescriptions = len(list(db.prescriptions.find()))
    deleted_prescriptions = len(list(db.deleted_prescriptions.find()))
    return render_template("admin/admin.html", **locals())


# admin profiles
@app.route("/admin/profile", methods=['GET', 'POST'])
def profile():
    if 'admin' not in session:
        return redirect("/admin/login")
    msg = dict()
    user = db.admins.find_one({"username": session["admin"]})
    data = user

    if request.method == "POST":
        form_data = request.form
        flag = True
        password = form_data['password']
        if len(password) < 4:
            flag = False
            msg['password'] = 'Password length must be at least 4.'

        c_password = form_data['c_password']
        if password != c_password:
            flag = False
            msg['c_password'] = 'Password did not match.'

        fullname = form_data['fullname']
        for ch in fullname:
            if ch not in string.ascii_letters and ch != ' ':
                flag = False
                msg['fullname'] = 'Full Name can contain characters[a-z][A-z] only.'
        if len(fullname) < 5:
            flag = False
            msg['fullname'] = 'Full Name must be atleast 5 characters.'

        email = form_data['email']
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)

        # if match is None:
        #    flag = False
        #    msg['email'] = "Wrong email format"

        find = db.users.find_one({"email": str(email)})
        if find is not None and find['username'] != session['username']:
            flag = False
            msg['email'] = 'Email associated with another account'

        birthday = form_data['birthday']
        allowed_min_age = 15
        if datetime.now() - timedelta(days=365 * allowed_min_age) < datetime.strptime(birthday, '%Y-%m-%d'):
            flag = False
            msg['birthday'] = 'You must be at least 15 years old'
        if flag:
            user['fullname'] = form_data['fullname']
            user['password'] = form_data['password']
            user['birthday'] = form_data['birthday']
            user['gender'] = form_data['gender']
            user['email'] = form_data['email']
            db.admins.save(user)
    return render_template("admin/profile.html", **locals())


# website stats on admin home
@app.route("/admin/stats", methods=['GET', 'POST'])
def stats():
    if 'admin' not in session:
        return redirect("/admin/login")
    users = len(list(db.users.find()))
    blocked_users = len(list(db.blocked_users.find()))
    doctors = len(list(db.users.find({"mode":"doctor"})))
    patients = len(list(db.users.find({"mode":"patient"})))
    prescriptions = len(list(db.prescriptions.find()))
    deleted_prescriptions = len(list(db.deleted_prescriptions.find()))
    return render_template("admin/stats.html", **locals())


# resets admin authorizations
@app.route("/admin/reset", methods=['GET', 'POST'])
def reset_admin():
    # if 'admin' not in session:
    #     return redirect("/admin/login")
    db.admins.remove()
    admin = dict()
    admin["username"] = "drai"
    admin["password"] = "drai"
    admin["fullname"] = "drai"
    admin["email"] = "draibd@gmail.com"
    admin["birthday"] = "1990-01-01"
    admin["gender"] = "male"

    db.admins.insert_one(admin)
    return ""


# admin login
@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]
        data = db.admins.find_one({"username": user})

        if data is None:
            error = "WRONG"
        if user == data["username"] and password == data["password"] and request.form["captcha"] == request.form["captcha_text"]:
            session["admin"] = user
            return redirect("/admin")
        else:
            error = "WRONG"
    captcha = dict()
    from Utils import utils
    url, txt = utils.captcha()
    captcha[txt] = url
    captcha_text = txt
    return render_template("admin/login.html", **locals())


# forgot password for admin panel
@app.route("/admin/forgot", methods=['GET', 'POST'])
def admin_forgot():
    if request.method == "POST":
        username = request.form["username"]
        user = db.admins.find_one({"username": username})
        if user is None:
            error = "User not found"
        else:
            msg = "Password reset link has been sent to your email."
            import Utils.utils as util
            import random
            link_text = ""
            for i in user['username']:
                link_text += i
                for j in range(5):
                    link_text += random.choice(string.ascii_letters)
            util.send_email(user["email"],
                            "Your DoctorAI Password reset link is: " + util.SERVER + "admin/reset_pass/" + link_text + "/")

    return render_template("admin/forgot.html", **locals())


# reset password for admin panel
@app.route("/admin/reset_pass/<string:id>/", methods=['GET', 'POST'])
def admin_reset_pass(id):
    msg = dict()
    username = ""
    for i in range(len(id)):
        if i%6 == 0:
            username += id[i]
    if request.method == "POST":
        password = request.form["password"]
        if len(password) < 6:
            msg["password"] = 'Password length must be at least 6.'
            return render_template('admin/reset.html', **locals())
        user = db.admins.find_one({'username': username})
        user["password"] = password
        db.admins.save(user)
        return redirect("/admin/login")
    return render_template("admin/reset.html", **locals())


# admin logout
@app.route("/admin/logout", methods=['GET', 'POST'])
def admin_logout():
    session.pop("admin")
    return redirect("/admin")


# list of unapproved registrations
@app.route("/admin/unapproved_registrations", methods=['GET', 'POST'])
def unapproved_registrations():
    if 'admin' not in session:
        return redirect("/admin/login")
    users = list(db.unapproved_users.find())
    if request.method =='POST':
        text = request.form["search"]
        temp = []
        for user in users:
            for k in user:
                if request.form["search"] in str(user[k]):
                    temp.append(user)
                    break
        users = temp
    for user in users:
        user['_id'] = str(user['_id'])
    return render_template("admin/unapproved_registrations.html", **locals())


# list of active users
@app.route("/admin/users", methods=['GET', 'POST'])
def users():
    if 'admin' not in session:
        return redirect("/admin/login")
    users = list(db.users.find())
    text = ""
    if request.method =='POST':
        text = request.form["search"]
        temp = []
        for user in users:
            for k in user:
                if request.form["search"] in str(user[k]):
                    temp.append(user)
                    break
        users = temp
    for user in users:
        user['_id'] = str(user['_id'])
    return render_template("admin/users.html", **locals())


# list of blocked users
@app.route("/admin/blocked_users", methods=['GET', 'POST'])
def blocked_users():
    if 'admin' not in session:
        return redirect("/admin/login")
    users = list(db.blocked_users.find())
    text = ""
    if request.method == 'POST':
        text = request.form["search"]
        temp = []
        for user in users:
            for k in user:
                if request.form["search"] in str(user[k]):
                    temp.append(user)
                    break
        users = temp
    for user in users:
        user['_id'] = str(user['_id'])
    return render_template("admin/blocked_users.html", **locals())


# change admin informations
@app.route("/admin/change_info/<string:id>", methods=['GET', 'POST'])
def change_info(id):
    if 'admin' not in session:
        return redirect("/admin/login")
    data = db.users.find_one({"_id": ObjectId(id)})
    if request.method == 'POST':
        new = dict(request.form)
        for k in new:
            data[k] = new[k]
        # db.users.delete_one({"_id": ObjectId(id)})
        # db.users.insert_one(data)
        db.users.save(data)
    return render_template("admin/change_info.html", **locals())


# terms edit page
@app.route("/admin/terms", methods=['GET', 'POST'])
def terms():
    if 'admin' not in session:
        return redirect("/admin/login")
    if request.method == 'POST':
        open("Path/etc/terms.txt","w").write(request.form['comment'])
    txt = open("Path/etc/terms.txt").read()
    return render_template("admin/terms.html", **locals())


# about us edit page
@app.route("/admin/about_us", methods=['GET', 'POST'])
def about_us():
    if 'admin' not in session:
        return redirect("/admin/login")
    if request.method == 'POST':
        open("Path/etc/about_us.txt", "w").write(request.form['comment'])
    txt = open("Path/etc/about_us.txt").read()
    return render_template("admin/about_us.html", **locals())


# faq edit page
@app.route("/admin/faq", methods=['GET', 'POST'])
def faq():
    if 'admin' not in session:
        return redirect("/admin/login")
    if request.method == 'POST':
        open("Path/etc/faq.txt", "w").write(request.form['comment'])
    txt = open("Path/etc/faq.txt").read()
    return render_template("admin/faq.html", **locals())


# list of comments
@app.route("/admin/comments", methods=['GET', 'POST'])
def comments():
    if 'admin' not in session:
        return redirect("/admin/login")
    comments = [dict(c) for c in db.comments.find()]
    for c in comments:
        c["_id"] = str(c["_id"])
    if request.method == 'POST':
        text = request.form["search"]
        temp = []
        for c in comments:
            for k in c:
                if text in c[k]:
                    temp.append(c)
                    break
        comments = temp
    pages = math.ceil(len(comments)/10)
    for i in range(len(comments)):
        comments[i]["bucket"] = int(i/10)
    return render_template("admin/comments.html", **locals())


# list of activity log
@app.route("/admin/activity", methods=['GET', 'POST'])
def activity():
    if 'admin' not in session:
        return redirect("/admin/login")
    acts = list(reversed(list(db.activities.find())))
    pages = math.ceil(len(acts)/10)
    for i in range(len(acts)):
        acts[i]["bucket"] = int(i/10)
    return render_template("admin/activity.html", **locals())


# export activity log
@app.route("/admin/activity/export", methods=['GET', 'POST'])
def activity_export():
    f = open("activity.csv", "w")
    acts = list(reversed(list(db.activities.find())))
    for act in acts:
        f.write(str(act["time"]).replace(" ", "-")+","+act["act"]+"\n")
    f.close()
    from flask import send_file
    return send_file("activity.csv",cache_timeout= 0, as_attachment=True)


# delete activity log
@app.route("/admin/activity/delete", methods=['GET', 'POST'])
def activity_delete():
    db.activities.remove()
    return redirect("/admin/stats")


# edit privacy policy
@app.route("/admin/pp", methods=['GET', 'POST'])
def pp():
    if 'admin' not in session:
        return redirect("/admin/login")
    if request.method == 'POST':
        open("Path/etc/pp.txt","w").write(request.form['comment'])
    txt = open("Path/etc/pp.txt").read()
    return render_template("admin/pp.html", **locals())


# shows history of a user
@app.route("/admin/history/<string:id>", methods=['GET', 'POST'])
def history(id):
    if 'admin' not in session:
        return redirect("/admin/login")
    user = db.users.find_one({"_id": ObjectId(id)})
    if user['mode'] == 'doctor':
        prescriptions = list(db.prescriptions.find({'doctor': user['username']}))
    else:
        prescriptions = list(db.prescriptions.find({'mobile': user['mobile']}))
    return render_template("admin/history.html", **locals())


# resets the password of a user
@app.route("/admin/reset/<string:id>", methods=['GET', 'POST'])
def reset(id):
    if 'admin' not in session:
        return redirect("/admin/login")
    user = db.users.find_one({"_id": ObjectId(id)})
    user["password"] = "123456"
    db.users.save(user)
    import Utils.utils as util
    import random
    link_text = ""
    for i in user['username']:
        link_text += i
        for j in range(5):
            link_text += random.choice(string.ascii_letters)
    util.send_email(user["email"],
                    "Your DoctorAI Password reset link is: " + util.SERVER + "auth/reset/" + link_text + "/")
    return render_template("admin/reset.html", **locals())


# list of all prescriptions
@app.route("/admin/prescriptions", methods=['GET', 'POST'])
def prescriptions():
    if 'admin' not in session:
        return redirect("/admin/login")
    prescriptions = list(db.prescriptions.find())
    if request.method == "POST":
        search_text = request.form["search"]
        new = []
        for p in prescriptions:
            for k in p:
                if search_text in str(p[k]):
                    new.append(p)
                    break
        prescriptions = new
    for presobj in prescriptions:
        doc_id = str(db.users.find_one({"username": presobj["doctor"]})["_id"])
        pt_id = db.users.find_one({"mobile": presobj["mobile"]})
        if pt_id is not None:
            pt_uname = str(pt_id["username"])
            presobj["pt_uname"] = pt_uname
            pt_id = str(pt_id["_id"])
        presobj["doc_id"] = doc_id
        presobj["pt_id"] = pt_id
    pres = []
    p = []
    temp = prescriptions
    while len(temp) > 0:
        p.append(temp[0])
        temp = temp[1:]
        if len(p) == 10:
            pres.append(p)
            p = []
    if len(p) != 0:
        pres.append(p)
    return render_template("admin/prescriptions.html", **locals())


# list of all deleted prescriptions
@app.route("/admin/deleted_prescriptions", methods=['GET', 'POST'])
def deleted_prescriptions():
    if 'admin' not in session:
        return redirect("/admin/login")
    prescriptions = list(db.deleted_prescriptions.find())
    if request.method == "POST":
        search_text = request.form["search"]
        new = []
        for p in prescriptions:
            for k in p:
                if search_text in str(p[k]):
                    new.append(p)
                    break
        prescriptions = new
    pres = []
    p = []
    temp = prescriptions
    while len(temp) > 0:
        p.append(temp[0])
        temp = temp[1:]
        if len(p) == 10:
            pres.append(p)
            p = []
    if len(p) != 0:
        pres.append(p)
    return render_template("admin/deleted_prescriptions.html", **locals())


# view a deleted prescription
@app.route('/admin/deleted_prescription/<string:prescriptionID>/', methods=['GET', 'POST'])
def deleted_prescription(prescriptionID):
    if 'admin' not in session:
        return redirect("/admin/login")
    presobj = None
    for x in db.deleted_prescriptions.find({'prescriptionid': int(prescriptionID)}):
        presobj = x
    dx_list = []
    cc_list = []
    rx_list = []
    ix_list = []
    rx_list = []

    for key in presobj:
        if key[:2] == 'dx':
            dx_list.append(presobj[key])
        if key[:2] == 'ix':
            ix_list.append(presobj[key])
        if key[:2] == 'cc':
            cc_list.append(presobj[key])
        if key[:2] == 'rx' and key[:3] != 'rxm':
            rx = dict()
            id = key.replace("rx", "")
            rx["rx"] = presobj[key]
            rx["dose"] = presobj["dose"+id]
            rx["duration"] = presobj["duration"+id]
            if "before"+id in presobj:
                rx["before"] = presobj["before"+id]
            else:
                rx["before"] = ""
            if "after"+id in presobj:
                rx["after"] = presobj["after"+id]
            else:
                rx["after"] = ""
            if presobj["dm" + id] == "Days":
                rx["days"] = "checked"
            else:
                rx["days"] = ""
            if presobj["dm" + id] == "Months":
                rx["months"] = "checked"
            else:
                rx["months"] = ""
            rx["mode"] = presobj["rxmode" + id]
            rx_list.append(rx)

    presobj['ix'] = ix_list
    presobj['dx'] = dx_list
    presobj['cc'] = cc_list
    presobj['rx'] = rx_list
    return render_template('admin/deleted_prescription.html', **locals())


# view a active prescription
@app.route('/admin/prescription/<string:prescriptionID>/', methods=['GET', 'POST'])
def prescription(prescriptionID):
    if 'admin' not in session:
        return redirect("/admin/login")
    presobj = None
    for x in db.prescriptions.find({'prescriptionid': int(prescriptionID)}):
        presobj = x
    dx_list = []
    cc_list = []
    rx_list = []
    ix_list = []
    rx_list = []

    for key in presobj:
        if key[:2] == 'dx':
            dx_list.append(presobj[key])
        if key[:2] == 'ix':
            ix_list.append(presobj[key])
        if key[:2] == 'cc':
            cc_list.append(presobj[key])
        if key[:2] == 'rx' and key[:3] != 'rxm':
            rx = dict()
            id = key.replace("rx", "")
            rx["rx"] = presobj[key]
            rx["dose"] = presobj["dose"+id]
            rx["duration"] = presobj["duration"+id]
            if "before"+id in presobj:
                rx["before"] = presobj["before"+id]
            else:
                rx["before"] = ""
            if "after"+id in presobj:
                rx["after"] = presobj["after"+id]
            else:
                rx["after"] = ""
            if presobj["dm" + id] == "Days":
                rx["days"] = "checked"
            else:
                rx["days"] = ""
            if presobj["dm" + id] == "Months":
                rx["months"] = "checked"
            else:
                rx["months"] = ""
            rx["mode"] = presobj["rxmode" + id]
            rx_list.append(rx)

    presobj['ix'] = ix_list
    presobj['dx'] = dx_list
    presobj['cc'] = cc_list
    presobj['rx'] = rx_list
    return render_template('admin/prescription.html', **locals())


# approves a user
@app.route("/admin/approve", methods=['GET', 'POST'])
def approve():
    if request.method == 'POST':
        req = request.json
        id = req["id"]
        data = db.unapproved_users.find_one({"_id": ObjectId(id)})
        data.pop("_id")
        db.unapproved_users.delete_one({"_id": ObjectId(id)})
        db.unverified_users.insert_one(data)
        import Utils.utils as util
        util.send_email(data['email'], "Your DoctorAI confirmation code is: "+data["key"]+ "<br> Verify at "+util.SERVER+"auth/verify")
        import Utils.utils as utils
        utils.register_activity("User " + id + " has been approved")
    return "ok"


# blocks a user
@app.route("/admin/block", methods=['GET', 'POST'])
def block():
    if request.method == 'POST':
        req = request.json
        id = req["id"]
        data = db.users.find_one({"_id": ObjectId(id)})
        data.pop("_id")
        db.users.delete_one({"_id": ObjectId(id)})
        db.blocked_users.insert_one(data)
        import Utils.utils as utils
        utils.register_activity("User " + id + " has been blocked")
    return "ok"


# unblocks a user
@app.route("/admin/unblock", methods=['GET', 'POST'])
def unblock():
    if request.method == 'POST':
        req = request.json
        id = req["id"]
        data = db.blocked_users.find_one({"_id": ObjectId(id)})
        data.pop("_id")
        db.blocked_users.delete_one({"_id": ObjectId(id)})
        db.users.insert_one(data)

        import Utils.utils as utils
        utils.register_activity("User " + id + " has been unblocked")
    return "ok"


# deletes a prescription
@app.route("/admin/delete_pres", methods=['GET', 'POST'])
def delete_pres():
    if request.method == 'POST':
        req = request.json
        id = req["id"]
        data = db.prescriptions.find_one({"prescriptionid": int(id)})
        data.pop("_id")
        db.prescriptions.delete_one({"prescriptionid": int(id)})
        db.deleted_prescriptions.insert_one(data)
        import Utils.utils as utils
        utils.register_activity("Prescription " + id + " has been deleted")
    return "ok"


# restores a prescription
@app.route("/admin/restore_pres", methods=['GET', 'POST'])
def restore_pres():
    if request.method == 'POST':
        req = request.json
        id = req["id"]
        data = db.deleted_prescriptions.find_one({"prescriptionid": int(id)})
        data.pop("_id")
        db.deleted_prescriptions.delete_one({"prescriptionid": int(id)})
        db.prescriptions.insert_one(data)
        import Utils.utils as utils
        utils.register_activity("Prescription " + id + " has been restored")
    return "ok"


# deletes a comment
@app.route("/admin/delete_comment", methods=['GET', 'POST'])
def delete_comment():
    if request.method == 'POST':
        req = request.json
        id = req["id"]
        db.comments.delete_one({"_id": ObjectId(id)})
        import Utils.utils as utils
        utils.register_activity("Comment " + id + " has been deleted")
    return "ok"


# Add (RX, DX, CC, IX)
@app.route("/admin/entry1", methods=['GET', 'POST'])
def entry1():
    if request.method == 'POST':
        d = dict()
        for k in request.form:
            d[k] = request.form[k]
        from Utils import utils
        utils.entry1(d)
    return render_template('admin/entry1.html', **locals())


# Add Weights
@app.route("/admin/entry2", methods=['GET', 'POST'])
def entry2():
    if request.method == 'POST':
        d = dict()
        for k in request.form:
            d[k] = request.form[k]
        from Utils import utils
        utils.entry2(d)
    return render_template('admin/entry2.html', **locals())


# config settings
@app.route("/admin/config", methods=['GET', 'POST'])
def config():
    from Utils import utils
    SERVER, SERVER_EMAIL, SUGGESTION_LIMIT, MAX_FILE_SIZE = utils.load_config()
    if request.method == 'POST':
        d = dict()
        for k in request.form:
            d[k] = request.form[k]
        SERVER = d["server"]
        SERVER_EMAIL = d["server_email"]
        SUGGESTION_LIMIT = d["suggestion"]
        MAX_FILE_SIZE = d["max_file"]
        utils.write_config(SERVER, SERVER_EMAIL, SUGGESTION_LIMIT, MAX_FILE_SIZE)
    return render_template('admin/config.html', **locals())


# serves the lists for Add Weights module
@app.route("/admin/entry2list", methods=['GET', 'POST'])
def entry2list():
    if request.method == 'POST':
        from Utils import utils
        res = utils.entry2list(dict())
        return json.dumps(res[request.json["mode"].upper()])
    return json.dumps(["a","b","c"])