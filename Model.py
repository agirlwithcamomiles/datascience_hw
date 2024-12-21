from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from flask import Flask

db = SQLAlchemy()

app = Flask(__name__, template_folder='C:/Users/vikto/PycharmProjects/programming_year2/programming_hw3/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rshu_crowled.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.app = app
db.init_app(app)


class Author(db.Model):

    __tablename__ = "authors"

    author_id = db.Column('author_id', db.Integer, db.Sequence('author_id_seq'), primary_key=True)
    name = db.Column('author_name', db.Text, )


class Meta(db.Model):
    __tablename__ = "news_meta"
    __table_args__ = {'extend_existing': True}

    news_id = db.Column('news_id', db.Integer, db.Sequence('news_id_seq'), primary_key=True)
    title = db.Column('title', db.Text)
    date = db.Column('date', db.Text)
    author_text = db.Column('author_text', db.Integer, ForeignKey('authors.author_id'))
    author_photo = db.Column('author_photo', db.Integer, ForeignKey('authors.author_id'))


class Categories(db.Model):

    __tablename__ = "categories"
    __table_args__ = (PrimaryKeyConstraint('category_id'),)

    category_id = db.Column('category_id', db.Integer)
    category_name = db.Column('category_name', db.Text)


class News_categories(db.Model):

    __tablename__ = "news_categories"
    __table_args__ = (PrimaryKeyConstraint('news_id', 'category_id'),)

    news_id = db.Column('news_id', db.Integer, ForeignKey('news_meta.news_id'))
    category_id = db.Column('category_id', db.Integer, ForeignKey('categories.category_id'))


class Links(db.Model):

    __tablename__ = "news_links"
    __table_args__ = (PrimaryKeyConstraint('news_id'),)

    news_id = db.Column('news_id', db.Integer, ForeignKey('news_meta.news_id'))
    news_links = db.Column('news_links', db.Text)


class Images(db.Model):

    __tablename__ = "news_images"
    __table_args__ = (PrimaryKeyConstraint('news_id'),)

    news_id = db.Column('news_id', db.Integer, ForeignKey('news_meta.news_id'))
    news_images = db.Column('news_images', db.Text)


class Short_text(db.Model):

    __tablename__ = "news_shorttext"
    __table_args__ = (PrimaryKeyConstraint('news_id'),)

    news_id = db.Column('news_id', db.Integer, ForeignKey('news_meta.news_id'))
    news_shorttext = db.Column('news_shorttext', db.Text)


class Full_text(db.Model):

    __tablename__ = "news_fulltext"
    __table_args__ = (PrimaryKeyConstraint('news_id'),)

    news_id = db.Column('news_id', db.Integer, ForeignKey('news_meta.news_id'))
    news_fulltext = db.Column('news_fulltext', db.Text)


with app.app_context():
    db.create_all()
