from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db, bcrypt, login_manager


# 博客标签表
class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))


# 博客关注表
class Star(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))


# 博客类别表
class Category(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))


# 博客表
class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    stars = db.Column(db.Integer())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'))
    comments = db.relationship(
        'Comment', backref='post', lazy='dynamic', cascade='all,delete-orphan')
    tags = db.relationship(
        'Tag',
        foreign_keys=[Tag.post_id],
        backref=db.backref('post', lazy='joined'),
        lazy='dynamic',
        cascade='all,delete-orphan')
    starer = db.relationship(
        'Star',
        foreign_keys=[Star.post_id],
        backref=db.backref('post', lazy='joined'),
        lazy='dynamic',
        cascade='all,delete-orphan')


# 评论
class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))


# 用户关注表
class Follow(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    follower_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    following_id = db.Column(db.Integer(), db.ForeignKey('user.id'))


# 用户表
# UserMixin可以提供Flask-Login要求实现的四个方法
class User(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(), unique=True)
    password_hash = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    avatar = db.Column(db.String())
    introduction = db.Column(db.Text())
    register_date = db.Column(db.DateTime())
    confirmed = db.Column(db.Boolean, default=False)  # 邮箱是否验证
    categories = db.relationship(
        'Category',
        backref='user',
        lazy='dynamic',
        cascade='all,delete-orphan')
    posts = db.relationship(
        'Post', backref='user', lazy='dynamic', cascade='all,delete-orphan')
    comments = db.relationship(
        'Comment', backref='user', lazy='dynamic', cascade='all,delete-orphan')
    staring = db.relationship(
        'Star',
        foreign_keys=[Star.user_id],
        backref=db.backref('user', lazy='joined'),
        lazy='dynamic',
        cascade='all,delete-orphan')
    followers = db.relationship(
        'Follow',
        foreign_keys=[Follow.following_id],
        backref=db.backref('following', lazy='joined'),
        lazy='dynamic',
        cascade='all,delete-orphan')
    following = db.relationship(
        'Follow',
        foreign_keys=[Follow.follower_id],
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',
        cascade='all,delete-orphan')

    # 将密码转为Hash值存储
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    # 检查明文密码的Hash值是否匹配
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # 生成验证令牌
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    # 验证令牌是否正确
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        return True


# Flask Login用user_loader获取用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
