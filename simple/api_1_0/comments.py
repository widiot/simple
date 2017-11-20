from flask import request, current_app, url_for, jsonify, g
from . import api
from .. import db
from ..models import Post, Comment


# 获取分页评论
@api.route('/comments/')
def get_comments():
    # 获取当前页
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['SIMPLE_PER_PAGE'], error_out=False)
    comments = pagination.items

    # 获取上一页和下一页
    prev = None
    next = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page - 1)
    if pagination.has_next:
        next = url_for('api.get_comments', page=page + 1)

    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


# 获取单个评论
@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


# 获取某个博客的分页评论
@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    # 获取评论
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['SIMPLE_PER_PAGE'], error_out=False)
    comments = pagination.items

    # 获取上一页和下一页
    prev = None
    next = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', id=id, page=page - 1)
    if pagination.has_next:
        next = url_for('api.get_post_comments', id=id, page=page + 1)

    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


# 发表评论
@api.route('/posts/<int:id>/comments/', methods=['POST'])
def new_post_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.user = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify({comment.to_json()}), 201, {
        'location': url_for('api.get_comment', id=comment.id)
    }
