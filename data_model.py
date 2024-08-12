# data_model.py

from app import app, db, News_FG
from datetime import datetime, timezone

# 애플리케이션 컨텍스트 설정
def test_add():
    with app.app_context():
        # 데이터 생성
        news_item = News_FG(
            date=datetime.now(timezone.utc),
            title="경제 뉴스",
            content="경제 관련 뉴스 내용",
            url="https://example.com/news/12345",
            keyword=['물가', '인플레이션']
        )
        
        # 데이터베이스에 추가
        db.session.add(news_item)
        db.session.commit()



# 첫 번째 뉴스 기사 조회
with app.app_context():
    first_news = News_FG.query.first()
    if first_news:
        print(f"Title: {first_news.title}, Date: {first_news.date}, URL: {first_news.url}, Keywords: {first_news.keyword}")

