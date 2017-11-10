import hashlib
from flask import current_app, request
from flask_login import AnonymousUserMixin, UserMixin
from datetime import datetime
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


# 用户权限
class Permission:
    FOLLOW = 0x01  # 关注用户
    COMMENT = 0x02  # 评论
    WRITE_ARTICLES = 0x04  # 写文章
    MODERATE_COMMENTS = 0x08  # 删除评论
    ADMINISTER = 0x80  # 管理员


# 用户角色
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean(), default=False, index=True)
    permissions = db.Column(db.Integer())
    users = db.relationship('User', backref='role', lazy='dynamic')

    # 当数据库没有roles中的角色时，就创建该角色
    @staticmethod
    def insert_roles():
        # 默认用户、管理员
        roles = {
            'User':
                (Permission.FOLLOW | Permission.COMMENT
                 | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS, True),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if not role:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


# 用户表
# 继承UserMixin可以提供Flask-Login要求实现的四个方法，不过调用的时候好像不是方法，是bool属性
class User(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String())
    email = db.Column(db.String(64), unique=True)
    avatar = db.Column(db.String())  # 用户自定义的头像
    gravatar_hash = db.Column(db.String(32))  # gravatar的头像Hash值
    introduction = db.Column(db.Text())
    register_date = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)  # 邮箱是否验证
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))
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

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # 如果email是管理员，则赋予管理员权限，否则赋予默认权限
        if not self.role:
            if self.email == current_app.config['SIMPLE_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if not self.role:
                self.role = Role.query.filter_by(default=True).first()

        # 设置gravatar的头像
        if self.email and not self.gravatar_hash:
            self.gravatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    # 将明文密码转为Hash值存储
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    # 检查明文密码的Hash值是否匹配
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # 生成gravatar的头像
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.gravatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,
                                                                     hash=hash,
                                                                     size=size,
                                                                     default=default,
                                                                     rating=rating)

    # 检查权限
    def can(self, permissions):
        return self.role is not None and (
                                             self.role.permissions & permissions) == permissions

    # 是否是管理员
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    # 生成注册验证令牌
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    # 验证注册令牌是否正确
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

    # 生成重置密码的令牌
    def generate_reset_password_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    # 重置密码
    def reset_password(self, token, password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.set_password(password)
        db.session().add(self)
        db.session().commit()
        return True

    # 生成修改邮箱的令牌
    def generate_change_email_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    # 修改邮箱
    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('change_email') != self.id:
            return False

        new_email = data.get('new_email')
        if not new_email:
            return False
        if User.query.filter_by(email=new_email).first():
            return False
        self.email = new_email
        self.gravatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()
        return True

    # 刷新用户登录时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()


# 匿名用户
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


# Flask Login用user_loader获取用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
