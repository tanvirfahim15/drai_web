from Database.database import db
import time

SERVER = "http://draibd.com/"
SERVER_EMAIL = "draibd247@gmail.com"
SUGGESTION_LIMIT = 10
MAX_FILE_SIZE = 500000



def send_sms(number, text):
    #print(number,text)
    return


# registers activity to the log
def register_activity(act):
    data = dict()
    import datetime
    data["time"] = datetime.datetime.now()
    data["act"] = act
    db.activities.insert_one(data)


# sends email
def send_email(addr, text):
    from mailjet_rest import Client
    import os
    api_key = '65e55755f2b8f0557791e3e5ac8728cf'
    api_secret = '051969db69a6cb19505381b8da5bc79d'
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": SERVER_EMAIL,
                    "Name": "DoctorAI"
                  },
                "To": [
                    {
                        "Email": addr,
                        "Name": addr
                    }
                ],
                "Subject": "Message from Doctor AI",
                "TextPart": text,
                "HTMLPart": text,
                "CustomID": "AppGettingStartedTest"
            }
        ]
    }
    print(data)
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())


# generates random string for captcha
def rand_str():
    import string
    import random
    S = 5
    ran = ""
    for i in range(S):
        ran += random.choice(string.ascii_uppercase+string.ascii_lowercase + string.digits)
    return ran


# generates image ffor captcha
def captcha():
    txt = rand_str()
    url = "https://api.imgbun.com/png?key=027f35ccb0b26359f0f2bba58430de77&text=" + txt + "&color=000000&background=FFFFFF&size=24"
    import requests
    return requests.get(url).json()["direct_link"], txt


# sends prescription to backend
def send_prescription(record):
    import requests
    from cryptography.fernet import Fernet
    import json
    fernet = Fernet(b'gIXN2ZIZYQ9fJwpLr3L0GmhCh4wgylVXpeet7YEUgVs=')
    password = fernet.encrypt("samiullah".encode()).decode()
    record["pass"] = password
    response = requests.post("http://3.110.94.61:8080/prescription", data=record)
    return json.loads(response.content)


# sends personalized information to backend
def send_pinfo(record):
    import requests
    from cryptography.fernet import Fernet
    import json
    fernet = Fernet(b'gIXN2ZIZYQ9fJwpLr3L0GmhCh4wgylVXpeet7YEUgVs=')
    password = fernet.encrypt("samiullah".encode()).decode()
    record["pass"] = password
    response = requests.post("http://3.110.94.61:8080/perinfo", data=record)
    return json.loads(response.content)


# sends suggestion request to backend using ml
def ml_request(input_dictionary):
    import requests
    from cryptography.fernet import Fernet
    import json
    fernet = Fernet(b'gIXN2ZIZYQ9fJwpLr3L0GmhCh4wgylVXpeet7YEUgVs=')
    password = fernet.encrypt("samiullah".encode()).decode()
    input_dictionary["pass"] = password
    input_dictionary["limit"] = SUGGESTION_LIMIT
    response = requests.post("http://3.110.94.61:8080/", data=input_dictionary)
    return json.loads(response.content)


# sends suggestion request to backend using string matching
def string_matching_request(input_dictionary):
    import requests
    from cryptography.fernet import Fernet
    import json
    fernet = Fernet(b'gIXN2ZIZYQ9fJwpLr3L0GmhCh4wgylVXpeet7YEUgVs=')
    password = fernet.encrypt("samiullah".encode()).decode()
    input_dictionary["pass"] = password
    input_dictionary["limit"] = SUGGESTION_LIMIT
    response = requests.post("http://3.110.94.61:8080/suggestions", data=input_dictionary)
    return json.loads(response.content)


# sends data to backend
def entry1(input_dictionary):
    import requests
    from cryptography.fernet import Fernet
    import json
    fernet = Fernet(b'gIXN2ZIZYQ9fJwpLr3L0GmhCh4wgylVXpeet7YEUgVs=')
    password = fernet.encrypt("samiullah".encode()).decode()
    input_dictionary["pass"] = password
    response = requests.post("http://3.110.94.61/manual_input", data=input_dictionary)
    return ""


# sends data to backend
def entry2(input_dictionary):
    import requests
    from cryptography.fernet import Fernet
    import json
    fernet = Fernet(b'gIXN2ZIZYQ9fJwpLr3L0GmhCh4wgylVXpeet7YEUgVs=')
    password = fernet.encrypt("samiullah".encode()).decode()
    input_dictionary["pass"] = password
    response = requests.post("http://3.110.94.61/add_weights", data=input_dictionary)
    return ""


# sends data to backend
def entry2list(input_dictionary):
    import requests
    from cryptography.fernet import Fernet
    import json
    fernet = Fernet(b'gIXN2ZIZYQ9fJwpLr3L0GmhCh4wgylVXpeet7YEUgVs=')
    password = fernet.encrypt("samiullah".encode()).decode()
    input_dictionary = dict()
    input_dictionary["pass"] = password
    response = requests.post("http://3.110.94.61:8080/unique_list", data=input_dictionary)
    return json.loads(response.content)


# loads configuration from file
def load_config():
    global SERVER, SERVER_EMAIL, SUGGESTION_LIMIT, MAX_FILE_SIZE
    f = open("config.txt").read()
    SERVER = f.split("\n")[0]
    SERVER_EMAIL = f.split("\n")[1]
    SUGGESTION_LIMIT = int(f.split("\n")[2])
    MAX_FILE_SIZE = int(f.split("\n")[3])
    return SERVER, SERVER_EMAIL, SUGGESTION_LIMIT, MAX_FILE_SIZE


# writes configuration from file
def write_config(SERVER, SERVER_EMAIL, SUGGESTION_LIMIT, MAX_FILE_SIZE):
    f = open("config.txt" , "w")
    f.write(SERVER+"\n")
    f.write(SERVER_EMAIL+"\n")
    f.write(str(SUGGESTION_LIMIT)+"\n")
    f.write(str(MAX_FILE_SIZE)+"\n")
    f.close()
    load_config()
