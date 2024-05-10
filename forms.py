from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, URL, Optional, ValidationError

from models import User


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[InputRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField(
        'Username',
        validators=[InputRequired(), Length(max=30)],
    )

    email = StringField(
        'E-mail',
        validators=[InputRequired(), Email(), Length(max=50)],
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=6, max=50)],
    )

    image_url = StringField(
        '(Optional) Image URL',
        validators=[Optional(), URL(), Length(max=255)]
    )

    def validate_username(self, username_field):
        """ Validation to check if username is already taken. """

        if User.is_username_taken(username_field.data):
            raise ValidationError('Username is already taken.')

    def validate_email(self, email_field):
        """ Validation to check if email is already taken. """

        if User.is_email_taken(email_field.data):
            raise ValidationError('Email is already registered.')


class UserUpdateForm(FlaskForm):
    """Form for updating user details."""

    username = StringField(
        'Username',
        # TODO: check if username is taken by a different user id
        validators=[Optional(), Length(max=30)],
    )

    email = StringField(
        'E-mail',
        # TODO: check back in on the EmailField vs. StringField
        validators=[Optional(), Email(), Length(max=50)],
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=6, max=50)],
    )

    image_url = StringField(
        '(Optional) Image URL',
        validators=[Optional(), URL(), Length(max=255)]
    )

    location = StringField(
        '(Optional) Location',
        validators=[Optional(), Length(max=30)]
    )

    bio = TextAreaField(
        '(Optional) Bio',
        validators=[Optional()]
    )

    header_image_url = StringField(
        '(Optional) Header Image URL',
        validators=[Optional(), URL()]
    )


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        'Username',
        validators=[InputRequired(), Length(max=30)],
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=6, max=50)],
    )


class CsrfForm(FlaskForm):
    """ form for CSRF protection"""
