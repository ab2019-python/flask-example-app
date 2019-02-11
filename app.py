from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, make_response, abort
from bson.objectid import ObjectId
import hashlib
import uuid

app = Flask(__name__)
client = MongoClient()
db = client.ab2019


def get_user_from_session():
	session_id = request.cookies.get('session_id')
	session = db.sessions.find_one({
		"session_id": session_id,
	})

	if not session:
		return

	user_id = session['user_id']
	user = db.users.find_one({
		"_id": user_id,
		"is_admin": True,
	})

	return user

@app.route("/remove/<document_id>")
def remove(document_id):
	if not get_user_from_session():
		abort(401)

	db.messages.remove({
		"_id": ObjectId(document_id)
	})
	return redirect("/")

@app.route("/edit/<document_id>", methods=["GET", "POST"])
def edit(document_id):
	if not get_user_from_session():
		abort(401)

	if request.method == "POST":
		sender = request.form['sender']
		body = request.form['body']
		db.messages.update_one({
				"_id": ObjectId(document_id) 
			}, {
				"$set": {
					"sender": sender,
					"body": body
				}
			}
		)

		return redirect('/')

	message = db.messages.find_one({
		"_id": ObjectId(document_id)
	})
	return render_template('edit.html', message=message)

def get_messages():
	return db.messages.find()

@app.route("/", methods=["GET", "POST"])
def home():
	if request.method == "POST":
		sender = request.form['sender']
		body = request.form['body']
		db.messages.insert({
			"sender": sender,
			"body": body
		})
	return render_template('home.html', messages=get_messages())


@app.route("/admin")
def admin():
	user = get_user_from_session()

	if not user:
		return "Forbidden."

	return render_template(
		"admin.html",
		messages=get_messages(),
		user=user,
	)

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form['email']
		password = request.form['password']

		password_encrypted = hashlib.sha256(password.encode('utf-8'))

		user = db.users.find_one({
			"email": email,
			"password": password_encrypted.hexdigest(),
			"is_admin": True,
		})

		if not user:
			return "Wrong email or password."

		session_id = str(uuid.uuid4())

		db.sessions.insert({
			"session_id": session_id,
			"user_id": user['_id']
		});

		response = make_response(render_template('login.html', success=True))
		response.set_cookie('session_id', session_id)
		return response
	return render_template('login.html')
