from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=3)])
    content = TextAreaField("Content", validators=[DataRequired()])