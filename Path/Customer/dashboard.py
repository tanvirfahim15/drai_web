import json
import random

from flask import render_template, request, session, Blueprint, redirect, url_for, flash, send_file
from Database.database import db
import string
import re
from datetime import datetime
from datetime import timedelta
from bson import ObjectId
from Path.Auth import auth

app = Blueprint('customer_dashboard', __name__)


# user dashboard
@app.route('/dashboard/', methods=['GET', 'POST'])
def dashboard():
    search_text = ""
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    user = db.users.find_one({"username": session['username']})
    if user['mode'] == 'doctor':
        prescriptions = list(db.prescriptions.find({'doctor': session['username']}))
    else:
        prescriptions = list(db.prescriptions.find({'mobile': user['mobile']}))
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

    return render_template("customer/dashboard.html", **locals())


# user dashboard for mobile
@app.route('/dashboard/mobile/', methods=['GET', 'POST'])
def dashboard_mobile():
    search_text = ""
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    user = db.users.find_one({"username": session['username']})
    if user['mode'] == 'doctor':
        prescriptions = list(db.prescriptions.find({'doctor': session['username']}))
    else:
        prescriptions = list(db.prescriptions.find({'mobile': user['mobile']}))
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
    return render_template("mobile/customer/dashboard.html", **locals())


# shows list of prescriptions created by/for a user
@app.route('/history/<string:mobile>/', methods=['GET', 'POST'])
def history(mobile):
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    user = db.users.find_one({"mobile": mobile})
    prescriptions = list(db.prescriptions.find({"mobile": mobile}))
    return render_template("customer/history.html", **locals())


# shows list of prescriptions created by/for a user mobile
@app.route('/history/<string:mobile>/mobile/', methods=['GET', 'POST'])
def history_mobile(mobile):
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    user = db.users.find_one({"mobile": mobile})
    prescriptions = list(db.prescriptions.find({"mobile": mobile}))
    return render_template("mobile/customer/history.html", **locals())


# upload feature for prescriptions
@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    user = db.users.find_one({"username": session['username']})
    from Utils import utils
    file_limit = utils.load_config()[3]/100000
    if request.method == 'POST':
        data = dict()
        for k in request.form:
            data[k] = request.form[k]
        import time
        data["time"] = time.time()

        f = request.files['file']
        if f.filename == "":
            error = "Upload a file"
            return render_template("customer/upload.html", **locals())

        size = 0
        from Utils import utils
        if size > utils.MAX_FILE_SIZE:
            error = "Maximum allowed file size is " + str(utils.MAX_FILE_SIZE) + "bytes"
            return render_template("customer/upload.html", **locals())
        data["ext"] = str(f.filename).split(".")[-1]
        id = db.uploads.insert_one(data).inserted_id
        f.save("static/Uploads/"+ str(id)+"." + str(f.filename).split(".")[-1])
        return redirect("/dashboard/")
    return render_template("customer/upload.html", **locals())


# upload feature for prescriptions on mobile
@app.route('/uploads/<string:mobile>', methods=['GET', 'POST'])
def uploads(mobile):
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    prescriptions = list(db.uploads.find({"mobile": mobile}))
    user = db.users.find_one({"username": session['username']})
    import time
    delete_permission = False
    if user["mode"] == "patient":
        delete_permission = True

    if request.method == "POST":
        search_text = request.form["search"]
        new = []
        for p in prescriptions:
            for k in p:
                if search_text in str(p[k]):
                    new.append(p)
                    break
        prescriptions = new
    for p in prescriptions:
        p["date"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(p["time"]+3600*6))

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

    return render_template("customer/uploads.html", **locals())


# deletes an uploaded file
@app.route('/delete_upload/<string:id>', methods=['GET', 'POST'])
def delete_upload(id):
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    db.uploads.remove({"_id": ObjectId(id)})
    return "ok"


# views an uploaded file
@app.route('/view_file/<string:file>', methods=['GET', 'POST'])
def view(file):
    return redirect(url_for('static', filename='Uploads/' + file), code=301)


# downloads an uploaded file
@app.route('/download/<string:file>', methods=['GET', 'POST'])
def download(file):
    from flask import send_file
    return send_file("static/Uploads/"+file, cache_timeout=0, as_attachment=True)


