from dataclasses import dataclass
from datetime import datetime
from boardgameforum import db, login_manager
from flask_login import UserMixin
from sqlalchemy.orm import relationship


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@dataclass
class User(db.Model, UserMixin):
    id: int
    username: str
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    sales = db.relationship('Sale', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


@dataclass  # using dataclass you don't need to have the serialize function
class Post(db.Model):
    # but you need to identify the types of the fields
    id: int
    title: str
    content: str
    tag: str
    user: User

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = relationship(User)
    # loading comments in the reverse order of date_posted
    comments = db.relationship('Comment', backref='comm', lazy=True, order_by='desc(Comment.date_posted)')

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', '{self.tag}')"

    # but with the serialize() allows you to get information from relationships
    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'tag': self.tag,
            'content': self.content,
            'user': self.user_id,
            'username': self.user.username
        }


@dataclass  # using dataclass you don't need to have the serialize function
class Sale(db.Model):
    # but you need to identify the types of the fields
    id: int
    title: str
    content: str
    price: str
    is_active: bool
    image_file: str
    user: User

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image_file = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, unique=False, default=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    def __repr__(self):
        return f"Post('{self.title}', '{self.price}', '{self.date_posted}')"

    # but with the serialize() allows you to get information from relationships
    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'image_file': self.image_file,
            'is_active': self.is_active,
            'content': self.content,
            'user': self.user_id,
            'username': self.user.username
        }


@dataclass
class Comment(db.Model):
    id: int
    content: str
    user: User

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = relationship(User)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = relationship(Post)


@dataclass
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_expired = db.Column(db.DateTime, nullable=False)
    token = db.Column(db.String(60), nullable=False, index=True)  # index helps searching


db.create_all()
