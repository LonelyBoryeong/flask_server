from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# 데이터베이스 URI 설정 (여기서는 SQLite를 사용)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy 객체 생성
db = SQLAlchemy(app)
# Flask-Migrate 객체 생성
migrate = Migrate(app, db)

@app.route("/", methods=['GET'])
def hello():
  return "hello world"

# 모델 정의
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
#질문 답변 시스템 db
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)


#뉴스 기사용 db
class News_FG(db.Model):
    #date, title, content, url, keyword
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    url = db.Column(db.String(500), nullable=False)  # URL 저장용 필드
    keyword = db.Column(db.JSON, nullable=False)  # 키워드 리스트를 저장하는 필드


# 데이터베이스 생성
with app.app_context():
    db.create_all()

# Flask 앱 실행
if __name__ == '__main__':
    app.run(debug=True)