# creates a prescription
@app.route('/prescribe/', methods=['GET', 'POST'])
def prescribe():
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    cur_date = datetime.date(datetime.now())
    if request.method == 'POST':
        form_as_dict = request.form.to_dict()

        record = dict()
        rand_id = random.randint(0, 999999)
        while True:
            if db.prescriptions.find_one({'prescriptionid': rand_id}):
                rand_id = random.randint(0, 999999)
            else:
                break

        record['prescriptionid'] = rand_id

        record['name'] = form_as_dict['name']
        record['age'] = form_as_dict['age']
        if 'male' in form_as_dict:
            record['sex'] = "Male"
        if 'female' in form_as_dict:
            record['sex'] = "Female"
        if 'other' in form_as_dict:
            record['sex'] = "Other"
        record['address'] = form_as_dict['address']
        record['mobile'] = form_as_dict['mobile']
        record['email'] = form_as_dict['email']
        record['date'] = form_as_dict['date']
        # dx = form_as_dict['dx'].replace("\r\n\r\n", "\r\n")
        for key in form_as_dict:
            if key[:2] == 'dx':
                record[key] = form_as_dict[key]
            if key[:2] == 'rx':
                record[key] = form_as_dict[key]
            if key[:2] == 'ix':
                record[key] = form_as_dict[key]
            if key[:2] == 'cc':
                record[key] = form_as_dict[key]
            if key[:4] == 'dose':
                record[key] = form_as_dict[key]
            if key[:8] == 'duration':
                record[key] = form_as_dict[key]
            if key[:2] == 'dm':
                record[key] = form_as_dict[key]
            if key[:6] == 'before':
                record[key] = form_as_dict[key]
            if key[:5] == 'after':
                record[key] = form_as_dict[key]

        record['bp'] = form_as_dict['bp']
        record['pulse'] = form_as_dict['pulse']
        record['temp'] = form_as_dict['temp']
        record['heart'] = form_as_dict['heart']
        record['lungs'] = form_as_dict['lungs']
        record['abd'] = form_as_dict['abd']
        record['anemia'] = form_as_dict['anemia']
        record['weight'] = form_as_dict['weight']
        record['sugar'] = form_as_dict['sugar']
        record['jaundice'] = form_as_dict['jaundice']
        record['cyanosis'] = form_as_dict['cyanosis']
        record['odemea'] = form_as_dict['odemea']
        record['advice'] = form_as_dict['advice']

        record['doctor'] = session['username']

        if "send_email" in form_as_dict:
            import Utils.utils as utils
            utils.send_email(record['email'], "Your prescription link is: "+ utils.SERVER+ "prescription/"+str(rand_id)+"/")

        p_info = db.personalized_info.find_one({"mobile":record["mobile"]})

        if p_info is None:
            p_info = dict()
            p_info["mobile"] = record["mobile"]
            p_info["status"] = "Verified"
            p_info["visits"] = ""
            p_info["inheritance"] = ""
            p_info["disability"] = ""
            p_info["previous_diseases"] = ""
            p_info["allergic_reactions"] = ""

        for key in record:
            if key.startswith("dx") or key.startswith("cc"):
                if record[key] in p_info["previous_diseases"].split(","):
                    continue
                if p_info["previous_diseases"] == "":
                    p_info["previous_diseases"] += record[key]
                else:
                    p_info["previous_diseases"] += "," + record[key]

        db.personalized_info.save(p_info)
        db.prescriptions.insert_one(record)

        import Utils.utils as utils
        utils.register_activity(record['doctor'] + " created a prescription")
        utils.send_prescription(record)
        utils.send_pinfo(p_info)
        url = '/prescription/' + str(rand_id) + '/'
        if 'print' in form_as_dict:
            return redirect(url+"pdf")
        return redirect(url)
    return render_template("customer/prescribe.html", **locals())


