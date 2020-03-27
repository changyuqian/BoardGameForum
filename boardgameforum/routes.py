import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from boardgameforum import app, db, bcrypt
from boardgameforum.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CommentForm, SaleForm
from boardgameforum.models import User, Post, Comment, Sale
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc


@app.route("/")
@app.route("/home")
def home():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file) \
        if current_user.is_authenticated else ""
    posts = Post.query.order_by(desc(Post.date_posted)).all()
    tags = set([ele.tag for ele in posts])
    hot_posts = sorted(posts, key=lambda x: len(x.comments), reverse=True)
    sales = Sale.query.order_by(desc(Sale.date_posted)).all()
    return render_template('index.html', posts=posts, image_file=image_file, hot_posts=hot_posts, sales=sales, tags=tags)


@app.route("/about")
def about():
    tags = [ele.tag for ele in Post.query.order_by(desc(Post.date_posted)).all()]
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file) \
        if current_user.is_authenticated else ""
    return render_template('about.html', title='About', image_file=image_file, tags=tags)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    tags = [ele.tag for ele in Post.query.order_by(desc(Post.date_posted)).all()]
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form, tags=tags)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file) \
        if current_user.is_authenticated else ""
    tags = [ele.tag for ele in Post.query.order_by(desc(Post.date_posted)).all()]
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, tag=form.tag.data, content=form.content.data, user=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', legend='Initiate Discussion', form=form,
                           image_file=image_file, tags=tags)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file) \
        if current_user.is_authenticated else ""
    tags = [ele.tag for ele in Post.query.order_by(desc(Post.date_posted)).all()]
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.tag.data = post.tag
        form.content.data = post.content
    return render_template('create_post.html', image_file=image_file, title='Update Post', form=form,
                           legend='Update Post', tags=tags)


@app.route("/post/<int:post_id>/delete", methods=['GET'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):

    tags = [ele.tag for ele in Post.query.order_by(desc(Post.date_posted)).all()]
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file) \
        if current_user.is_authenticated else ""
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated: # you can only comment if you're logged in
            comment = Comment(content=form.content.data, user=current_user, post=post)
            db.session.add(comment)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(f'/post/{post.id}')
        else:
            flash('You are not logged in. You need to be logged in to be able to comment!', 'danger')
    return render_template('post.html', image_file=image_file, title="post", post=post, form=form, tags=tags)


def save_item_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/item_pics', picture_fn)
    output_size = (400, 400)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/sale/new", methods=['GET', 'POST'])
@login_required
def new_sale():

    tags = [ele.tag for ele in Post.query.order_by(desc(Post.date_posted)).all()]
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file) \
        if current_user.is_authenticated else ""
    form = SaleForm()
    if form.validate_on_submit():
        if form.picture.data:
            image_file = save_item_picture(form.picture.data)
        sale = Sale(title=form.title.data, price=form.price.data, image_file=image_file, content=form.content.data, user=current_user)
        db.session.add(sale)
        db.session.commit()
        flash('Your sale has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_sale.html', title='New Sale', legend='Item to sell', form=form, image_file=image_file, tags=tags)


@app.route("/sale/<int:sale_id>", methods=['GET', 'POST'])
def sale(sale_id):

    tags = [ele.tag for ele in Post.query.order_by(desc(Post.date_posted)).all()]
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file) \
        if current_user.is_authenticated else ""
    sale = Sale.query.get_or_404(sale_id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:  # you can only comment if you're logged in
            comment = Comment(content=form.content.data, user=current_user, sale=sale)
            db.session.add(comment)
            db.session.commit()
            flash('Your sale has been created!', 'success')
            return redirect(f'/sale/{sale.id}')
        else:
            flash('You are not logged in. You need to be logged in to be able to sell!', 'danger')
    return render_template('sale.html', image_file=image_file, title="sale", sale=sale, form=form, tags=tags)


@app.route("/sale/<int:sale_id>/sold", methods=['GET'])
@login_required
def sold(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    sale.is_active = False
    if sale.author != current_user:
        abort(403)
    db.session.commit()
    return redirect(url_for('home'))
