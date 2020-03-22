# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask import make_response
from flask import request
from flask import abort
import jwt
import datetime
from functools import wraps
import pymysql.cursors


db = pymysql.connect(       host='remotemysql.com',
                             user='w1oDULvgJe',
                             password='dDMif4qtml',
                             db='w1oDULvgJe',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

conn = db.cursor()

app = Flask(__name__)


tasks = [
    {
        'id': 1,
        'title': 'FLASK API',
        'description': 'Flask ile Api Olustur.', 
        'done': True
    },
    {
        'id': 2,
        'title': 'REACT-FLASK',
        'description': 'Flask Api ile React Uygulaması Olustur.', 
        'done': False
    }
    ,{
        'id': 3,
        'title': 'FLASK API MySQL',
        'description': 'Flask Api ile MySQL Bağlantısını olustur.', 
        'done': False
    }
    ,{
        'id': 4,
        'title': 'FLASK API JWT',
        'description': 'Flask Api JWT Ekle.', 
        'done': True
    }
    ,{
        'id': 5,
        'title': 'REACT-NATİVE FLASK',
        'description': 'Flask Api İle React-Native Uygulaması Geliştir.', 
        'done': False
    }
]

app.config['SECRET_KEY'] ='Bu bir pyFlask-JWT Api Projesidir.'

def auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            token = kwargs['token']
        except:
            token = request.headers['token'] or \
                request.form.get('token')

        if not token:
            return jsonify({'message': 'Token required!'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],  algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token invalid!'}), 403

        return f(*args,**kwargs)
    
    return wrapper

@app.route('/todo/api/login',methods=['POST'])
def get_login():
    
    username = request.json['username']
    password = request.json['password']
    token = ''
    query ="""  
                select COUNT(*) as count,Password as password,UserId as userid 
                from tblUser where NickName =%s 
                group by Password,UserId"""

    conn.execute(query,(username))
    res = conn.fetchone()
    if isinstance(res, type(None)):
        token = 'Invalid username or password'
    elif res["count"] ==1:

        if password == str(res["password"]):
           
            token = jwt.encode({
                'user': username,
                'userid' :res["userid"],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                }, app.config['SECRET_KEY'], algorithm='HS256')
           
     
        else:
            token = 'Invalid username or password'
    return jsonify({'token': str(token)})


@app.route('/todo/api/tasks', methods=['GET'])
@auth
def get_tasks():
    token = request.headers['token']
   
    token = jwt.decode(token, app.config['SECRET_KEY'])
    
    userid = token["userid"]
    
    query ="SELECT * FROM tblTask WHERE UserId =%s ORDER BY id ASC"
    
    conn.execute(query,(userid))
    
    res = conn.fetchall()

    return jsonify({'tasks': res})


@app.route('/todo/api/token', methods=['GET'])
@auth
def get_token():
    token = request.headers['token']
    token = jwt.decode(token, app.config['SECRET_KEY'])
    print(token["user"])
    return jsonify({'task ':token["user"]})



@app.route('/todo/api/tasks/<int:task_id>', methods=['GET'])
@auth
def get_task(task_id):
    
    token = request.headers['token']
   
    token = jwt.decode(token, app.config['SECRET_KEY'])
    
    userid = token["userid"]
    
    query ="SELECT * FROM tblTask WHERE UserId =%s AND id =%s"
    
    conn.execute(query,(userid,task_id))
    
    res = conn.fetchone()

    return jsonify({'tasks': res})


@app.route('/todo/api/tasks', methods=['POST'])
@auth
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

@app.route('/todo/api/tasks/<int:task_id>', methods=['PUT'])
@auth
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})

@app.route('/todo/api/tasks/<int:task_id>', methods=['DELETE'])
@auth
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)
