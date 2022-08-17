from flask import Flask, url_for
from flask import render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from flask_bcrypt import Bcrypt
from datetime import datetime
from config import Config

#Configurations & Initializations
#===============================================================================================================================================================================================================
# Configure application
app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)

# Initialize the database
db = SQLAlchemy(app)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///microblog.db'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Initialize Flask_login Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))
#===============================================================================================================================================================================================================

# Create database model
#===============================================================================================================================================================================================================
# Table to store user name and login credentials
class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False, unique = True)
    name = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(80), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    
# Table to store the posts
class posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(300), nullable = True)
    content_url = db.Column(db.String(), nullable = True)
    likes = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)
    post_date = db.Column(db.DateTime, default = datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    

# Table to store profile information of users
class user_profile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(300), nullable = True)
    profile_pic_url = db.Column(db.String(), nullable = True)
    email = db.Column(db.String(120), nullable=False)
    Birthdate = db.Column(db.Text, nullable = True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
# Table to track follower list and following list
class followers(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    follower_id = db.Column(db.Integer, nullable = False)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#=============================================================================================================================================================================================================== 

# Ensure that respones are not cached
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#All Forms
#===============================================================================================================================================================================================================
# Register form
class RegisterForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    name = StringField(validators = [DataRequired(), Length(min=1, max=200)], render_kw={"placeholder": "Name"})
    password = PasswordField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    confirmpassword = PasswordField(validators=[DataRequired(), Length(min=4, max=20), EqualTo('password', message='Both password fields must be equal!')], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Register')    
    # Validate to see if the username is unique
    def validate_username(self, username):
        existing_user_username = users.query.filter_by(
            username = username.data).first()        
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")
    
# Login Form
class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
#===============================================================================================================================================================================================================

#All Routes
#===============================================================================================================================================================================================================
# Default route
@app.route('/')
@login_required
def home():
    return render_template("index.html")
    
#Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = users(username = form.username.data, name = form.name.data, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))    
    return render_template('register.html', form=form)

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()    
    if form.validate_on_submit():
        user = users.query.filter_by(username = form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))            
    return render_template('login.html', form=form)

# Logout Route
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
#===============================================================================================================================================================================================================

if __name__ == '__main__':
    app.run(debug=True)