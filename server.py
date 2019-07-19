from flask import Flask, render_template, request, redirect, flash, session
from mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key= "so secret"
import humanize
import datetime

import re
EMAIL_REGEX= re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PW_REGEX= re.compile(r'^[a-zA-Z.+_-]+[0-9._-]+$')

from flask_bcrypt import Bcrypt        
bcrypt = Bcrypt(app)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/create", methods=["POST"])
def create():
	valid=True

	mysql=connectToMySQL("tv_shows")
	query=(f"SELECT email FROM users where email= %(email)s")
	data={
	'email': request.form["email"]
	}
	result=mysql.query_db(query, data)
	if result!=False:
		flash("this email is already registered")
		valid= False

	if request.form['pw']!=request.form['pwconf']:
		flash("Passwords do not match!")
		valid=False
	if len(request.form["username"])<5:
		flash("username must be at least 5 characters")
		valid=False
	if len(request.form["fname"])<2:
		flash("Please enter a first name")
		valid=False
	if len(request.form["lname"])<2:
		flash("Please enter a last name")
		valid=False
	if not EMAIL_REGEX.match(request.form["email"]):
		flash("Please enter valid email")
		valid=False
	if not PW_REGEX.match(request.form['pw']):
		flash("Passwords must be at least 8 characters and contain at least one letter and one number")
		valid=False

	if valid==False:
		return redirect("/")
	if valid==True:
		pw_hash = bcrypt.generate_password_hash(request.form['pw'])

		mysql=connectToMySQL("tv_shows")
		query= "INSERT INTO users (username, fname, lname, email, pw, created_at, updated_at) VALUES(%(un)s, %(fn)s, %(ln)s, %(em)s, %(pw)s, now(), now())"
		data= {
			'un':request.form["username"], 
			'fn':request.form["fname"], 
			'ln':request.form["lname"], 
			'em':request.form["email"], 
			'pw':pw_hash
		}
		result=mysql.query_db(query, data)

		session['userid'] = result

		return redirect("/wall")

@app.route("/login", methods=["POST"])
def login():
	mysql=connectToMySQL("tv_shows")
	query=(f"SELECT * FROM users where email= %(email)s")
	data={
	'email': request.form["email"]
	}
	result=mysql.query_db(query, data)
	session['user']=result
	if len(result)>0:
		if bcrypt.check_password_hash(result[0]['pw'], request.form['pw']):
			session['userid'] = result[0]['id']
			return redirect("/wall")
	flash("not valid login credentials")
	return redirect("/")

@app.route("/wall")
def mainpage():
	mysql=connectToMySQL("tv_shows")
	query=(f"SELECT * FROM users where users.id={session['userid']}")
	user=mysql.query_db(query)
	print("**************", user)

	return render_template("user_page.html", user=user)


if __name__ == "__main__":
	app.run(debug=True)