import flask
from flask import flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy 
import sqlalchemy as sa

import models

class HRException(Exception): pass

app = flask.Flask("hrms")
db = models.SQLAlchemy(model_class=models.HRDBBase)

@app.route("/")
def index():
    return flask.render_template("index.html")
  
@app.route("/employees")
def employees():
    query = db.select(models.Employee)
    users = db.session.execute(query).scalars()
    ret = {}
    for user in users:
        ret[user.id] = {"fname" : user.first_name,   
           "lname" : user.last_name,
           "title" : user.title.title,
           "email" : user.email,
           "phone" : user.phone
           }
    return flask.jsonify(ret)

@app.route("/employees/<int:empid>", methods=(["GET","POST"]))
def employee_details(empid):
    try:
        query = db.select(models.Employee).where(models.Employee.id == empid)
        user = db.session.execute(query).scalar()
        leave_query = db.select(sa.func.count(models.Leave.id)).where(models.Leave.employee_id == empid)
        leave = db.session.execute(leave_query).scalar()
        if flask.request.method == "POST":
            date = flask.request.form['Date']   
            reason = flask.request.form['Reason']
            leave = models.Leave(employee_id=empid,
                                date=date,
                                reason=reason)
            db.session.add(leave)
            db.session.commit()
            return redirect(url_for("employees"))
        
    except HRException as e:
        raise HRException (f'Employee with id: {empid} does not exist')

    ret = { "id": user.id,
        "fname" : user.first_name,   
           "lname" : user.last_name,
           "title" : user.title.title,
           "email" : user.email,
           "phone" : user.phone,
           "leaves_taken" : leave,
           "leaves_remaining" : user.title.max_leaves - leave,
           "total_leaves" : user.title.max_leaves}
    return flask.jsonify(ret)