# created a prescription on mobile
@app.route('/prescribe/mobile/', methods=['GET', 'POST'])
def prescribe_mobile():
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    cur_date = datetime.date(datetime.now())
    if request.method == 'POST':
        form_as_dict = request.form.to_dict()
        record = dict()
        rand_id = random.randint(0, 999999)
        while True:
            if db.prescriptions.find_one({'prescriptionid': rand_id}):
                rand_id = random.randint(0, 999999)
            else:
                break

        record['prescriptionid'] = rand_id

        record['name'] = form_as_dict['name']
        record['age'] = form_as_dict['age']
        if 'male' in form_as_dict:
            record['sex'] = "Male"
        if 'female' in form_as_dict:
            record['sex'] = "Female"
        if 'other' in form_as_dict:
            record['sex'] = "Other"
        record['address'] = form_as_dict['address']
        record['mobile'] = form_as_dict['mobile']
        record['email'] = form_as_dict['email']
        record['date'] = form_as_dict['date']
        # dx = form_as_dict['dx'].replace("\r\n\r\n", "\r\n")
        for key in form_as_dict:
            if key[:2] == 'dx':
                record[key] = form_as_dict[key]
            if key[:2] == 'rx':
                record[key] = form_as_dict[key]
            if key[:2] == 'ix':
                record[key] = form_as_dict[key]
            if key[:2] == 'cc':
                record[key] = form_as_dict[key]
            if key[:4] == 'dose':
                record[key] = form_as_dict[key]
            if key[:8] == 'duration':
                record[key] = form_as_dict[key]
            if key[:2] == 'dm':
                record[key] = form_as_dict[key]
            if key[:6] == 'before':
                record[key] = form_as_dict[key]
            if key[:5] == 'after':
                record[key] = form_as_dict[key]

        record['bp'] = form_as_dict['bp']
        record['pulse'] = form_as_dict['pulse']
        record['temp'] = form_as_dict['temp']
        record['heart'] = form_as_dict['heart']
        record['lungs'] = form_as_dict['lungs']
        record['abd'] = form_as_dict['abd']
        record['anemia'] = form_as_dict['anemia']
        record['weight'] = form_as_dict['weight']
        record['sugar'] = form_as_dict['sugar']
        record['jaundice'] = form_as_dict['jaundice']
        record['cyanosis'] = form_as_dict['cyanosis']
        record['odemea'] = form_as_dict['odemea']
        record['advice'] = form_as_dict['advice']

        record['doctor'] = session['username']
        if "send_email" in form_as_dict:
            import Utils.utils as utils
            utils.send_email(record['email'], "Your prescription link is: "+ utils.SERVER+ "prescription/"+str(rand_id)+"/")

        p_info = db.personalized_info.find_one({"mobile": record["mobile"]})

        if p_info is None:
            p_info = dict()
            p_info["mobile"] = record["mobile"]
            p_info["status"] = "Verified"
            p_info["visits"] = ""
            p_info["inheritance"] = ""
            p_info["disability"] = ""
            p_info["previous_diseases"] = ""
            p_info["allergic_reactions"] = ""

        for key in record:
            if key.startswith("dx") or key.startswith("cc"):
                if record[key] in p_info["previous_diseases"].split(","):
                    continue
                if p_info["previous_diseases"] == "":
                    p_info["previous_diseases"] += record[key]
                else:
                    p_info["previous_diseases"] += "," + record[key]

        db.personalized_info.save(p_info)
        db.prescriptions.insert_one(record)

        import Utils.utils as utils
        utils.register_activity(record['doctor'] + " created a prescription")
        utils.send_prescription(record)
        utils.send_pinfo(p_info)

        url = '/prescription/' + str(rand_id) + '/'
        if 'print' in form_as_dict:
            return redirect(url+"pdf")
        return redirect(url)
    return render_template("mobile/customer/prescribe.html", **locals())


# views a prescription
@app.route('/prescription/<string:prescriptionID>/', methods=['GET', 'POST'])
def prescription(prescriptionID):
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    presobj = None
    for x in db.prescriptions.find({'prescriptionid': int(prescriptionID)}):
        presobj = x
    if session['username'] != presobj['doctor']:
        return "ACCESS DENIED"
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

    return render_template('customer/prescription.html', **locals())


# views a prescription on mobile
@app.route('/prescription/<string:prescriptionID>/mobile/', methods=['GET', 'POST'])
def prescription_mobile(prescriptionID):
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    presobj = None
    for x in db.prescriptions.find({'prescriptionid': int(prescriptionID)}):
        presobj = x
    if session['username'] != presobj['doctor']:
        return "ACCESS DENIED"
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
            rx["mode"] = presobj["rxmode" + id]
            rx_list.append(rx)

    presobj['ix'] = ix_list
    presobj['dx'] = dx_list
    presobj['cc'] = cc_list
    presobj['rx'] = rx_list

    return render_template('mobile/customer/prescription.html', **locals())


