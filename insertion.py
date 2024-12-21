from Model import Meta, db, Author, Categories, News_categories, Links, Images, Short_text, Full_text
from flask import Flask
import pandas as pd
import re

app = Flask(__name__, template_folder='C:/Users/vikto/PycharmProjects/programming_year2/programming_hw3/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rshu_crowled.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.app = app
db.init_app(app)

df = pd.read_csv('crowler_rshu.csv')
df = pd.DataFrame(df)

#   заполним таблицу authors
unique_authors = list(set(df['author_text'].unique()) ^ set(df['author_photo'].unique()))
unique_authors = [item.rstrip().strip() for item in unique_authors]
authors_list = list()
for i in unique_authors:
    if i not in authors_list:
        authors_list.append(i)
        with app.app_context():
            new_author = Author(name=i)
            db.session.add(new_author)
            db.session.flush()
            db.session.commit()


#   заполним таблицу news_meta
df_1 = df[["title", "pub_date", "author_text", "author_photo"]]
meta_list = list(set((df_1.itertuples(index=False, name=None))))
for item in meta_list:
    with app.app_context():
        author_t = item[2].rstrip().strip()
        author_p = item[3].rstrip().strip()
        author_text = db.session.query(Author.author_id).filter_by(name=author_t).scalar()
        author_photo = db.session.query(Author.author_id).filter_by(name=author_p).scalar()
        if not Meta.query.filter_by(title=item[0]).first():
            new_meta = Meta(title=item[0], date=item[1], author_text=author_text, author_photo=author_photo)
            db.session.add(new_meta)
            db.session.flush()
            db.session.commit()

#   заполним таблицу categories
df_1 = df["tags"]
categories_dict_list = list()
for category in df_1:
    for cat in category.split(", "):
        cat = re.sub(r'[^a-zA-Zа-яА-ЯёЁ\d\s:]', '', cat)
        if cat not in categories_dict_list:
            categories_dict_list.append(cat)
            new_category = Categories(category_name=cat)
            with app.app_context():
                db.session.add(new_category)
                db.session.flush()
                db.session.commit()

#   заполним таблицу news_categories
df_1 = df[["title", "tags"]]
category_list = list(set(df_1.itertuples(index=False, name=None)))
for i in range(len(category_list)):
    for j in category_list[i][1].split(", "):
        j = re.sub(r'[^a-zA-Zа-яА-ЯёЁ\d\s:]', '', j)
        with app.app_context():
            news_id = db.session.query(Meta.news_id).filter(Meta.title == str(category_list[i][0])).scalar()
            category_id = db.session.query(Categories.category_id).filter(Categories.category_name == j).scalar()
            new_connection = News_categories(news_id=news_id, category_id=category_id)
            if not News_categories.query.filter_by(news_id=news_id, category_id=category_id).first():
                db.session.add(new_connection)
                db.session.flush()
                db.session.commit()

# заполним таблицу news_image
df_1 = df[["title", "image_link"]]
image_list = list(set(df_1.itertuples(index=False, name=None)))
for i in range(len(image_list)):
    with app.app_context():
        news_id = db.session.query(Meta.news_id).filter(Meta.title == str(image_list[i][0])).scalar()
        new_image = Images(news_id=news_id, news_images=image_list[i][1])
        if not Images.query.filter_by(news_id=news_id).first():
            db.session.add(new_image)
            db.session.flush()
            db.session.commit()

# заполним таблицу news_links
df_1 = df[["title", "href"]]
link_list = list(set(df_1.itertuples(index=False, name=None)))
for i in range(len(link_list)):
    with app.app_context():
        news_id = db.session.query(Meta.news_id).filter(Meta.title == str(link_list[i][0])).scalar()
        new_link = Links(news_id=news_id, news_links=link_list[i][1])
        if not Links.query.filter_by(news_id=news_id).first():
            db.session.add(new_link)
            db.session.flush()
            db.session.commit()

#   заполним таблицу news_shorttext
df_1 = df[["title", "short_text"]]
short_list = list(set(df_1.itertuples(index=False, name=None)))
for i in range(len(short_list)):
    with app.app_context():
        news_id = db.session.query(Meta.news_id).filter(Meta.title == str(short_list[i][0])).scalar()
        new_short = Short_text(news_id=news_id, news_shorttext=short_list[i][1])
        if not Short_text.query.filter_by(news_id=news_id).first():
            db.session.add(new_short)
            db.session.flush()
            db.session.commit()

# заполним таблицу news_longtext
df_1 = df[["title", "full_text"]]
full_list = list(set(df_1.itertuples(index=False, name=None)))
for i in range(len(full_list)):
    with app.app_context():
        news_id = db.session.query(Meta.news_id).filter(Meta.title == str(full_list[i][0])).scalar()
        new_full = Full_text(news_id=news_id, news_fulltext=full_list[i][1])
        if not Full_text.query.filter_by(news_id=news_id).first():
            db.session.add(new_full)
            db.session.flush()
            db.session.commit()
