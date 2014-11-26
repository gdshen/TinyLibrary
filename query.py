from flask_wtf import Form  # 注意这里是从flask_wtf里面import Form类而不是从wtforms里面
from wtforms import StringField, SubmitField, IntegerField, PasswordField
from wtforms.validators import DataRequired


class BookQueryForm(Form):
    bookId = StringField('BookId')
    bookName = StringField('BookName')  # , validators=[DataRequired()])
    author = StringField('Author')
    press = StringField('Press')
    submit = SubmitField('Submit')


class BookBuyForm(Form):
    bookName = StringField('请输入图书名')
    bookId = StringField('请输入图书SN号')
    author = StringField('请输入图书作者')
    press = StringField('请输入输入出版社')
    price = StringField('请输入图书价格')
    total = IntegerField('请输入图书新增数量', validators=[DataRequired()])
    submit = SubmitField('提交')


class UserAddForm(Form):
    studentName = StringField()
    studentId = StringField()
    college = StringField()
    userName = StringField()
    password = PasswordField()
    submit = SubmitField('提交')