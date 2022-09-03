from flask import Flask
from flask import render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, DateField, URLField, FileField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from wtforms.widgets import TextArea
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import uuid as uuid
from datetime import datetime
from config import Config

# Configurations & Initializations
#===============================================================================================================================================================================================================
# Configure application
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Config file
app.config.from_object(Config)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///microblog.db'

# Initialize the database
db = SQLAlchemy(app)

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
    all_following = db.relationship('Follow', backref='following', lazy = True)

    def __repr__(self):
        return f"User('{self.username}', '{self.name}', '{self.date_created}')"

# Table to store the posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(300), nullable = True)
    image_url = db.Column(db.String(), nullable = True)
    video_url = db.Column(db.String(), nullable = True)
    post_date = db.Column(db.DateTime, default = datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.content}', '{self.content_url}', '{self.likes}', '{self.dislikes}', '{self.post_date}')"

# Table to store profile information of users
class User_Profile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(300), nullable = True)
    profile_pic_url = db.Column(db.String(), nullable = True, default = 'default_profile.webp')
    email = db.Column(db.String(120), nullable=True)
    Birthdate = db.Column(db.DateTime, nullable = True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User_Profile('{self.description}', '{self.profile_pic_url}', '{self.email}', '{self.Birthdate}', '{self.post_date}')"

# Table to track following list and following list
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
    submit = SubmitField('Sign In')

# Change Password Form
class ChangePasswordForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username", "disabled": True})
    current_password = PasswordField(validators = [DataRequired(), Length(min=1, max=200)], render_kw={"placeholder": "Current Password"})
    new_password = PasswordField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder": "New Password"})
    confirm_new_password = PasswordField(validators=[DataRequired(), Length(min=4, max=20), EqualTo('new_password', message='Both password fields must be equal!')], render_kw={"placeholder": "Confirm New Password"})
    submit = SubmitField('Change Password')

# Add Post Form
class Add_PostForm(FlaskForm):
    content = StringField(validators=[Length(max=300)], render_kw={"placeholder": "What's happening?"}, widget=TextArea())
    image_url = URLField('Image URL', render_kw={"placeholder": "Image URL"})
    video_url = URLField('Video URL', render_kw={"placeholder": "Video URL"})
    submit = SubmitField('Post')

# New User Profile Form
class NewUserForm(FlaskForm):
    description = StringField("Description", validators=[DataRequired()], render_kw={"placeholder": "How would you describe yourself?"}, widget=TextArea())
    email = EmailField("Email Address", validators=[DataRequired()], render_kw={"placeholder": 'Email'})
    birthdate = DateField ("Birthdate", validators=[DataRequired()], render_kw={"placeholder": 'Birthdate'})
    submit = SubmitField("Update")
    
# My Profile Form
class MyProfileForm(FlaskForm):
    description = StringField("Description", validators=[DataRequired()], render_kw={"placeholder": "How would you describe yourself?", 'disabled': 'disabled'}, widget=TextArea())
    name = StringField("Name", validators = [DataRequired(), Length(min=1, max=200)], render_kw={"placeholder": "Name", 'disabled': 'disabled'})
    email = EmailField("Email Address", validators=[DataRequired()], render_kw={"placeholder": 'Email', 'disabled': 'disabled'})
    birthdate = DateField ("Birthdate", format='%Y-%m-%d', validators=[DataRequired()], render_kw={"placeholder": 'Birthdate', 'disabled': 'disabled'})
    profile_pic_file = FileField("Profile Pic")
    submit = SubmitField("Update")

# Follow & Unfollow Buttons
class FollowUnfollowForm(FlaskForm):
    follow = SubmitField("Follow")
    unfollow = SubmitField("Unfollow")
    
# Account Page Buttons
class Account(FlaskForm):
    change_password = SubmitField("Change Password")
    delete_account = SubmitField("Delete Account")
    
# Remove & Unfollow Buttons
class RemoveUnfollowForm(FlaskForm):
    remove = SubmitField("Remove")
    unfollow = SubmitField("Unfollow")
    user_id = StringField(validators=[DataRequired()])
#===============================================================================================================================================================================================================

#All Routes
#===============================================================================================================================================================================================================
# Default route
@app.route("/home", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    # Add new post
    form = Add_PostForm()
    user_profile_pic = (User_Profile.query.filter_by(owner_id = current_user.id).first()).profile_pic_url
    if form.validate_on_submit():

        # Check if image is added or not
        if form.image_url.data:
            image_url = form.image_url.data
        else:
            image_url = None
        
        # Check if video is added or not
        if form.video_url.data:
            video_url = form.video_url.data
        else:
            video_url = None

        # Add the data of post to the database
        add_post = Post(content = form.content.data, author_id = current_user.id, image_url = image_url, video_url = video_url)
        db.session.add(add_post)
        db.session.commit()
        return redirect(url_for('index'))

    # Get all posts from the database of both user and the other users they are following
    following_list = []
    all_followings = Follow.query.filter_by(users_id = current_user.id).all()
    for following in all_followings:
        following_list.append(following.follower_id)
    following_list.insert(0, current_user.id)
    all_posts = Post.query.filter(Post.author_id.in_(following_list)).all()

    # Sort the posts in LIFO order to see lastest posts on the top.
    new_posts = []
    for post in all_posts:
        new_post = {
            'id' : post.id,
            'content': post.content,
            'author_id': post.author_id,
            'image_url': post.image_url,
            'video_url': post.video_url,
            'author_name': post.author.name,
            'author_username': post.author.username,
            'profile_pic_url': (User_Profile.query.filter_by(owner_id = post.author_id).first()).profile_pic_url
        }
        new_posts.insert(0,new_post)

    return render_template('index.html', form=form, posts = new_posts, user_pic = user_profile_pic)

#Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_username = form.username.data
        new_user = User(username = new_username, name = form.name.data, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        new_created = User.query.filter_by(username = new_username).first()
        new_id = new_created.id
        session['messages'] = new_id
        return redirect(url_for('new_profile'))
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
            else:
                return render_template('login.html', form=form, password_error = "Incorrect password!!")
        else:
             return render_template('login.html', form=form, username_error = "Username does not exist!!")
    return render_template('login.html', form=form)

# Logout Route
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Change Password Route
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def changepassword():
    form = ChangePasswordForm()
    form.username.data = current_user.username
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.current_password.data):
                new_hashed_password = bcrypt.generate_password_hash(form.new_password.data)
                user.password = new_hashed_password
                db.session.commit()
                return redirect(url_for('index'))
    return render_template("changepassword.html", form=form)

# Explore Route
@app.route("/explore", methods = ["GET", "POST"])
@login_required
def explore():
    form = Add_PostForm()
    user_profile_pic = (User_Profile.query.filter_by(owner_id = current_user.id).first()).profile_pic_url
    posts = Post.query.all()
    # Sort the posts in LIFO order to see lastest posts on the top.
    new_posts = []
    for post in posts:
        new_post = {
            'id' : post.id,
            'content': post.content,
            'author_id': post.author_id,
            'image_url': post.image_url,
            'video_url': post.video_url,
            'author_name': post.author.name,
            'author_username': post.author.username,
            'profile_pic_url': (User_Profile.query.filter_by(owner_id = post.author_id).first()).profile_pic_url
        }
        new_posts.insert(0,new_post)

    return render_template('explore.html', form=form, posts = new_posts, user_pic = user_profile_pic)

# New_Profile. This is only for new users signing up
@app.route("/new_profile", methods = ["GET", "POST"])
def new_profile():
    try:
        id = session['messages']
    except KeyError:
 # Returns a 403.html whihch does not exist to indicate that this page cannot be accessed by directly changing the url
        return render_template('403.html')
    form = NewUserForm()
    id = session['messages']
    if form.validate_on_submit():
        new_profile = User_Profile(description=form.description.data, email=form.email.data, Birthdate=form.birthdate.data, owner_id=id)
        db.session.add(new_profile)
        db.session.commit()
        session.clear()
        return redirect(url_for('index'))
    return render_template('first_profile.html', form=form)

# My_Profile
@app.route("/my_profile", methods = ["GET", "POST"])
@login_required
def my_profile():
    profile = User_Profile.query.filter_by(owner_id = current_user.id).first()
    form = MyProfileForm(description = profile.description, birthdate = profile.Birthdate, name = profile.user_user.name, email = profile.email)
    
    if form.validate_on_submit():
        new_name = form.name.data
        profile.user_user.name = new_name
        profile.description = form.description.data
        profile.email = form.email.data
        profile.Birthdate = form.birthdate.data
        if form.profile_pic_file.data:
            filename = secure_filename(form.profile_pic_file.data.filename)
            new_filename = (str(uuid.uuid1()) + filename)
            form.profile_pic_file.data.save('static/images/uploads/' + new_filename)
            profile.profile_pic_url= new_filename
        try:
            db.session.commit()
        except:
            return redirect(url_for('index'))

    return render_template('my_profile.html', form=form, my_profile = profile, )

# View all other user's profiles
@app.route('/profile/<username>', methods = ["GET", "POST"])
@login_required
def user_profile(username):
    if username == current_user.username:
        return redirect(url_for('my_profile'))

    user_profile = User.query.filter_by(username = username).first()

    if not user_profile:
        return render_template("404.html")
    
    form = FollowUnfollowForm()
    follow_check = Follow.query.filter_by(users_id = current_user.id, follower_id = user_profile.id).first()
    following = False
    if follow_check:
        following = True
    if form.validate_on_submit():
        if form.follow.data:
            new_follow = Follow(users_id = current_user.id, follower_id = user_profile.id)
            db.session.add(new_follow)
            db.session.commit()
            return redirect(url_for('user_profile', username = username))
        else:
            unfollow = Follow.query.filter_by(users_id = current_user.id, follower_id = user_profile.id).first()
            db.session.delete(unfollow)
            db.session.commit()
            return redirect(url_for('user_profile', username = username))
    profile = User_Profile.query.filter_by(owner_id = user_profile.id).first()
    return render_template("users_profile.html", profile = profile, form = form, following = following)

# Account Settings
@app.route("/account", methods = ["GET", "POST"])
@login_required
def account():
    form = Account()
    profile = User_Profile.query.filter_by(owner_id = current_user.id).first()
    if form.validate_on_submit():
        if form.change_password.data:
            return redirect(url_for('changepassword'))
        elif form.delete_account.data:
            session['messages'] = current_user.id
            return redirect(url_for('deleteaccount'))
    
    return render_template("account.html", form=form, profile = profile)

# Follower List
@app.route ("/followers", methods = ["GET", "POST"])
@login_required
def followers():
    form = RemoveUnfollowForm()
    profile = User_Profile.query.filter_by(owner_id = current_user.id).first()
    followers = Follow.query.filter_by(follower_id = current_user.id).all()
    following = Follow.query.filter_by(users_id = current_user.id).all()
    follower_number = len(followers)
    following_number = len(following)
        
    all_followers_data = []
    
    for follow in followers:
        follow_info = {}
        user_info = (User.query.filter_by(id = follow.users_id).first())
        user_profile = User_Profile.query.filter_by(owner_id = follow.users_id).first()
        follow_info['id'] = user_info.id
        follow_info ['profile_pic_url'] = user_profile.profile_pic_url
        follow_info ['name'] = user_info.name
        follow_info['username'] = user_info.username
        all_followers_data.append(follow_info)
    
    if request.method == "POST" or form.validate_on_submit():
        username_id = form.user_id.data
        remove = Follow.query.filter_by(users_id = username_id, follower_id = current_user.id).first()
        db.session.delete(remove)
        db.session.commit()
        return redirect(url_for('followers'))
    
    return render_template("follower.html", form=form, profile = profile, followers = all_followers_data, follower_number = follower_number, following_number = following_number, users_name = current_user.name)

# Following List
@app.route ("/following", methods = ["GET", "POST"])
@login_required
def following():
    form = RemoveUnfollowForm()
    profile = User_Profile.query.filter_by(owner_id = current_user.id).first()
    followers = Follow.query.filter_by(follower_id = current_user.id).all()
    following = Follow.query.filter_by(users_id = current_user.id).all()
    follower_number = len(followers)
    following_number = len(following)
    all_following_data = []
    
    for follow in following:
        follow_info = {}
        user_info = (User.query.filter_by(id = follow.follower_id).first())
        user_profile = User_Profile.query.filter_by(owner_id = follow.follower_id).first()
        follow_info['id'] = user_info.id
        follow_info ['profile_pic_url'] = user_profile.profile_pic_url
        follow_info ['name'] = user_info.name
        follow_info['username'] = user_info.username
        all_following_data.append(follow_info)
        
    
    if request.method == "POST" or form.validate_on_submit():
        username_id = form.user_id.data
        unfollow = Follow.query.filter_by(users_id = current_user.id, follower_id = username_id).first()
        db.session.delete(unfollow)
        db.session.commit()
        return redirect(url_for('following'))     
    return render_template("following.html", form = form, profile = profile, following = all_following_data, follower_number = follower_number, following_number = following_number, users_name = current_user.name)

# Permenant Account Delete
@app.route ("/delete_account", methods = ["GET", "POST"])
@login_required
def deleteaccount():
        try:
            user_id = session['messages']
        except KeyError:
            # Returns a 403.html whihch does not exist to indicate that this page cannot be accessed by directly changing the url
            return render_template('403.html')
        
        user_info = User.query.filter_by(id = current_user.id).first()
        all_posts = Post.query.filter_by(author_id = current_user.id).all()
        following_users = Follow.query.filter_by(users_id = current_user.id).all()
        users_following = Follow.query.filter_by(follower_id = current_user.id).all()
        users_profile = User_Profile.query.filter_by(owner_id = current_user.id).first()
        db.session.delete(user_info)
        for post in all_posts:
            db.session.delete(post)
        for user in users_following:
            db.session.delete(user)
        for user in following_users:
            db.session.delete(user)
        db.session.delete(users_profile)
        db.session.commit()
        session.clear()
        return redirect(url_for('logout'))

#===============================================================================================================================================================================================================

if __name__ == '__main__':
    app.run(debug=True)