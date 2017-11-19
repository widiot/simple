from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Post


# 获取某个用户
@api.route('/user/<int:id>')
def get_user(id):
    return User.query.get_or_404(id)


# 获取某个用户的分页文章
@api.route('/user/<int:id>/posts/')
def get_user_posts(id):
    # 获取用户和分页文章
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['SIMPLE_PER_PAGE'], error_out=False)
    posts = pagination.items

    # 设置前一页和后一页的URL
    prev = None
    next = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', id=id, page=page - 1)
    if pagination.has_next:
        next = url_for('api.get_user_posts', id=id, page=page + 1)

    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


# 获取用户关注的人的博客
@api.route('/user/<int:id>/timeline/')
def get_user_followed_posts(id):
    # 获取用户和分页文章
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['SIMPLE_PER_PAGE'], error_out=False)
    posts = pagination.items

    # 设置前一页和后一页的URL
    prev = None
    next = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', id=id, page=page - 1)
    if pagination.has_next:
        next = url_for('api.get_user_posts', id=id, page=page + 1)

    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
