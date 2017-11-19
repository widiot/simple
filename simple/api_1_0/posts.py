from flask import request, g, jsonify, current_app, url_for
from . import api
from .errors import forbidden
from .decorators import permission_required
from .. import db
from ..models import Post, Permission


# 发表文章
@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.user = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {
        'location': url_for('api.get_posts', id=post.id)
    }


# 更新博客
@api.route('/posts/<ind:id>', methods=['PUT'])
def update_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.user and not g.current_user.can(
            Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.title = request.json.get('title', post.title)
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())


# 获取分页文章
@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['SIMPLE_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    next = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page - 1, _external=True)
    if pagination.has_next:
        next = url_for('api.get_posts', page=page + 1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


# 获得一篇文章
@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())
