import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import random
import nest_asyncio
from tqdm import tqdm
from extensions import db
from datetime import datetime

# nest_asyncio를 적용하여 중첩된 이벤트 루프 허용
nest_asyncio.apply()
class Naver_news(db.Model):
    __tablename__ = 'Naver_news'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=True)
    title = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)
    keyword = db.Column(db.JSON, nullable=True)
    sentiment = db.Column(db.String(10),nullable=True)
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




# 경제 관련 키워드 리스트
economic_keywords = [
    # 일반 경제 용어
    '경제', '경제성장', '경제위기', '금융', '물가', '인플레이션', '디플레이션', '경기', '불황', '호황',

    # 금융 시장 관련
    '주식', '증시', '코스피', '코스닥', '환율', '금리', '채권', '펀드', '선물', '옵션', '파생상품', '외환',

    # 무역 및 국제 경제
    '무역', '수출', '수입', '관세', 'FTA', '세계경제', '글로벌경제', '미중무역전쟁', '보호무역', '자유무역',

    # 고용 및 노동
    '고용', '실업', '일자리', '노동', '임금',

    # 부동산
    '부동산', '주택', '아파트','재개발',

    # 경제 지표
    'GDP', '무역수지', '경상수지', '소비자물가지수', '생산자물가지수', '실업률', '경제성장률', '기준금리',
]


def reset_naver_news_table():
    """
    Naver_news 테이블을 리셋하는 함수
    기존 테이블을 삭제한 후 동일한 구조로 새로 생성합니다.
    """
    try:
        # 테이블 삭제
        Naver_news.__table__.drop(db.engine)

        # 테이블 생성
        db.create_all()

        print("Naver_news 테이블이 성공적으로 리셋되었습니다.") 
    except Exception as e:
        print(f"테이블 리셋 중 오류 발생: {e}") 

def is_economic_news(title, content):
    title = title or ""
    content = content or ""
    text = f"{title} {content}"
    matching_keywords = [keyword for keyword in economic_keywords if keyword in text]
    return (bool(matching_keywords), matching_keywords)

class NewsCrawler:
    def __init__(self, start_date, end_date, page_num):
        self.start_date = start_date
        self.end_date = end_date
        self.page_num = page_num
        self.data = []
        self.total_days = (end_date - start_date).days + 1
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    async def get_news_urls(self, session, date):
        urls = []
        for page in range(1, self.page_num + 1):
            url = f'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=101&date={date}&page={page}'
            async with session.get(url, headers=self.headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                news_list = soup.select('.newsflash_body .type06_headline li dl')
                news_list.extend(soup.select('.newsflash_body .type06 li dl'))

                for news in news_list:
                    news_url = news.a['href']
                    urls.append(news_url)

        return urls

    async def crawl(self):
        async with aiohttp.ClientSession() as session:
            pbar = tqdm(total=self.total_days, desc="Crawling Progress")
            current_date = self.start_date
            while current_date <= self.end_date:
                await self.crawl_date(session, current_date)
                current_date += timedelta(days=1)
                pbar.update(1)
                await asyncio.sleep(random.uniform(1, 3))
            pbar.close()

    async def get_news_content(self, session, url):
        async with session.get(url, headers=self.headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            try:
                article = soup.select_one('#dic_area')
                if article:
                    title = article.select_one('strong.media_end_summary')
                    title = title.text if title else "제목 없음"

                    # 이미지 설명 제거
                    for img_desc in article.select('em.img_desc'):
                        img_desc.decompose()

                    content = ' '.join(p.strip() for p in article.strings if p.strip())

                    return title, content
                else:
                    return None, None
            except:
                return None, None

    async def process_url(self, session, url, date):
        title, content = await self.get_news_content(session, url)
        re = is_economic_news(title, content)
        if re[0]:  # Only add if it's economic news
            self.data.append({
                'date': date,
                'title': title,
                'content': content,
                'url': url,
                'keyword': re[1]
            })

    async def crawl_date(self, session, date):
        date_str = date.strftime('%Y%m%d')
        urls = await self.get_news_urls(session, date_str)
        tasks = [self.process_url(session, url, date_str) for url in urls]
        await asyncio.gather(*tasks)

    async def crawl(self):
        async with aiohttp.ClientSession() as session:
            pbar = tqdm(total=self.total_days, desc="Crawling Progress")
            current_date = self.start_date
            while current_date <= self.end_date:
                await self.crawl_date(session, current_date)
                current_date += timedelta(days=1)
                pbar.update(1)
                await asyncio.sleep(random.uniform(1, 3))  # 요청 간 랜덤 지연
            pbar.close()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.crawl())
        #return pd.DataFrame(self.data)
        db.create_all()
        # 예시 JSON 데이터
        for item in self.data:
            # date 문자열을 datetime 객체로 변환
            date_obj = datetime.strptime(item['date'], '%Y%m%d')
            
            # Naver_news 객체 생성
            news_item = Naver_news(
                date=date_obj,
                title=item['title'],
                content=item['content'],
                url=item['url'],
                keyword=item['keyword']
            )
            # DB에 추가
            db.session.add(news_item)

        # 모든 변경 사항을 커밋
        db.session.commit()
        return self.data[0]
    
    def run_tmp(self):
        
        db.create_all()

        # 예시 JSON 데이터
        data = [
            {
                'date': '2024-08-16',
                'title': 'Example Title',
                'content': 'This is an example content.',
                'url': 'http://example.com',
                'keyword': 'example'
            },
            {
                'date': '2024-08-17',
                'title': 'Another Title',
                'content': 'This is another example content.',
                'url': 'http://example.com/another',
                'keyword': 'another'
            }
        ]

        for item in data:
            # date 문자열을 datetime 객체로 변환
            date_obj = datetime.strptime(item['date'], '%Y-%m-%d')
            
            # Naver_news 객체 생성
            news_item = Naver_news(
                date=date_obj,
                title=item['title'],
                content=item['content'],
                url=item['url'],
                keyword=item['keyword']
            )
            
            # DB에 추가
            db.session.add(news_item)

        # 모든 변경 사항을 커밋
        db.session.commit()