import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, flash, redirect, session, g
from flask import url_for
from functools import wraps
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

from forms import UserAddForm, UserUpdateForm, LoginForm, MessageForm, CsrfForm
from models import db, dbx, User, Message, Like, DEFAULT_HEADER_IMAGE_URL, DEFAULT_IMAGE_URL

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

db.init_app(app)



##############################################################################
# Before Requests

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = db.session.get(User, session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def add_csrf_to_g():
    """ Add csrf before a request. """

    g.csrf_form = CsrfForm()



##############################################################################
# Decorator wraps

# Source: https://flask.palletsprojects.com/en/2.3.x/patterns/viewdecorators/
def login_required(route_function):
    """ Validates that the g.user is logged in,
    redirects to homepage otherwise """
    @wraps(route_function)

    def decorated_route(*args, **kwargs):

        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect(url_for("homepage"))  # Redirect to home
        return route_function(*args, **kwargs)

    return decorated_route

def csrf_protected(route_function):
    """ Protects a route for CSRF """
    @wraps(route_function)

    def decorated_route(*args, **kwargs):
        form = g.csrf_form

        # CSRF check
        if form.validate_on_submit():
            # If valid, execute route function
            return route_function(*args, **kwargs)

        else:  # pragma: no cover
            # didn't pass CSRF; ignore logout attempt
            raise Unauthorized()

    return decorated_route


##############################################################################
# User signup/login/logout


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    do_logout()

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            db.session.rollback()
            return render_template('users/signup.jinja', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.jinja', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login and redirect to homepage on success."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            username=form.username.data,
            password=form.password.data,
        )

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.jinja', form=form)


@app.post('/logout')
@csrf_protected
def logout():
    """Handle logout of user and redirect to homepage."""

    do_logout()
    return redirect("/login")


##############################################################################
# General user routes:

@app.get('/users')
@login_required
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    #if not g.user:
    #    flash("Access unauthorized.", "danger")
    #    return redirect("/")

    search = request.args.get('q')

    if not search:
        q = db.select(User).order_by(User.id.desc())

    else:
        q = db.select(User).filter(User.username.like(f"%{search}%"))

    users = dbx(q).scalars().all()

    return render_template('users/index.jinja', users=users)


@app.get('/users/<int:user_id>')
@login_required
def show_user(user_id):
    """Show user profile."""

    #if not g.user:
    #    flash("Access unauthorized.", "danger")
    #    return redirect("/")

    user = db.get_or_404(User, user_id)

    return render_template('users/show.jinja', user=user)


@app.get('/users/<int:user_id>/following')
@login_required
def show_following(user_id):
    """Show list of people this user is following."""

    #if not g.user:
    #    flash("Access unauthorized.", "danger")
    #    return redirect("/")

    user = db.get_or_404(User, user_id)
    return render_template('users/following.jinja', user=user)


@app.get('/users/<int:user_id>/followers')
@login_required
def show_followers(user_id):
    """Show list of followers of this user."""

    #if not g.user:
    #    flash("Access unauthorized.", "danger")
    #    return redirect("/")

    user = db.get_or_404(User, user_id)
    return render_template('users/followers.jinja', user=user)


@app.post('/users/follow/<int:follow_id>')
@login_required
def start_following(follow_id):
    """Add a follow for the currently-logged-in user.

    Redirect to following page for the current for the current user.
    """

    #if not g.user:
    #    flash("Access unauthorized.", "danger")
    #    return redirect("/")

    followed_user = db.get_or_404(User, follow_id)

    g.user.follow(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.post('/users/stop-following/<int:follow_id>')
@login_required
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user.

    Redirect to following page for the current for the current user.
    """

    # if not g.user:
    #     flash("Access unauthorized.", "danger")
    #     return redirect("/")

    followed_user = db.get_or_404(User, follow_id)

    g.user.unfollow(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
@login_required
def profile_update():
    """Update profile for current user."""

    #if not g.user:
    #    flash("Access unauthorized.", "danger")
    #    return redirect("/")

    form = UserUpdateForm(obj=g.user)  # FIXME: move it under security check

    if form.validate_on_submit():

        is_auth = bool(User.authenticate(
            username=g.user.username,
            password=form.password.data
        ))

        if is_auth:

            try:
                # user = db.get_or_404(User, g.user.id)

                user = g.user

                user.email = form.email.data
                user.username = form.username.data
                user.image_url = form.image_url.data or DEFAULT_IMAGE_URL
                # FIXME: line break
                user.header_image_url = form.header_image_url.data or DEFAULT_HEADER_IMAGE_URL
                user.bio = form.bio.data
                user.location = form.location.data

                db.session.commit()
                flash("Edited your account successfully.", "success")
            except IntegrityError:
                flash("User email / username already taken", "danger")
                db.session.rollback()
                return render_template(
                    "/users/edit.jinja",
                    user=g.user,
                    form=form,
                )

            return redirect(f"/users/{g.user.id}")

        else:
            flash("Incorrect password, please try again", "danger")

    return render_template(
        "/users/edit.jinja",
        form=form,
    )


@app.post('/users/delete')
@login_required
def delete_user():
    """Delete user.

    Redirect to signup page.
    """

    #if not g.user:
    #    flash("Access unauthorized.", "danger")
    #    return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()
    flash("Account deleted", "danger")

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
@login_required
def add_message():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    #if not g.user:
    #    flash("Access unauthorized.", "danger")
    #    return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/create.jinja', form=form)


@app.get('/messages/<int:message_id>')
@login_required
def show_message(message_id):
    """Show a message."""

    #if not g.user:
    #    flash("Access unauthorized.", "danger")
    #    return redirect("/")

    msg = db.get_or_404(Message, message_id)
    return render_template('messages/show.jinja', message=msg)


@app.post('/messages/<int:message_id>/delete')
@login_required
def delete_message(message_id):
    """Delete a message.

    Check that this message was written by the current user.
    Redirect to user page on success.
    """

    #if not g.user:
    #    flash("Access unauthorized.", "danger")
    #    return redirect("/")

    msg = db.get_or_404(Message, message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


##############################################################################
# Likes

@app.post('/messages/like/<int:message_id>')
@login_required
@csrf_protected
def toggle_like(message_id):
    """ Will call is_liked method from the User model. Depending on
    the output, will either call the liked or the unlike method and then
    render the appropriate jinja
    """

    #form = CsrfForm()

    #if not g.user or not form.validate_on_submit():
    #    flash("Access unauthorized.", "danger")
    #    return redirect("/")

    redirection_url = request.form.get(
        "came_from", "/")

    # Will return true if the message is liked; false otherwise
    if not g.user.is_liked(message_id):

        g.user.like(message_id=message_id)

        db.session.commit()
        return redirect(redirection_url)

    else:
        g.user.unlike(message_id)
        db.session.commit()

        return redirect(redirection_url)


@app.get('/users/<int:user_id>/likes')
@login_required
def show_likes(user_id):
    """ Show all liked messages from user """

    user = db.get_or_404(User, user_id)

    liked_message_ids = [
        liked_msgs.id for liked_msgs in user.likes]
    # Add current user to the liked message list

    q = (
        db.select(Message)
        .where(Message.id.in_(liked_message_ids))
        .order_by(Message.timestamp.desc())
    )
    liked_msgs = dbx(q).scalars().all()

    return render_template(
        'users/likes.jinja',
        messages=liked_msgs,
        user=user,
    )


##############################################################################
# Homepage and error pages


@app.get('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of self & followed_users
    """

    if g.user:

        followers = [
            follower.id for follower in g.user.following]

        # Add current user to the followers list
        followers.append(g.user.id)

        q = (
            db.select(Message)
            .where(Message.user_id.in_(followers))
            .order_by(Message.timestamp.desc())
            .limit(100)
        )

        messages = dbx(q).scalars().all()

        return render_template('home.jinja', messages=messages)

    else:
        return render_template('home-anon.jinja')


@app.after_request
def add_header(response):
    """Add non-caching headers on every request."""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True

    return response


@app.errorhandler(404)
def page_not_found(e):
    """ Render the 404 page """
    return (render_template('error_404.jinja'), 404)
