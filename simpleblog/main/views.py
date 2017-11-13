from flask import (render_template, url_for, abort, flash, redirect,
                   current_app, request)
from flask_login import login_required, current_user
from datetime import datetime
from . import main
from .. import db
from .forms import PostForm
from ..models import User, Post


# 主页
@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['SIMPLE_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)


# 博客固定页面
@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)


# 写博客
@main.route('/editor-post')
@login_required
def editor_post():
    form = PostForm()
    return render_template('edit_post.html', form=form, published=None)


# 发表博客
@main.route('/publish-post', methods=['GET', 'POST'])
@login_required
def publish_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            body=form.body.data,
            published=True,
            timestamp=datetime.utcnow(),
            user=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash('博客发表成功')
        return redirect(url_for('main.post', id=post.id))
    else:
        flash('博客发表失败')
    return render_template('edit_post.html', form=form, published=False)


# 更新博客
@main.route('/update-post/<int:id>', methods=['GET', 'POST'])
@login_required
def update_post(id):
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
        flash('文章更新成功')
        return redirect(url_for('main.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template(
        'edit_post.html', form=form, published=post.published)


# 用户资料页面
@main.route('/user/<username>/<option>/<int:page>')
def user(username, option, page):
    # 页面只能是options中的
    options = ['blog', 'latest', 'hot', 'following', 'followed']
    if option not in options:
        abort(404)

    # 查询user
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)

    per_page = current_app.config['SIMPLE_PER_PAGE']
    # blog
    if option == options[0]:
        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=per_page, error_out=False)
        posts = pagination.items
    return render_template(
        'user.html', user=user, pagination=pagination, posts=posts)
