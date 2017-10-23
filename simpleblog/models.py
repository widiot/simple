from . import db


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(), unique=True)
    password = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    avatar = db.Column(db.String(), unique=True)
    introduction = db.Column(db.text())
    register_date = db.Column(db.DateTime())
    categories = db.relationship(
            'Category',
            backref='user',
            lazy='dynamic',
            cascade='all,delete-orphan')
    posts = db.relaionship(
            'Post', backref='user', lazy='dynamic', cascade='all,delete-orphan')
    comments = db.relationship(
            'Comment', backref='user', lazy='dynamic', cascade='all,delete-orphan')
    favorites = db.relationship(
            'Favorite',
            foreign_keys=[Favorite.post_id],
            backref=db.backref('user', lazy='dynamic'),
            lazy='dynamic',
            cascade='all,delete-orphan')
    followers = db.relationship(
            'Follow',
            foreign_keys=[Follow.following_id],
            backref=db.backref('following', lazy='dynamic'),
            lazy='dynamic',
            cascade='all,delete-orphan')
    following = db.relationship(
            'Follow',
            foreign_keys=[Follow.follower_id],
            backref=db.backref('follower', lazy='dynamic'),
            lazy='dynamic',
            cascade='all,delete-orphan')


class Category(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))


class Favorite(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))


class Follow(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    follower_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    following_id = db.Column(db.Integer(), db.ForeignKey('user.id'))


class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    stars = db.Column(db.Integer())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'))
    comments = db.relationship(
            'Comment',
            backref='post',
            lazy='dynamic',
            cascade='all,delete-orphan')
    tags = db.relationship(
            'Tag',
            secondary=True,
            backref=db.backref('post', lazy='dynamic'),
            lazy='dynamic',
            cascade='all,delete-orphan')


class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())


tags = db.Table(
        'post_tags',
        db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')))


class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    stars = db.Column(db.Integer())
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
