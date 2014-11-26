# todo 功能完成 招募人员进行测试
# todo 管理员不能删除管理员
# 记住，有表格使用的使用方法一定要加上post
from flask import Flask, url_for, redirect, flash
from flask import render_template
from flask.ext.login import login_required, LoginManager, login_user, current_user, logout_user
import time
from database import *
from query import *
from login import *

app = Flask(__name__)
login_manager = LoginManager(app)
app.config['SECRET_KEY'] = 'This is a secret string'
CSRF_ENABLED = True


@app.route('/')
def hello_world():
    return render_template("index.html")

# login_required 应该要放在app.route下面才可以，其实还有admin_required可以使用
@app.route('/test')
@login_required
def test():
    return '你现在已经是登录的用户' + current_user.studentName


# 匿名用户查询
@app.route('/query', methods=['GET', 'POST'])
def query():
    form = BookQueryForm()
    if form.validate_on_submit():
        bar = Book.select().where(
            Book.bookName.contains(form.bookName.data) &
            Book.bookId.contains(form.bookId.data) &
            Book.author.contains(form.author.data) &
            Book.press.contains(form.press.data)
        )
        return render_template('query.html', form=form, bar=bar)
    return render_template('query.html', form=form)


# 普通用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = Student.get(Student.userName == form.user.data)
        if check_password_hash(u.password_hash, form.password.data):
            login_user(u)
            return redirect(url_for('user_index'))
        else:
            flash('用户名或者密码错误')
            return render_template("login.html", form=form)
    return render_template('login.html', form=form)


# 普通用户查询
@login_required
@app.route('/user/query', methods=['GET', 'POST'])
def user_query():
    form = BookQueryForm()
    if form.validate_on_submit():
        bar = Book.select().where(
            Book.bookName.contains(form.bookName.data) &
            Book.bookId.contains(form.bookId.data) &
            Book.author.contains(form.author.data) &
            Book.press.contains(form.press.data)
        )
        return render_template('user/query.html', form=form, bar=bar)
    return render_template('user/query.html', form=form)


# 普通用户借阅情况查询
@login_required
@app.route('/user/borrow')
def borrow_state():
    br = BorrowRelation.select().where(BorrowRelation.studentId == current_user.studentId)
    return render_template('user/borrow_state.html', br=br)


# 普通用户借阅书籍
# 一个用户多次借阅同一书号的书，可以根据书的实体不同而区分，在归还的时候也可以根据借阅而区分
@login_required
@app.route('/user/borrow/<book_Id>', methods=['GET', 'POST'])
def borrow_book(book_Id):
    # try:
    # BorrowRelation.get(BorrowRelation.studentId == current_user.studentId & BorrowRelation.bookId == book_Id)
    # flag = False
    # except BorrowRelation.DoesNotExist:
    bookname = (Book.get(Book.bookId == book_Id)).bookName
    BorrowRelation.create(studentId=current_user.studentId, bookName=bookname, bookId=book_Id, number=1)
    book = Book.get(Book.bookId == book_Id)
    book.remained -= 1
    book.save()
    t = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    Record.create(studentId=current_user.studentId, bookId=book_Id, operation='借', time=t)
    # flag = True
    return render_template('user/borrow_book.html', flag=True)


# 普通用户归还书籍
@login_required
@app.route('/user/return/<br_Id>', methods=['GET', 'POST'])
def return_book(br_Id):
    br = BorrowRelation.get(BorrowRelation.id == br_Id)
    t = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    Record.create(studentId=current_user.studentId, bookId=br.bookId, operation='还', time=t)
    book = Book.get(Book.bookId == br.bookId)
    book.remained += 1
    book.save()
    br.delete_instance()
    return render_template('user/return_book.html')


# 普通用户的个人信息
@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('user/profile.html')


# 普通用户首页

@app.route('/user/index')
@login_required
def user_index():
    return render_template('user/index.html')


# 普通用户退出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('hello_world'))


# 管理员用户登录
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        u = Student.get(Student.userName == form.user.data)
        if check_password_hash(u.password_hash, form.password.data) and u.admin == 1:
            login_user(u)
            return redirect(url_for('admin_index'))
        else:
            flash('用户名或者密码错误或者您不具有管理员权限')
            return render_template("login.html", form=form)
    return render_template('login.html', form=form)


# 管理员用户首页
@app.route('/admin/index')
@login_required
def admin_index():
    if current_user.admin == 1:
        return render_template('admin/index.html')
    else:
        flash('您不是管理员,请使用管理员用户登录')
        return redirect(url_for('admin_login'))


