import flask
from flask import flash
from flask_sqlalchemy import SQLAlchemy

import models


emp = []

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


def employee_details(empid):
    query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(query).scalar()
    return flask.render_template("userdetails.html", user = user)


def get_leave_details(empid):
    query = (
        db.select(
            db.func.count(models.Employee.id),
            models.Designation.max_leaves,
        ).where(
            models.Employee.id == empid,
            models.Employee.id == models.Leave.employee_id,
            models.Employee.title_id == models.Designation.id,
        ).group_by(
            models.Employee.id,
            models.Employee.first_name,
            models.Employee.last_name,
            models.Designation.max_leaves,
        )
    )
    leave_detail = db.session.execute(query).fetchall()
    if leave_detail:
        (
            leaves_taken,
            total_leaves,
        ) = leave_detail[0]
        leaves_remaining = total_leaves - leaves_taken
    else:
        query = (
            db.select(
            models.Designation.max_leaves
            )
            .where(
                models.Employee.id == empid, models.Employee.title_id == models.Designation.id
            )
        )
        leave_detail = db.session.execute(query).fetchall()
        (
           total_leaves,
        ) = leave_detail[0]
        leaves_taken = 0
        leaves_remaining = total_leaves
    leave_detail = {
        'leaves_taken':leaves_taken,
        'leaves_remaining':leaves_remaining,
        'total_leaves':total_leaves
    }
    return leave_detail

@app.route("/employees/<int:empid>")
def employee_details(empid):
    leave_detail = get_leave_details(empid)
    query = db.select(models.Employee).order_by(models.Employee.first_name)
    users = db.session.execute(query).scalars()
    query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(query).scalar()
    return flask.render_template("userdetails.html", user = user,users = users, leave=leave_detail)

@app.route("/<int:empid>/add_leave", methods = ['GET','POST'])
def add_employee_leaves(empid):
    leave_detail = get_leave_details(empid)
    query = db.select(models.Employee).order_by(models.Employee.first_name)
    users = db.session.execute(query).scalars()
    query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(query).scalar()
    if flask.request.method == "POST":
        date = flask.request.form['Date']
        reason = flask.request.form['Reason']
        query = models.Leave(employee_id=empid,
                            date=date,
                            reason=reason)
        db.session.add(query)
        db.session.commit()
    return flask.render_template("add_leaves.html",empid=empid, user=user, users=users,leave = leave_detail)