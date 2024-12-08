# app.py
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///articles.db'
db = SQLAlchemy(app)

# app.py
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    preview = db.Column(db.String(250))  # Add preview field
    author = db.Column(db.String(100))
    date = db.Column(db.String(100))
    link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/upload', methods=['POST'])
def upload_article():
    data = request.get_json()
    new_article = Article(
        title=data['title'],
        content=data['content'],
        preview=data.get('preview'),  # Get preview from data
        author=data['author'],
        date=data['date'],
        link=data['link']
    )
    db.session.add(new_article)
    db.session.commit()
    return jsonify({'message': 'Article uploaded successfully'}), 200

    
@app.route('/')
def index():
    # get latest 3 articles
    articles = Article.query.order_by(Article.created_at.desc()).limit(3).all()
    return render_template('index.html', articles=articles)


@app.get('/all')
def all_news():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('all.html', articles=articles)


@app.get('/article/<id>')
def article(id):
    article = Article.query.get(id)
    return render_template('article.html', article=article)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)