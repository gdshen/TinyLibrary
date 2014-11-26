from wtforms import StringField, PasswordField, SubmitField
from flask_wtf import Form
from wtforms.validators import DataRequired

__author__ = 'gdshen95'


class LoginForm(Form):
    user = StringField('user', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('提交')




