import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import random
import nest_asyncio
from tqdm.asyncio import tqdm_asyncio
import os
import csv
import torch
from transformers import pipeline
import warnings

warnings.filterwarnings("ignore")

# nest_asyncio를 적용하여 중첩된 이벤트 루프 허용
nest_asyncio.apply()

# GPU 사용 가능 여부 확인
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# 감성 분석 파이프라인 초기화
sentiment_pipeline = pipeline("text-classification", model="snunlp/KR-FinBert-SC", device=device)

# 경제 관련 키워드 리스트
economic_keywords = [
    '경제', '경제성장', '경제위기', '금융', '물가', '인플레이션', '디플레이션', '경기', '불황', '호황',
    '주식', '증시', '코스피', '코스닥', '환율', '금리', '채권', '펀드', '선물', '옵션', '파생상품', '외환',
    '무역', '수출', '수입', '관세', 'FTA', '세계경제', '글로벌경제', '미중무역전쟁', '보호무역', '자유무역',
    '고용', '실업', '일자리', '노동', '임금',
    '부동산', '주택', '아파트', '재개발',
    'GDP', '무역수지', '경상수지', '소비자물가지수', '생산자물가지수', '실업률', '경제성장률', '기준금리',
]

def is_economic_news(title, content):
    title = title or ""
    content = content or ""
    text = f"{title} {content}"
    matching_keywords = [keyword for keyword in economic_keywords if keyword in text]
    return (bool(matching_keywords), matching_keywords)

def clean_text(text):
    if text is None:
        return ""
    return ''.join(char for char in text if ord(char) < 65536)  # UTF-16 범위 내의 문자만 유지

def analyze_sentiment(text):
    if pd.isna(text):
        return '중립'
    result = sentiment_pipeline(str(text)[:512])[0]  # 텍스트 길이 제한
    label = result['label']
    if label == 'positive':
        return '탐욕'
    elif label == 'negative':
        return '공포'
    else:
        return '중립'

class NewsCrawlerAnalyzer:
    def __init__(self, start_date, end_date, page_num):
        self.start_date = start_date
        self.end_date = end_date
        self.page_num = page_num
        self.data = []
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        self.progress_dir = '/content/drive/MyDrive/고독한보령/공포탐욕/공포탐욕뉴스/네이버뉴스'
        self.output_dir = self.progress_dir

    def get_progress_file(self, date):
        year_month = date.strftime('%Y_%m')
        return os.path.join(self.progress_dir, f'crawling_progress_{year_month}.txt')

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

    async def get_news_content(self, session, url):
        async with session.get(url, headers=self.headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            try:
                article = soup.select_one('#dic_area')
                if article:
                    title_elem = soup.select_one('h2#title_area, h3#articleTitle')
                    title = title_elem.text.strip() if title_elem else "제목 없음"
                    content = ' '.join(p.strip() for p in article.strings if p.strip())
                    return clean_text(title), clean_text(content)
                else:
                    return None, None
            except Exception as e:
                print(f"Error parsing article content from {url}: {e}")
                return None, None

    async def process_url(self, session, url, date):
        title, content = await self.get_news_content(session, url)
        re = is_economic_news(title, content)
        if re[0]:  # Only add if it's economic news
            sentiment = analyze_sentiment(content)
            self.data.append({
                'date': date,
                'title': title,
                'content': content,
                'url': url,
                'keywords': re[1],
                'sentiment': sentiment
            })

    async def crawl_date(self, session, date):
        date_str = date.strftime('%Y%m%d')
        urls = await self.get_news_urls(session, date_str)
        tasks = [self.process_url(session, url, date_str) for url in urls]
        await asyncio.gather(*tasks)

    def save_to_csv(self, data, filename):
        df = pd.DataFrame(data)
        try:
            df.to_csv(filename, index=False, encoding='utf-8', mode='a',
                      header=not os.path.exists(filename), errors='replace',
                      escapechar='\', quoting=csv.QUOTE_ALL)
        except Exception as e:
            print(f"UTF-8 인코딩으로 CSV 저장 중 오류 발생: {e}")
            try:
                print("CP949 인코딩으로 저장을 시도합니다...")
                df.to_csv(filename, index=False, encoding='cp949', mode='a',
                          header=not os.path.exists(filename), errors='replace',
                          escapechar='\', quoting=csv.QUOTE_ALL)
            except Exception as e:
                print(f"CP949 인코딩으로 저장 중 오류 발생: {e}")
                print("데이터를 저장할 수 없습니다.")

    def save_progress(self, date):
        progress_file = self.get_progress_file(date)
        with open(progress_file, 'w') as f:
            f.write(date.strftime('%Y-%m-%d'))

    def load_progress(self, date):
        progress_file = self.get_progress_file(date)
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                return datetime.strptime(f.read().strip(), '%Y-%m-%d')
        return None

    async def crawl(self):
        current_date = self.start_date
        total_days = (self.end_date - self.start_date).days + 1
        pbar = tqdm_asyncio(total=total_days, desc="Crawling and Analyzing Progress")

        async with aiohttp.ClientSession() as session:
            while current_date <= self.end_date:
                last_crawled_date = self.load_progress(current_date)
                if last_crawled_date and last_crawled_date >= current_date:
                    current_date = last_crawled_date + timedelta(days=1)
                    pbar.update((last_crawled_date - self.start_date).days + 1)
                    continue

                year_folder = f"{current_date.year}end"
                year_path = os.path.join(self.output_dir, year_folder)
                os.makedirs(year_path, exist_ok=True)

                output_file = os.path.join(year_path, f"sentiment_naver_economic_news_{current_date.year}_{current_date.month:02d}.csv")
                await self.crawl_date(session, current_date)
                self.save_to_csv(self.data, output_file)
                self.save_progress(current_date)
                self.data = []  # Clear the data after saving to CSV
                current_date += timedelta(days=1)
                pbar.update(1)
                await asyncio.sleep(random.uniform(1, 3))  # 요청 간 랜덤 지연
        pbar.close()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.crawl())
        return pd.DataFrame(self.data)

# 크롤링 및 분석 실행
YEAR = 2024       # 원하는 년도로 수정하세요 (2009-2023)
START_MONTH = 8   # 시작 월
END_MONTH = 8     # 종료 월 (포함)
page_num = 10     # 각 날짜마다 크롤링할 페이지 수

start_date = datetime(YEAR, START_MONTH, 1)
end_date = datetime(YEAR, END_MONTH, 31)

crawler_analyzer = NewsCrawlerAnalyzer(start_date, end_date, page_num)
df = crawler_analyzer.run()

print("크롤링, 감성 분석 완료 및 CSV 저장 완료")

     