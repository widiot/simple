from . import api


# 获取某个博客的评论
@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    pass