# 管理员淘汰采购图书
@app.route('/admin/query', methods=['GET', 'POST'])
@login_required
def admin_query():
    if current_user.admin == 1:
        form = BookQueryForm()
        if form.validate_on_submit():
            bar = Book.select().where(
                Book.bookName.contains(form.bookName.data) &
                Book.bookId.contains(form.bookId.data) &
                Book.author.contains(form.author.data) &
                Book.press.contains(form.press.data)
            )
            return render_template('admin/query.html', form=form, bar=bar)
        return render_template('admin/query.html', form=form)
    else:
        flash('您不是管理员,请使用管理员用户登录')
        return redirect(url_for('admin_login'))


# 管理员采购现有图书
@app.route('/admin/buy/<book_Id>', methods=['GET', 'POST'])
@login_required
def admin_buy(book_Id):
    if current_user.admin == 1:
        form = BookBuyForm()
        book = Book.get(Book.bookId == book_Id)
        if form.validate_on_submit():
            if form.bookId.data != book_Id:
                Book.create(bookName=form.bookName.data, bookId=form.bookId.data, author=form.author.data,
                            press=form.press.data, price=form.price.data, total=form.total.data, remained=form.total.data)
                flash('采购成功,请查询已验证')
                return redirect(url_for('admin_query'))
            book.total += form.total.data
            book.remained += form.total.data
            book.save()
            flash('采购成功,请查询已验证')
            return redirect(url_for('admin_query'))
        else:
            # flash('输入信息有误')
            return render_template('admin/buy.html', form=form, book=book)
    else:
        flash('您不是管理员,请使用管理员用户登录')
        return redirect(url_for('admin_login'))


# 管理员淘汰现有图书
@app.route('/admin/throw/<book_Id>')
@login_required
def admin_throw(book_Id):
    if current_user.admin == 1:
        book = Book.get(Book.bookId == book_Id)
        book.delete_instance()
        book.save()
        flash('淘汰成功')
        return redirect(url_for('admin_query'))
    else:
        flash('您不是管理员,请使用管理员用户登录')
        return redirect(url_for('admin_login'))


# 管理员查看最近借阅记录
@app.route('/admin/data')
@login_required
def admin_data():
    if current_user.admin == 1:
        bar = Record.select()
        return render_template('admin/borrow_data.html', bar=bar)
    else:
        flash('您不是管理员,请使用管理员用户登录')
        return redirect(url_for('admin_login'))


# 管理员对用户进行管理
@app.route('/admin/usermanager', methods=['GET', 'POST'])
@login_required
def admin_usermanager():
    if current_user.admin == 1:
        u = Student.select()
        return render_template('admin/usermanager.html', u=u)
    else:
        flash('您不是管理员,请使用管理员用户登录')
        return redirect(url_for('admin_login'))


# 管理员对用户进行删除
@app.route('/admin/userdelete/<studentid>', methods=['GET', 'POST'])
@login_required
def admin_userdelete(studentid):
    if current_user.admin == 1:
        stu = Student.get(Student.studentId == studentid)
        if stu.admin != 1:
            stu.delete_instance()
            stu.save()
            flash('用户删除成功')
        else:
            flash('不可以删除管理员')
        return redirect(url_for('admin_usermanager'))
    else:
        flash('您不是管理员,请使用管理员用户登录')
        return redirect(url_for('admin_login'))


# 管理员对用户进行添加
@app.route('/admin/useradd', methods=['GET', 'POST'])
@login_required
def admin_useradd():
    if current_user.admin == 1:
        form = UserAddForm()
        if form.validate_on_submit():
            password_gen = generate_password_hash(form.password.data)
            Student.create(studentName=form.studentName.data, studentId=form.studentId.data, college=form.college.data,
                           userName=form.userName.data, password_hash=password_gen, admin=0)
            # 对只能添加一个用户的问题已经处理，对让peewee自行创建database table，实现主键自增
            flash('用户添加成功')
            return redirect(url_for('admin_usermanager'))
        return render_template('admin/useradd.html', form=form)
    else:
        flash('您不是管理员,请使用管理员用户登录')
        return redirect(url_for('admin_login'))


#  这里有问题，对于Id只能是unicode的问题
@login_manager.user_loader
def load_user(userid):
    try:
        return Student.get(Student.id == userid)
    except Student.DoesNotExist:
        return None


if __name__ == '__main__':
    app.run(debug=True)
