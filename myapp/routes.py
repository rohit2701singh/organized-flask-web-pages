from flask import render_template, request, redirect, url_for, flash, abort
from myapp import app, bcrypt, db, login_manager
from myapp.models import User, Post
from myapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_login import login_user, current_user, logout_user, login_required
from myapp.data_file import matches_list    # dummy data file
from PIL import Image
import pandas as pd
import secrets
import os
import bleach


@app.route("/", methods=["GET", "POST"])
def home():
    match_data = matches_list
    if request.method == "POST":
        team_name = (request.form.get("team_name")).upper()
        venue_city_name = (request.form.get("venue_city_name")).title()
        data = pd.DataFrame(matches_list)

        if len(team_name) != 0 and len(venue_city_name) != 0:
            team_matches = data[(data["team 1"] == team_name) | (data["team 2"] == team_name)]
            selected_city_matches = team_matches[team_matches["venue city"] == venue_city_name]
            combined_match_df = pd.DataFrame(selected_city_matches)
            team_venue_match_list = combined_match_df.to_dict(orient="records")
            return render_template('index.html', full_data=team_venue_match_list)

        elif len(team_name) != 0:
            team_matches = data[(data["team 1"] == team_name) | (data["team 2"] == team_name)]
            match_df = pd.DataFrame(team_matches)
            team_match_list = match_df.to_dict(orient="records")
            return render_template('index.html', full_data=team_match_list)

        elif len(venue_city_name) != 0:
            city_matches = data[data["venue city"] == venue_city_name]
            city_df = pd.DataFrame(city_matches)
            city_matches_list = city_df.to_dict(orient="records")
            return render_template('index.html', full_data=city_matches_list)

    return render_template('index.html', full_data=match_data, title='home')


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    registration_form = RegistrationForm()

    if registration_form.validate_on_submit():
        username = registration_form.username.data
        email = registration_form.email.data
        password = registration_form.password.data
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash(f"Account created successfully for {username}! You can now login", category="success")
        return redirect(url_for('login'))

    return render_template('registration.html', form=registration_form, title='register')


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        remember_me = login_form.remember.data

        get_user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        # print(get_user_data)

        if get_user and bcrypt.check_password_hash(get_user.password, password):
            login_user(get_user, remember=remember_me)
            next_page = request.args.get('next')

            flash(f"successfully logged in user {get_user.username}!", category="success")
            return redirect(next_page or url_for('home'))
        else:
            flash("please enter the correct details", category="danger")

    return render_template('login.html', form=login_form, title='login')



def save_picture(form_picture):
    # print(form_picture)     # <FileStorage: 'wallll.jpeg' ('image/jpeg')>
    # print(type(form_picture))   # <class 'werkzeug.datastructures.FileStorage'>
    # print(form_picture.filename)    # wallll.jpeg

    random_hex = secrets.token_hex(nbytes=8)
    _, f_ext = os.path.splitext(form_picture.filename)  # splits pathname into a pair (root, extension) ex: desktop/file.py --> (desktop/file, .py)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    previous_img_path = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)

    if current_user.image_file != 'default.jpg' and os.path.isfile(previous_img_path):    # delete users old pic if exist
        os.remove(previous_img_path)

    # form_picture.save(picture_path)

    output_size = (160, 160)    # if you don't want large image then resize them
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_filename = save_picture(form.picture.data)
            current_user.image_file = picture_filename

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()

        flash(message="Your account has been updated!", category='success')
        return redirect(url_for('account'))
    
    elif request.method == 'GET':   # prefilled user details in form
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=f'profile_pics/{current_user.image_file}')

    return render_template('account.html', image_file=image_file, form=form, title='account')


@app.route('/remove_img', methods=['GET', 'POST'])
@login_required
def remove_profile_image():

    if current_user.image_file != 'default.jpg':
        
        previous_img_path = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)

        if os.path.isfile(previous_img_path):
            os.remove(previous_img_path)    # remove previous image then set it to default

        current_user.image_file = 'default.jpg'
        db.session.commit()

        flash('Your profile picture has been removed.', 'warning')
    else:
        flash("Can't remove. Image is already the default one.", 'warning')

    return redirect(url_for('account'))  # Redirect to the profile page or where necessary



@app.route("/logout")
def logout():
    if not current_user.is_authenticated:
        flash("You are already logged out!", category="warning")
        return redirect(url_for("login"))

    logout_user()
    flash("User logged out successfully", category="info")
    return redirect(url_for("home"))


@app.route("/all_post")
def all_posts():
    # posts = db.session.execute(db.select(Post).order_by(Post.id.desc())).scalars()
    # return render_template('all_posts.html', title='All Post', posts=posts, image_file=show_image_in_web())

    page = request.args.get('page', 1, type=int)  # page number from query params, default page=1
    per_page = 4  # Number of posts per page

    posts = db.paginate(db.select(Post).order_by(Post.date_posted.desc()), page=page, per_page=per_page, error_out=False)
    return render_template('all_posts.html', title='All Post', posts=posts)



# bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
# If you do not provide tags and attributes to bleach.clean(), then it uses safe default values internally
# tags not in this dict will be escaped or stripped from the text

allowed_tags = {
    'a', 'abbr', 'b', 'blockquote', 'code', 'em', 'i', 'li',
    'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'
}    

custom_attrs = {
    'a': ['href', 'title'],
    'code': ['class']
}

@app.route("/post/new" , methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():   # sanitize HTML input from user before saving it to the database 
        content_data = bleach.clean(form.content.data, tags=allowed_tags, attributes=custom_attrs) 

        post = Post(title=form.title.data, content=content_data, author=current_user)
        db.session.add(post)
        db.session.commit()

        flash(message="Your post has been created!", category='success')
        return redirect(url_for('all_posts'))
    return render_template('create_post.html', title='New Post', form=form, legend='Create New Post')


@app.route("/post/<int:post_id>")
def post_details(post_id):
    post = db.get_or_404(Post, post_id)

    return render_template('post.html', title=post.title, post=post)


@app.route("/user/<string:username>")
def user_posts(username):
    user = db.first_or_404(db.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    per_page = 2

    posts = db.paginate(
        db.select(Post).where(Post.author == user).order_by(Post.date_posted.desc()),
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template('user_posts.html', title='User Posts', user=user, posts=posts)



@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = db.get_or_404(Post, post_id)

    if post.author != current_user: 
        abort(403)
    
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = bleach.clean(form.content.data, tags=allowed_tags, attributes=custom_attrs)
        db.session.commit()
        flash(message="Your post has been updated!", category='success')
        return redirect(url_for('post_details', post_id=post.id))
    
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)

    if post.author != current_user: 
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash(message="Your post has been deleted", category="success")
    
    return redirect(url_for('all_posts'))
