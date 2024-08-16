from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import model2 

app = Flask(__name__)

# 데이터베이스 URI 설정 (여기서는 SQLite를 사용)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy 객체 생성
db = SQLAlchemy(app)
# Flask-Migrate 객체 생성
migrate = Migrate(app, db)

#뉴스 기사용 db
class News_FG(db.Model):
    #date, title, content, url, keyword
    __tablename__ = 'News_FG'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), nullable=True)
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text(), nullable=True)
    url = db.Column(db.String(500), nullable=True)  # URL 저장용 필드
    keyword = db.Column(db.JSON, nullable=True)  # 키워드 리스트를 저장하는 필드

class News_senti(db.Model):
    __tablename__ = 'news_senti'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=True)
    fear_greed_index = db.Column(db.Integer, nullable=True)
    z_score_grade = db.Column(db.Integer, nullable=True)
    category = db.Column(db.Integer, nullable=True)

class Naver_news(db.Model):
    __tablename__ = 'Naver_news'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=True)
    title = db.Column(db.text, nullable=True)
    content = db.Column(db.text, nullable=True)
    url = db.Column(db.text, nullable=True)
    keyword = db.Column(db.JSON, nullable=True)
    

'''
@app.route("/", methods=['GET'])
def hello():
  return "hello world"
'''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news_crawler')
def news_crawler():
    # 크롤링 실행
    # 현재 날짜를 가져옴 (시간 제외)
    today = model2.datetime.date.today()

    #start_date = datetime(2024, 6, 1)
    #end_date = datetime(2024, 6, 30)
    start_date = today
    end_date = today
    page_num = 10  # 각 날짜마다 크롤링할 페이지 수

    crawler = model2.NewsCrawler(start_date, end_date, page_num)
    df_json = crawler.run_tmp()
    # 애플리케이션 컨텍스트 설정
    return df_json

@app.route('/data')
def data():
    # 실제 데이터 파일 경로를 사용하세요
    df = pd.read_csv('/Users/leechanho8511/vscode/flask/flask2/data/뉴스분석지표_daily_2008_2024.csv')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')

    # NaT (잘못된 날짜 형식) 데이터를 제거
    df = df.dropna(subset=['date'])

    # 데이터 준비
    data = {
        "dates": df['date'].dt.strftime('%Y-%m-%d').tolist(),
        "fear_greed_index": df['fear_greed_index'].tolist(),
        "z_score_grade": df['z_score_grade'].tolist(),
        "category": df['category'].tolist()
    }

    return jsonify(data)
    

# 데이터베이스 생성
with app.app_context():
    db.create_all()

# Flask 앱 실행
if __name__ == '__main__':
    app.run(debug=True)
