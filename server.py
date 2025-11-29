from flask import Flask, request, jsonify, render_template, send_from_directory, make_response
from flask_socketio import SocketIO
from blockchain import Blockchain
from pbft import PBFT
import os
import json
from random import *
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

app = Flask(__name__)
socketio = SocketIO(app)

blockchain = Blockchain()
pbft = PBFT([blockchain])

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def cleanup_data():
    with open("database/users.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for user in data["users"]:
            user["data"]["logined"] = False 
            with open('database/users.json', 'w') as f:
                json.dump(data, f, ensure_ascii=True, indent=4)

    print("Очистка данных входа")
                    
                        

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=cleanup_data,
    trigger=IntervalTrigger(minutes=30),
    id='reloadlog',
    name='reloadLogin',
    replace_existing=True
)

scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/keyword/')
def keyword():
    return render_template('keyword.html')

@app.route('/doc/')
def doc():
    return render_template('doc.html')

@app.route('/reg/', methods=['POST'])
def getUserData():
    id = request.form['tag']

    with open("database/users.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for user in data["users"]:
            if (user["data"]["uid"] == id):
                return jsonify({"n": "Set-Cookie", "ci": user["data"]["cookie-id"], "hasinbd": True, "status": "success"})

        return jsonify({"hasinbd": False, "status": "success"})
    

@app.route('/addMember/', methods=['POST'])
def addMember():
    with open("database/users.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for user in data["users"]:
            if (user["data"]["uid"] == request.form['uid']):
                return jsonify({"status": "success", "res": -1})
            if (user["data"]["cookie-id"] == request.cookies.get('Set-Cookie')):
                sender = user["data"]

    if sender["priv"] == "admin":
        with open("database/users.json", "r", encoding="utf-8") as f:
            data = json.load(f)

            datanew = {
                "uid": request.form["uid"],
                "name": request.form["name"],
                "surname": request.form["surname"],
                "priv": request.form["priv"],
                "keyword": "",
                "cookie-id": str(randint(0, 1000000)),
                "logined": False
            }

            datafolder = {
                "data": datanew 
            }

            data["users"].append(datafolder)

            with open('database/users.json', 'w') as f:
                json.dump(data, f, ensure_ascii=True, indent=4)

        return jsonify({"status": "success", "res": 1})
    else:
        return jsonify({"status": "success", "res": 0})

@app.route('/keyword/', methods=['POST'])
def getUserWord():
    word = request.form['word']

    with open("database/users.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for user in data["users"]:
            if (user["data"]["cookie-id"] == request.cookies.get('Set-Cookie')):
                if (user["data"]["keyword"] != ""):
                    if (word == user["data"]["keyword"]):
                        user["data"]["logined"] = True 
                        with open('database/users.json', 'w') as f:
                            json.dump(data, f, ensure_ascii=True, indent=4)
                        return jsonify({"status": "success", "success": 1}) 
                    else:
                        return jsonify({"status": "success", "success": 0}) 
                else:
                    user["data"]["keyword"] = word
                    user["data"]["logined"] = True
                    with open('database/users.json', 'w', encoding='utf8') as f:
                        json.dump(data, f, ensure_ascii=True, indent=4)
                    return jsonify({"status": "success", "success": 1})   

        return jsonify({"status": "success", "success": 0})   
        
               
    
@app.route('/autoreg/', methods=['GET'])
def getAutoUserReg():
    if request.cookies.get("Set-Cookie"):
        with open("database/users.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for user in data["users"]:
                if (user["data"]["cookie-id"] == request.cookies.get('Set-Cookie')):
                    if (user["data"]["logined"]):
                        return jsonify({"status": "success", "hasinbd": 1})
                    else:
                        return jsonify({"status": "success", "hasinbd": 0})
        return jsonify({"status": "success", "hasinbd": -2})            
    else:
        return jsonify({"status": "success", "hasinbd": -1})
    

@app.route('/isadmin/', methods=['GET'])
def isAdmin():
    with open("database/users.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for user in data["users"]:
            if (user["data"]["cookie-id"] == request.cookies.get('Set-Cookie')):
                if (user["data"]["priv"] == "admin"):
                    return jsonify({"status": "success", "res": True})
                else:
                    return jsonify({"status": "success", "res": False})
                

@app.route('/getIP/', methods=['GET'])
def getIP():
    with open("database/config.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return jsonify({"status": "success", "ip": data["ip"], "port": data["port"]})
                

@app.route('/getName/', methods=['GET'])
def getName():
    with open("database/users.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for user in data["users"]:
            if (user["data"]["cookie-id"] == request.cookies.get('Set-Cookie')):
                return jsonify({"status": "success", "fullname": user["data"]["name"] + " " + user["data"]["surname"]})
    

@app.route('/send_document', methods=['POST'])
def send_document():
    file = request.files['document']
    to = request.form['to']
    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    touser = 0

    with open("database/users.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for user in data["users"]:
            if (user["data"]["cookie-id"] == request.cookies.get('Set-Cookie')):
                sender = user["data"]
            if (user["data"]["name"] == to.split(" ")[0]) and (user["data"]["surname"] == to.split(" ")[1]):
                touser = user["data"]

    if (touser != 0):
        data = {
            'document': filename,
            'to': touser["uid"],
            'from': sender["uid"],
        }

        pbft.request(data)
        return jsonify({"status": "success", "res": True})
    else:
        return jsonify({"status": "success", "res": False})

@app.route('/getDocuments/', methods=['POST'])
def get_documents():
    with open("database/users.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for user in data["users"]:
            if (user["data"]["cookie-id"] == request.cookies.get("Set-Cookie")):
                documents = [block.data for block in blockchain.chain if isinstance(block.data, dict) and block.data.get("to") == user["data"]["uid"]]
            
    for document in documents:
        with open("database/users.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for user in data["users"]:
                if (user["data"]["uid"] == document.get("from")):
                    document["from"] = user["data"]["name"] + " " + user["data"]["surname"]
                    break

    return jsonify(documents)


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    with open("database/config.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    socketio.run(app, host='0.0.0.0', port=int(data["port"]), debug=True)