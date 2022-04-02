from flask import Flask, render_template, session, flash,request
import os
from Database.database import db
from Path.Auth.auth import app as auth
from Path.Customer.dashboard import app as customer_dashboard
from Path.Customer.profile import app as customer_profile
from Path.Andriod.android import app as android
from Path.etc.etc import app as etc
from Path.Admin.admin import app as admin
from bson import ObjectId
from waitress import serve
from Utils import utils
utils.load_config()


app = Flask(__name__)
app.secret_key = 'UIrfBBN*E(DNJ'


app.register_blueprint(auth)

app.register_blueprint(customer_dashboard)
app.register_blueprint(customer_profile)
app.register_blueprint(android)
app.register_blueprint(etc)
app.register_blueprint(admin)


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("home.html", **locals())


@app.route("/mobile/", methods=['GET', 'POST'])
def home_mobile():
    return render_template("mobile/home.html", **locals())



if __name__ == "__main__":

    app.secret_key = 's@$#EW77979***78%^y secret key'
    #port = int(os.environ.get('PORT', 5000))
    #app.run(host='192.168.1.105', port=5003)
    #app.run(host='127.0.0.1', port=5002)
    serve(app, host='0.0.0.0', port=80)