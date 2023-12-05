import flask
import models

from flask_sqlalchemy import SQLAlchemy

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


@app.route("/employees/<int:empid>")
def employee_details(empid):
    query = db.select(models.Employee).where(models.Employee.id == empid)
    user = db.session.execute(query).scalar()
    return flask.render_template("userdetails.html", user = user)
