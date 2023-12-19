import flask
from flask import flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy 
from flask_cors import CORS
from flask import request


import sqlalchemy as sa

import models

class HRException(Exception): pass

app = flask.Flask("hrms")
CORS(app)
db = models.SQLAlchemy(model_class=models.HRDBBase)


@app.route("/")
def index():
    return flask.render_template("index.html")
  
@app.route("/employees")
def employees():
    query = db.select(models.Employee).order_by(models.Employee.first_name)
    users = db.session.execute(query).scalars()
    ret = []
    for user in users:
        details={"id" : user.id,
            "fname" : user.first_name,   
           "lname" : user.last_name,
           "title" : user.title.title,
           "email" : user.email,
           "phone" : user.phone
           }
        ret.append(details)
    return flask.jsonify(ret)

@app.route("/employees/<int:empid>", methods=(["GET","POST"]))
def employee_details(empid):
    try:
        query = db.select(models.Employee).where(models.Employee.id == empid)
        user = db.session.execute(query).scalar()
        leave_query = db.select(sa.func.count(models.Leave.id)).where(models.Leave.employee_id == empid)
        leave = db.session.execute(leave_query).scalar()
        if flask.request.method == "POST":
            leave_data = request.get_json()
            date = leave_data.get('date')
            reason = leave_data.get('reason')
            if not date or not reason:
                return flask.jsonify({'error': 'Enter data'}), 400
            insert_data = models.Leave(employee_id=empid ,date=date, reason=reason)
            db.session.add(insert_data)
            db.session.commit()
            return flask.jsonify({'message': 'Leave submitted successfully'}), 200
        
    except HRException as e:
        raise HRException (f'Employee with id: {empid} does not exist')
    
    ret = []
    if (user.title.max_leaves - leave <= 0):
        details = details = { "id": user.id,
        "fname" : user.first_name,   
           "lname" : user.last_name,
           "title" : user.title.title,
           "email" : user.email,
           "phone" : user.phone,
           "leaves_taken" : leave,
           "leaves_remaining" : 0,
           "total_leaves" : user.title.max_leaves}
        ret.append(details)
    
    else:
        details = { "id": user.id,
            "fname" : user.first_name,   
            "lname" : user.last_name,
            "title" : user.title.title,
            "email" : user.email,
            "phone" : user.phone,
            "leaves_taken" : leave,
            "leaves_remaining" : user.title.max_leaves - leave,
            "total_leaves" : user.title.max_leaves}
        ret.append(details)

    return flask.jsonify(ret)
