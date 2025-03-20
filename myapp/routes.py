from flask import render_template, request, redirect, url_for, flash
from myapp import app, bcrypt, db, login_manager
from myapp.models import User
from myapp.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required
from myapp.data_file import matches_list    # dummy data file
from PIL import Image
import pandas as pd
import secrets
import os


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

    return render_template('index.html', full_data=match_data)


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

    return render_template('registration.html', form=registration_form)


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

    return render_template('login.html', form=login_form)



def save_picture(form_picture):
    random_hex = secrets.token_hex(nbytes=8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
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
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        
    
    image_file = url_for('static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html', image_file=image_file, form=form)


@app.route("/logout")
def logout():
    if not current_user.is_authenticated:
        flash("You are already logged out!", category="warning")
        return redirect(url_for("login"))

    logout_user()
    flash("User logged out successfully", category="info")
    return redirect(url_for("home"))
