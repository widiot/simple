from flask import (render_template, url_for, abort, flash, redirect,
                   current_app, request)
from flask_login import login_required, current_user
from datetime import datetime
from . import main
from .. import db
from .forms import PostForm, CommentForm
from ..decorators import permission_required, Permission
from ..models import User, Post, Follow, Comment


# 主页
@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['SIMPLE_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)


# 关注的人的博客
@main.route('/followed-posts')
@login_required
def followed_posts():
    pagination = current_user.followed_posts.order_by(
        Post.timestamp.desc()).paginate(
            page=request.args.get('page', 1, type=int),
            per_page=current_app.config['SIMPLE_PER_PAGE'],
            error_out=False)
    posts = pagination.items
    return render_template(
        'followed_posts.html', posts=posts, pagination=pagination)


# 博客固定页面，以及提交评论
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    # 查找博客
    post = Post.query.get_or_404(id)

    # 提交评论
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            timestamp=datetime.utcnow(),
            post=post,
            user=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('main.post', id=post.id, page=-1))

    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SIMPLE_PER_PAGE']

    # 如果page是-1，表明这是发表评论后的重定向，需要计算真实的page
    if page == -1:
        page = (post.comments.count() - 1) // per_page + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=per_page, error_out=False)
    comments = pagination.items
    return render_template(
        'post.html',
        post=post,
        form=form,
        comments=comments,
        pagination=pagination)


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
    # 查询user
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)

    # 每页显示的项目数
    per_page = current_app.config['SIMPLE_PER_PAGE']

    # 页面是固定的
    if option == 'blog':
        pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
            page, per_page=per_page, error_out=False)
        posts = pagination.items
        return render_template(
            'user.html',
            user=user,
            pagination=pagination,
            posts=posts,
            option=option)
    elif option in ['followers', 'followed']:
        if option == 'followers':
            pagination = user.followers.order_by(
                Follow.timestamp.desc()).paginate(
                    page, per_page=per_page, error_out=False)
            follows = [{
                'user': item.follower,
                'timestamp': item.timestamp
            } for item in pagination.items]
        else:
            pagination = user.followed.order_by(
                Follow.timestamp.desc()).paginate(
                    page, per_page=per_page, error_out=False)
            follows = [{
                'user': item.followed,
                'timestamp': item.timestamp
            } for item in pagination.items]
        return render_template(
            'user.html',
            user=user,
            pagination=pagination,
            follows=follows,
            option=option)
    else:
        abort(404)


# 关注用户
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    # 检查用户是否存在
    if user is None:
        flash('该用户不存在')
        return redirect(url_for('main.index'))

    # 检查是否已经关注该用户
    if current_user.is_following(user):
        flash('你已经关注该用户')
        return redirect(
            url_for('main.user', username=username, option='blog', page=1))

    # 关注该用户
    print('yes')
    current_user.follow(user)
    return redirect(
        url_for('main.user', username=username, option='blog', page=1))


# 取消关注
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    # 检查用户是否存在
    if user is None:
        flash('该用户不存在')
        return redirect(url_for('main.index'))

    # 检查是否已经关注该用户
    if not current_user.is_following(user):
        flash('你没有关注该用户')
        return redirect(
            url_for('main.user', username=username, option='blog', page=1))

    # 取消关注该用户
    current_user.unfollow(user)
    return redirect(
        url_for('main.user', username=username, option='blog', page=1))
