# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask import make_response
from flask import request
from flask import abort
import jwt
import datetime
from functools import wraps
import pymysql.cursors
from flask_swagger_ui import get_swaggerui_blueprint

db = pymysql.connect(       host='remotemysql.com',
                             user='w1oDULvgJe',
                             password='dDMif4qtml',
                             db='w1oDULvgJe',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

conn = db.cursor()

app = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Flask-Todo-API-JWT"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


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

    token = request.headers['token']
   
    token = jwt.decode(token, app.config['SECRET_KEY'])
     
    userid = token["userid"]

    if not request.json or not 'title' in request.json:
        abort(400)
    title = request.json['title']
    description =request.json['description']
    done = request.json['done']
    enddate = request.json['enddate']
    
    query ="""
    insert into tblTask
    (Description, Done, EndDate, Title, UserId)
    values
    (%s, %s, %s, %s, %s)
    """
    conn.execute(query,(description,done,enddate,title,userid))
    
    db.commit()

    return  jsonify({"task" :True}), 201

@app.route('/todo/api/tasks/<int:task_id>', methods=['PUT'])
@auth
def update_task(task_id):
    token = request.headers['token']

    token = jwt.decode(token, app.config['SECRET_KEY'])

    userid = token["userid"]

    title = request.json['title']

    description =request.json['description']

    done = request.json['done']

    enddate = request.json['enddate']
    
    query ="""
    update tblTask 
    set CreationDate = CreationDate
  , Description = %s
  , Done = %s
  , EndDate = %s
  , Title = %s
  , UserId = %s 
    where id = %s
    """
    conn.execute(query,(description,done,enddate,title,userid,task_id))
    
    db.commit()

    return jsonify({'task': True }) ,200

@app.route('/todo/api/tasks/<int:task_id>', methods=['DELETE'])
@auth
def delete_task(task_id):
    token = request.headers['token']
   
    token = jwt.decode(token, app.config['SECRET_KEY'])
    
    userid = token["userid"]
    
    query ="DELETE FROM tblTask WHERE UserId =%s AND id =%s"

    conn.execute(query,(userid,task_id))
    
    db.commit()


    return jsonify({'tasks': True})
  


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)
