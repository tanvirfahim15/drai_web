from random import randint
from flask import render_template, request, session, Blueprint, redirect, url_for, flash
from Database.database import db
import string
import re
from datetime import datetime
from datetime import timedelta
from bson import ObjectId
import json

app = Blueprint('etc', __name__)


@app.route('/about_us/', methods=['GET', 'POST'])
def about_us():
    txt = open("Path/etc/about_us.txt").read()
    return render_template('etc/about_us.html', **locals())


@app.route('/about_us/mobile/', methods=['GET', 'POST'])
def about_us_mobile():
    txt = open("Path/etc/about_us.txt").read()
    return render_template('mobile/etc/about_us.html', **locals())


@app.route('/terms/', methods=['GET', 'POST'])
def terms():
    txt = open("Path/etc/terms.txt").read()
    return render_template('etc/terms.html', **locals())


@app.route('/terms/mobile/', methods=['GET', 'POST'])
def terms_mobile():
    txt = open("Path/etc/terms.txt").read()
    return render_template('mobile/etc/terms.html', **locals())


@app.route('/faq/', methods=['GET', 'POST'])
def faq():
    txt = open("Path/etc/faq.txt").read()
    return render_template('etc/faq.html', **locals())


@app.route('/faq/mobile/', methods=['GET', 'POST'])
def faq_mobile():
    txt = open("Path/etc/faq.txt").read()
    return render_template('mobile/etc/faq.html', **locals())


@app.route('/privacy_policy/', methods=['GET', 'POST'])
def privacy_policy():
    txt = open("Path/etc/pp.txt").read()
    return render_template('etc/privacy_policy.html', **locals())


@app.route('/privacy_policy/mobile/', methods=['GET', 'POST'])
def privacy_policy_mobile():
    txt = open("Path/etc/pp.txt").read()
    return render_template('mobile/etc/privacy_policy.html', **locals())


@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    msg = None
    if request.method == 'POST':
        data = dict()
        data["name"] = request.form.to_dict()["name"]
        data["email"] = request.form.to_dict()["email"]
        data["comment"] = request.form.to_dict()["comment"]
        db.comments.insert_one(data)
        msg = "Your comment has been recorded."
        from Utils import utils
        utils.send_email(utils.SERVER_EMAIL,"New comment on Doctor AI from: " +str(data["name"]))
    return render_template('etc/contact.html', **locals())


@app.route('/contact/mobile/', methods=['GET', 'POST'])
def contact_mobile():
    msg = None
    if request.method == 'POST':
        data = dict()
        data["name"] = request.form.to_dict()["name"]
        data["email"] = request.form.to_dict()["email"]
        data["comment"] = request.form.to_dict()["comment"]
        db.comments.insert_one(data)
        msg = "Your comment has been recorded."
        from Utils import utils
        utils.send_email(utils.SERVER_EMAIL,"New comment on Doctor AI")
    return render_template('mobile/etc/contact.html', **locals())
