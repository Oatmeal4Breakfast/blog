from flask_wtf import FlaskForm
from wtforms import Label, StringField, SubmitField, PasswordField, validators
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField
from dataclasses import dataclass


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@dataclass
class RegisterUserData:
    email: str
    name: str
    password: str


class RegisterForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    name = StringField(label="Name", validators=[DataRequired()])
    submit = SubmitField(label="Register")

    def get_data(self) -> RegisterUserData:
        return RegisterUserData(
            email=str(self.email.data),
            name=str(self.name.data),
            password=str(self.password.data),
        )


@dataclass
class LoginData:
    email: str
    password: str


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Login")

    def get_data(self) -> LoginData:
        return LoginData(email=str(self.email.data), password=str(self.password.data))


@dataclass
class CommentData:
    comment: str


class CommentForm(FlaskForm):
    comment = CKEditorField(label="Comment", validators=[DataRequired()])
    submit = SubmitField(label="Post")

    def get_data(self) -> CommentData:
        return CommentData(comment=self.comment.data)
