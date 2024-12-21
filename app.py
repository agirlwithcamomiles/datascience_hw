from flask import Flask
from flask import request, redirect
from flask import render_template
from flask import flash
from sqlalchemy.sql import text
from Model import Meta, db, Author, Categories, News_categories, Short_text, Full_text
import matplotlib.pyplot as plt
import io
import base64



app = Flask(__name__, template_folder='C:/Users/vikto/PycharmProjects/programming_year2/programming_hw3/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rshu_crowled.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.app = app
db.init_app(app)
app.secret_key = b'a secret key'

@app.route('/')
def index():
    return render_template('base')


@app.route('/questions')
def question_page():
    return render_template('questions.html')


@app.route('/process', methods=['GET'])
def answer_process():
    if request.args.get('author_text')  is None or request.args.get('news_title')  is None or request.args.get('news_shorttext') is None or request.args.get('news_fulltext') is None or request.args.get('author_photo') is None:
        return redirect('/questions')

    author_text = request.args.get('author_text')
    news_title = request.args.get('news_title')
    news_shorttext = request.args.get('news_shorttext')
    news_fulltext = request.args.get('news_fulltext')
    author_photo = request.args.get('author_photo')
    date = request.args.get('publication_date')

    author = db.session.query(Author).filter_by(name=author_text).first()
    if author is None:
        author = Author(name=author_text)
        db.session.add(author)
        db.session.flush()

    author_photos = db.session.query(Author).filter_by(name=author_photo).first()
    if author_photos is None:
        author_photos = Author(name=author_photo)
        db.session.add(author_photos)
        db.session.flush()

        author_text_id = db.session.query(Author.author_id).filter_by(name=author_text).scalar()
        author_photo_id = db.session.query(Author.author_id).filter_by(name=author_photo).scalar()
        meta = Meta(title=news_title,
                    date=date,
                    author_text=author_text_id,
                    author_photo=author_photo_id)
        db.session.add(meta)
        db.session.flush()
        db.session.commit()

        news_id = db.session.query(Meta.news_id).filter(Meta.title == news_title).scalar()
        short_text = Short_text(news_id=news_id, news_shorttext=news_shorttext)
        db.session.add(short_text)

        full_text = Full_text(news_id=news_id, news_fulltext=news_fulltext)
        db.session.add(full_text)
        db.session.flush()
        db.session.commit()
    return "Data processed successfully!"


@app.route('/search')
def search():
    titles = Meta.query.all()
    categories = Categories.query.all()

    data = {
        "titles": titles,
        "categories": categories
    }
    return render_template("search.html", data=data)


@app.route('/results')
def results():
    if request.values.get("news_title") and request.values.get("categories"):
        search_result = db.session.query(Meta)\
            .join(News_categories) \
            .join(Categories) \
            .filter(
                Meta.news_id == request.values.get("news_title", int),
                Categories.category_id == request.values.get("categories", int),
            )
        search_result = search_result.limit(250).all()
        if len(search_result) == 0:
            flash(f'No such news')
            return redirect('/search')
        else:
            return render_template("results.html", results=search_result)
    elif request.values.get("news_title") and not request.values.get("categories"):
        search_result = db.session.query(Meta) \
            .join(News_categories) \
            .join(Categories) \
            .filter(
            Meta.news_id == request.values.get("news_title", int),
        )
        search_result = search_result.all()
        return render_template("results.html", results=search_result)
    elif not request.values.get("news_title") and request.values.get("categories"):
        search_result = db.session.query(Meta) \
            .join(News_categories) \
            .join(Categories) \
            .filter(
            Categories.category_id == request.values.get("categories", int),
        )
        search_result = search_result.limit(250).all()
        return render_template("results.html", results=search_result)
    else:
        search_result = []
        return "No results found."


@app.route('/stats')
def stats():
    # top five most productive days with greatest number of news
    top_dates = db.session.execute(text('SELECT date, count(*) FROM news_meta GROUP BY date ORDER BY count(*) DESC LIMIT 5')).fetchall()

    dates = list()
    counts = list()
    for row in top_dates:
        dates.append(str(row[0]))
        counts.append(row[1])

    # the plot to embed in html file
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.bar(dates, counts, color='aquamarine')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of articles')
    ax.set_title('Top 5 dates with most articles')
    ax.tick_params(axis='x', labelsize=8)
    plt.xticks(rotation=15)

    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)
    img_top_dates_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')


    # top five most productive authors with greatest number of news
    top_authors_of_texts = db.session.execute(text('SELECT author_name, count (*) FROM news_meta JOIN authors ON news_meta.author_text = authors.author_id GROUP BY author_name ORDER BY count(*) DESC LIMIT 5')).fetchall()
    authors = list()
    counts_2 = list()
    for row in top_authors_of_texts:
        authors.append(str(row[0]))
        counts_2.append(row[1])

    # the plot to embed in html file
    fig, ax2 = plt.subplots(figsize=(10, 7))
    ax2.bar(authors, counts_2, color='aquamarine')
    ax2.set_xlabel('Author')
    ax2.set_ylabel('Number of articles')
    ax2.set_title('Top 5 authors with most articles')
    ax2.tick_params(axis='x', labelsize=8)
    plt.xticks(rotation=15)

    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)
    img_top_auts_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')


    # list of text authors who are also photographers
    text_photo = db.session.execute(text('SELECT author_name FROM news_meta JOIN authors ON news_meta.author_text = authors.author_id INTERSECT SELECT author_name FROM news_meta JOIN authors ON news_meta.author_photo = authors.author_id')).fetchall()

    # average number of categories per news item
    avg_cats = db.session.execute(text('SELECT COUNT(category_id) / COUNT(news_meta.news_id) FROM news_categories JOIN news_meta ON news_categories.news_id = news_meta.news_id')).fetchall()

    # top 5 most popular categories
    top_cats = db.session.execute(text('SELECT category_name, count(*) FROM categories JOIN news_categories ON categories.category_id = news_categories.category_id GROUP BY category_name ORDER BY count(*) DESC LIMIT 5')).fetchall()

    categories = list()
    counts_3 = list()
    for row in top_cats:
        categories.append(str(row[0]))
        counts_3.append(row[1])

    # the plot to embed in html file
    fig, ax3 = plt.subplots(figsize=(10, 7))
    ax3.bar(categories, counts_3, color='aquamarine')
    ax3.set_xlabel('Category')
    ax3.set_ylabel('Number of articles')
    ax3.set_title('Top 5 categories with most articles')
    ax3.tick_params(axis='x', labelsize=8)
    plt.xticks(rotation=12)

    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)
    img_top_cats_base64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

    return render_template("stats.html", chart_img_1=img_top_dates_base64, chart_img_2=img_top_auts_base64, authors=enumerate(text_photo, start=1), number=avg_cats[0][0], chart_img_3=img_top_cats_base64)


if __name__ == '__main__':
    app.run(debug=False)
