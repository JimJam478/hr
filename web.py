import flask
from flask import flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy 
import sqlalchemy as sa

import models

app = flask.Flask("hrms")
db = models.SQLAlchemy(model_class=models.HRDBBase)

@app.route("/")
def index():
    return flask.render_template("index.html")
  
@app.route("/employees")
def employees():
    query = db.select(models.Employee).order_by(models.Employee.first_name)
    users = db.session.execute(query).scalars()
    return flask.render_template("userlist.html", users = users)

@app.route("/employees/<int:empid>", methods=(["GET","POST"]))
def employee_details(empid):
    query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(query).scalar()
    leave_query = db.select(sa.func.count(models.Leave.id)).where(models.Leave.employee_id == empid)
    leave = db.session.execute(leave_query).scalar()
    if flask.request.method == "POST":
        date = flask.request.form['Date']
        reason = flask.request.form['Reason']
        query = models.Leave(employee_id=empid,
                            date=date,
                            reason=reason)
        db.session.add(query)
        db.session.commit()
        return redirect(url_for("employees"))

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