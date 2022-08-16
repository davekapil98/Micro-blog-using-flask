from flask import Flask
from flask import render_template, request, redirect
from login_form import LoginForm
from register_form import RegisterForm
# from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy
from config import Config

# Configure application
app = Flask(__name__)
app.config.from_object(Config)

# # Congigure the database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///microblog.db'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# # Initialize the database
# db = SQLAlchemy(app)

# # Create database model
# class users(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(200), nullable = False)
#     date_created = db.Column(db.DateTime, default = datetime.utcnow)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Default route
@app.route('/')
def index():
    return render_template("index.html")

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)
    
#Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    return render_template('register.html', title='Register', form=form)