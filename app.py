from flask import Flask, url_for
from flask import render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, EmailField, DateField, URLField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from flask_bcrypt import Bcrypt
from datetime import datetime
from config import Config

# Configurations & Initializations
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
    return User.query.get(int(user_id))
#===============================================================================================================================================================================================================

# Create database model
#===============================================================================================================================================================================================================
# Table to store user name and login credentials
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False, unique = True)
    name = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(80), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy = True)
    user_profile = db.relationship('User_Profile', backref='user_user', lazy = True)
    followers = db.relationship('Follow', backref='following', lazy = True)
        
    def __repr__(self):
        return f"User('{self.username}', '{self.name}', '{self.date_created}')"
    
# Table to store the posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(300), nullable = True)
    content_url = db.Column(db.String(), nullable = True)
    likes = db.Column(db.Integer, default = 0)
    dislikes = db.Column(db.Integer, default = 0)
    post_date = db.Column(db.DateTime, default = datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Post('{self.content}', '{self.content_url}', '{self.likes}', '{self.dislikes}', '{self.post_date}')"    

# Table to store profile information of users
class User_Profile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(300), nullable = True)
    profile_pic_url = db.Column(db.String(), nullable = True)
    email = db.Column(db.String(120), nullable=True)
    Birthdate = db.Column(db.Text, nullable = True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"User_Profile('{self.description}', '{self.profile_pic_url}', '{self.email}', '{self.Birthdate}', '{self.post_date}')"
    
# Table to track follower list and following list
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    follower_id = db.Column(db.Integer, nullable = False)
    users_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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
        existing_user_username = User.query.filter_by(
            username = username.data).first()        
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")
    
# Login Form
class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
# Add Post Form
class Add_PostForm(FlaskForm):
    content = StringField(validators=[Length(max=300)], render_kw={"placeholder": "What's happening?"})
    upload = URLField('Image URL', render_kw={"placeholder": "Image URL"})
    submit = SubmitField('Post')
    
# New User Profile Form
class MyProfileForm(FlaskForm):
    description = StringField(validators=[DataRequired()], render_kw={"placeholder": "How would you describe yourself?"})
    email = EmailField(validators=[DataRequired()], render_kw={"placeholder": 'Email'})
    birthdate = DateField (validators=[DataRequired()], render_kw={"placeholder": 'Birthdate'})
    submit = SubmitField("Update")
#===============================================================================================================================================================================================================

#All Routes
#===============================================================================================================================================================================================================
# Default route
@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    # Add new post
    form = Add_PostForm()
    if form.validate_on_submit():
        
        # Check if image is added or not
        if form.upload.data:
            url = form.upload.data
        else:
            url = None
         
        # Add the data of post to the database   
        add_post = Post(content = form.content.data, author_id = current_user.id, content_url = url)
        db.session.add(add_post)
        db.session.commit()
        return redirect(url_for('index'))
    
    # Get all posts from the database
    all_posts = Post.query.filter_by(author_id = current_user.id).all()
    
    # Sort the posts in LIFO order to see lastest posts on the top.
    new_posts = []
    for post in all_posts:
        new_posts.insert(0,post)
        
    return render_template('index.html', form=form, posts = new_posts)
    
#Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username = form.username.data, name = form.name.data, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))    
    return render_template('register.html', form=form)

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()    
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))            
    return render_template('login.html', form=form)

# Logout Route
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# New_Profile
@app.route("/my_profile", methods = ["GET", "POST"])
@login_required
def my_profile():
    form = MyProfileForm()
    if form.validate_on_submit():
        new_profile = User_Profile(description = form.description.data, email = form.email.data, Birthdate = form.birthdate.data, owner_id = current_user.id)
        db.session.add(new_profile)
        db.session.commit()
        return redirect(url_for('index'))    
    return render_template('myprofile.html', form=form)

@app.route("/explore", methods = ["GET", "POST"])
@login_required
def explore():
    form = Add_PostForm()
    posts = Post.query.all()
    # Sort the posts in LIFO order to see lastest posts on the top.
    new_posts = []
    for post in posts:
        new_posts.insert(0,post)
    
    return render_template('explore.html', form=form, posts = new_posts)
     
#===============================================================================================================================================================================================================

if __name__ == '__main__':
    app.run(debug=True)