# pos print prescription: not working
@app.route('/prescription/<string:prescriptionID>/print/pos/', methods=['GET', 'POST'])
def prescriptionPOS(prescriptionID):
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    prescription = dict(db.prescriptions.find_one({'prescriptionid': int(prescriptionID)}))

    doct = dict(db.users.find_one({'username': str(session['username'])}))

    return "" #render_template('mobile/customer/pos.html', **locals())


# pos print prescription: not working
@app.route('/prescription/<string:prescriptionID>/str/', methods=['GET', 'POST'])
def prescriptionSTR(prescriptionID):
    prescription = dict(db.prescriptions.find_one({'prescriptionid': int(prescriptionID)}))
    return "" # str(prescription)


# emails a prescription
@app.route('/prescription/<string:prescriptionID>/email', methods=['GET', 'POST'])
def prescriptionMail(prescriptionID):
    pres = dict(db.prescriptions.find_one({'prescriptionid': int(prescriptionID)}))
    import Utils.utils as utils
    utils.send_email(pres['email'], "Your prescription link is: "+ utils.SERVER+ "prescription/"+str(prescriptionID)+"/")
    return "<script> window.close()</script>"


# generates PDF of a prescription
@app.route('/prescription/<string:prescriptionID>/pdf', methods=['GET', 'POST'])
def prescriptionPDF(prescriptionID):
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    # prescription =  find prescription by id
    form_as_dict = dict(db.prescriptions.find_one({'prescriptionid': int(prescriptionID)}))

    doct = dict(db.users.find_one({'username': str(session['username'])}))

    degree = doct['degrees']
    dxs = ""
    rxs = ""
    ixs = ""
    ccs = ""

    rxcnt = 0
    for key, value in form_as_dict.items():
        if "dx" == key[0:2]:
            dxs = dxs + value
        if "cc" == key[0:2]:
            ccs = ccs + value
        if "ix" == key[0:2]:
            ixs = ixs + value
        if "rxmode" == key[0:6]:
            rxcnt += 1

    rxmap = dict()
    for val in range(rxcnt):
        rxmap[str(val)] = []

    for key, value in form_as_dict.items():
        if key[0:6] == "rxmode":
            num = key[6:]
            rxmap[num].append((key[0:6], value))
        if key[0:2] == "rx" and key[2] != "m":
            num = key[2:]
            rxmap[num].append((key[0:2], value))
        if key[0:2] == "dm":
            num = key[2:]
            rxmap[num].append((key[0:2], value))
        if key[0:4] == "dose":
            num = key[4:]
            rxmap[num].append((key[0:4], value))
        if key[0:6] == "before":
            num = key[6:]
            rxmap[num].append((key[0:6], value))
        if key[0:5] == "after":
            num = key[5:]
            rxmap[num].append((key[0:5], value))
        if key[0:8] == "duration":
            num = key[8:]
            rxmap[num].append((key[0:8], value))

        drug_template0 = """
            {\\bf $ drugname $}  &  &  \\\\
                $ duration $ & $ dm $ &   \\\\
                $ dose $ & $ befaf $ \\\\
                    &             &         \\\\
            """
        drug_template1 = """
            {\\bf $ drugname $} &  &  \\\\
                $ duration $  &  &  \\\\
                    &             &         \\\\
            """
    total_drugs = rxcnt
    total_drugs_template = list()

    for key, value in rxmap.items():
        for itms in value:
            drugname = ""
            duration = ""
            dm = ""
            dose = ""
            befaf = ""
            if itms[0] == "rxmode" and itms[1] == "0":
                # print(value)
                for it in value:
                    if it[0] == "rx":
                        drugname = it[1]
                    if it[0] == "duration":
                        duration = it[1]
                    if it[0] == "dm":
                        dm = it[1]
                    if it[0] == "dose":
                        dose = it[1]
                    if it[0] == "before":
                        if "checked" in it[1]:
                            befaf = "Before Eating"
                        else:
                            befaf = ""
                    if it[0] == "after":
                        if "checked" in it[1]:
                            befaf = "After Eating"
                        else:
                            befaf = ""

                temp0 = drug_template0
                temp0 = temp0.replace("$ drugname $", drugname)
                temp0 = temp0.replace("$ duration $", duration)
                temp0 = temp0.replace("$ dm $", dm)
                temp0 = temp0.replace("$ dose $", dose)
                temp0 = temp0.replace("$ befaf $", befaf)
                total_drugs_template.append(temp0)

            if itms[0] == "rxmode" and itms[1] == "1":
                for it in value:
                    if it[0] == "rx":
                        drugname = it[1]
                    if it[0] == "duration":
                        duration = it[1]
                temp1 = drug_template1
                temp1 = temp1.replace("$ drugname $", drugname)
                temp1 = temp1.replace("$ duration $", duration)
                total_drugs_template.append(temp1)

    rxs = """"""
    for i in range(total_drugs):
        rxs = rxs + total_drugs_template[i]

    tex = open('prescriptions/template.tex').read()

    # replace fields
    tex = tex.replace("$ ptid $", str(form_as_dict['prescriptionid']))
    tex = tex.replace("$ drname $", doct['fullname'])
    tex = tex.replace("$ degree $", degree)
    tex = tex.replace("$ cadd $", doct['caddr'])
    tex = tex.replace("$ cmobile $",  doct['mobile'])
    # tex = tex.replace("$ phone $", form_as_dict['mobile'])
    tex = tex.replace("$ date $", form_as_dict['date'])
    tex = tex.replace("$ ptname $", form_as_dict['name'])
    tex = tex.replace("$ ptage $", form_as_dict['age'])
    tex = tex.replace("$ ptsex $", form_as_dict['sex'])
    tex = tex.replace("$ ptemail $", form_as_dict['email'])
    tex = tex.replace("$ ptmobile $", form_as_dict['mobile'])
    tex = tex.replace("$ ptaddress $", form_as_dict['address'])
    tex = tex.replace("$ dx $", dxs)
    tex = tex.replace("$ cc $", ccs)
    tex = tex.replace("$ ix $", ixs)
    tex = tex.replace("$ rx $", rxs)
    tex = tex.replace("$ bp $", form_as_dict['bp'])
    tex = tex.replace("$ pulse $", form_as_dict['pulse'])
    tex = tex.replace("$ temperature $", form_as_dict['temp'])
    tex = tex.replace("$ heart $", form_as_dict['heart'])
    tex = tex.replace("$ lungs $", form_as_dict['lungs'])
    tex = tex.replace("$ abd $", form_as_dict['abd'])
    tex = tex.replace("$ anemia $", form_as_dict['anemia'])
    tex = tex.replace("$ jaundice $", form_as_dict['jaundice'])
    tex = tex.replace("$ cyanosis $", form_as_dict['cyanosis'])
    tex = tex.replace("$ odemea $", form_as_dict['odemea'])

    tex_file = open("prescriptions/files/" + prescriptionID + ".tex", "w")
    tex_file.write(tex)
    tex_file.close()

    import os
    os.system("xelatex --interaction=batchmode prescriptions/files/" + prescriptionID + ".tex > /dev/null 2>&1")
    os.system("cp " + prescriptionID + ".pdf" + " prescriptions/files/" + prescriptionID + ".pdf")

    static_file = open('prescriptions/files/' + prescriptionID + '.pdf', 'rb')
    return send_file(static_file, attachment_filename=prescriptionID + '.pdf')


# returns string matching suggestions from backend
@app.route('/suggestions/', methods=['GET', 'POST'])
def suggestions(cryptography=None):
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    import json

    if request.method == 'POST':
        from Utils import utils
        response = list(utils.string_matching_request(dict(request.json)))
        return json.dumps(response)
    return json.dumps([["RX-azyth","All square \nat the interval"],["DX-napa","d"], ["IX-napa extra","i"], ["CC-salora","c"]])


# returns machine learning suggestions from backend
@app.route('/suggestionsML/', methods=['GET', 'POST'])
def suggestionsML(cryptography=None):
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    if not auth.is_logged_in():
        return redirect(url_for("auth.auth_login"))
    import json

    if request.method == 'POST':
        from Utils import utils
        response = utils.ml_request(dict(request.json))
        return json.dumps(response)
    return json.dumps([["RX-azyth","All square \nat the interval",["s","w"]],["DX-napa","d",[]], ["IX-napa extra","i",[]], ["CC-salora","c",[]]])