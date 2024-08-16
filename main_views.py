from flask import Blueprint, Flask, jsonify, render_template
import factory_model
import datetime
bp = Blueprint('main', __name__ , url_prefix= '/')


@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/news_crawler')
def news_crawler():
    # 크롤링 실행
    # 현재 날짜를 가져옴 (시간 제외)
    today = factory_model.datetime.date.today()

    #start_date = datetime(2024, 6, 1)
    #end_date = datetime(2024, 6, 30)
    start_date = today
    end_date = today
    page_num = 10  # 각 날짜마다 크롤링할 페이지 수

    crawler = factory_model.NewsCrawler(start_date, end_date, page_num)
    df_json = crawler.run()
    # 애플리케이션 컨텍스트 설정
    return df_json

@bp.route('/news_crawler_tmp')
def news_crawler_tmp():
    # 크롤링 실행
    # 현재 날짜를 가져옴 (시간 제외)
    today = datetime.date.today()

    #start_date = datetime(2024, 6, 1)
    #end_date = datetime(2024, 6, 30)
    start_date = today
    end_date = today
    page_num = 10  # 각 날짜마다 크롤링할 페이지 수

    crawler = factory_model.NewsCrawler(start_date, end_date, page_num)
    df_json = crawler.run_tmp()
    print(df_json)
    re = jsonify(df_json)
    # 애플리케이션 컨텍스트 설정
    return re

@bp.route('/data')
def data():
    # 실제 데이터 파일 경로를 사용하세요
    df = factory_model.pd.read_csv('/Users/leechanho8511/vscode/flask/flask2/data/뉴스분석지표_daily_2008_2024.csv')
    df['date'] = factory_model.pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')

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
    