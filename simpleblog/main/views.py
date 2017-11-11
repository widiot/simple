from flask import render_template, url_for, abort, flash, redirect
from flask_login import login_required, current_user
from . import main
from .. import db
from .forms import PostForm
from ..models import User, Post


# 主页
@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# 博客固定页面
@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)


# 写博客
@main.route('/edit')
@login_required
def edit_new():
    form = PostForm()
    return render_template('edit_post.html', form=form, published=False)


# 发表博客
@main.route('/publish', methods=['GET', 'POST'])
@login_required
def publish():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, published=True)
        db.session.add(post)
        db.session.commit()
        flash('博客发表成功')
        return redirect(url_for('main.post', id=post.id))
    else:
        flash('博客发表失败')
    return render_template('edit_post.html', form=form, published=False)


# 更新博客
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_update(id):
    post = Post.query.get_or_404(id)
    # 如果不是作者，并且不是管理员，则返回403
    if current_user != post.user and not current_user.is_administrator():
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('文章已更新')
        return redirect(url_for('main.post', id=post.id))
    form.body.data = post.body
    return render_template(
        'edit_post.html', form=form, published=post.published)


# 用户资料页面
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    return render_template('user.html', user=user)
