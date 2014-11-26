# 数据库的库对象类的建立与连接

from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import peewee as pw

myDB = pw.MySQLDatabase('library', host='localhost', port=3306, user='root', passwd='asdjkl')


class MySQLModel(pw.Model):
    """A base model that will use our MySQL database"""

    class Meta:
        database = myDB


class Book(MySQLModel):
    bookName = pw.CharField(100)
    bookId = pw.CharField(100,primary_key=True)
    author = pw.CharField(100)
    press = pw.CharField(100)
    price = pw.IntegerField()
    total = pw.IntegerField()
    remained = pw.IntegerField()

    class Meta:
        db_table = 'book'


class Student(UserMixin, MySQLModel):
    # id = pw.CharField(20, primary_key=True) 把ID注释掉让peewee自动生成可以自增的主键
    studentName = pw.CharField(100)
    studentId = pw.CharField()
    college = pw.CharField(100)
    userName = pw.CharField(100)
    password_hash = pw.CharField(100)
    admin = pw.BooleanField()

    def password(self, passwd):
        self.password_hash = generate_password_hash(passwd)

    def password_verify(self, passwd):
        return check_password_hash(self.password_hash, passwd)

    class Meta:
        db_table = 'student'


class BorrowRelation(MySQLModel):
    studentId = pw.CharField(100)
    bookName = pw.CharField(100)
    bookId = pw.CharField(100)
    number = pw.IntegerField()
    # id = pw.IntegerField(primary_key=True)

    class Meta:
        db_table = 'borrowrelation'


class Record(MySQLModel):
    studentId = pw.CharField(100)
    bookId = pw.CharField(100)
    operation = pw.CharField(100)
    time = pw.CharField(100)

    class Meta:
        db_table = 'record'


myDB.connect()
myDB.create_tables([BorrowRelation, Record, Student], safe=True)
