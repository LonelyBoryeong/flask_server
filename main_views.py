from flask import Blueprint, Flask, jsonify, render_template, redirect, url_for
import factory_model
import datetime
bp = Blueprint('main', __name__ , url_prefix= '/')

# 뉴스 테이블 중 하나를 사용하여 제목 리스트 가져오기
@bp.route('/')
def list_news():
    news = factory_model.Naver_news
    titles = news.query.with_entities(news.id, news.title).all()
    return render_template('news_list.html', titles=titles)

# 뉴스 상세보기 페이지
@bp.route('/news/<int:news_id>')
def show_news_detail(news_id):
    # 특정 ID에 해당하는 뉴스 가져오기
    news = factory_model.Naver_news.query.get(news_id)
    return render_template('news_detail.html', news=news)

@bp.route('/f_g_score')
def f_g_score():
    return render_template('f_g_score.html')

@bp.route('/reset')
def reset_naver_news_table():
    """
    Naver_news 테이블을 리셋하는 함수
    기존 테이블을 삭제한 후 동일한 구조로 새로 생성합니다.
    """
    
    factory_model.reset_naver_news_table()
    return redirect(url_for('main.list_news'))



@bp.route('/news_crawler')
def news_crawler():
    # 크롤링 실행
    # 현재 날짜를 가져옴 (시간 제외)
    today = datetime.date.today()

    #start_date = datetime(2024, 6, 1)
    #end_date = datetime(2024, 6, 30)
    start_date = today
    end_date = today
    page_num = 1  # 각 날짜마다 크롤링할 페이지 수

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
@bp.route('/news')
def show_news():
    # 샘플 데이터
    news_data = {
        "content": "\"머루, 다래, 산딸기 등으로 현금 수입 올려\"…지방발전 10x20 정책 일환 (서울=뉴스1) 유민주 기자 = 북한이 바닷가 양식에 이어 산속 먹거리도 적극 발굴하고 활용할 것을 당부했다. 북한 노동당 기관지 노동신문은 18일 '산을 낀 곳에서는 산을, 바다를 낀 곳에서는 바다를 잘 이용하자'라는 제목의 기사에서 \"지방에 있는 좋은 조건들과 예비들을 최대한으로 동원한 데 대한 독창적인 사상과 방침을 제시하시고 정력적으로 이끌어주신 아버이 수령(김일성)의 영도 아래 조국당 어디서나 전변의 새 역사는 끊임없이 펼쳐졌다\"라고 보도했다. 이어 산이 군 면적의 95%를 차지하는 창성군을 조명하며 \"신세타령만 하던 창성군 인민들이 산을 잘 이용한 데 대한 당의 방침을 잘 받들었다\"라고 선전했다. 이들은 \"산중에 풍부한 머루, 다래, 산딸기 등 각종 산 열매와 산나물, 공예작물 같은 것을 채취하여 여러 가지 식료품과 일용품을 생산하고 산골짜기마다에서는 소와 양을 비롯한 풀 먹는 짐승들을 대대적으로 길러 해마다 현금 수입을 늘렸다\"라고 설명했다. 또 창성군에 이어 자강도의 초산군과 평안남도의 양덕군을 비롯한 산간 지역에서도 주민들의 생활에 근본적인 변화가 일어났다고 전했다. 앞서 김정은 노동당 총비서는 지난달 함경남도 신포시 바닷가 양식장을 방문해 참가한 지방경제발전관련협의회에서 \"풍어동지구 앞 바다수역에서 밥조개(가리비)와 다시마 양식을 잘하면 척박하고 경제력이 약한 신포시가 3~4년 후에는 공화국의 시·군들 가운데 제일 잘사는 '부자시'가 될 수 있다\"라고 말했다. 신문은 \"신포시 바닷가양식업의 시범을 창조하고 이를 일반화하여 바닷가를 낀 시, 군들의 경제발전과 인민생활에서 실질적인 개선을 가져오며 당의 지방발전정책을 보다 강력히 추진시켜 나갈 수 있는 역사적인 이정표를 마련한 7월의 지방경제발전관련협의회는 오늘의 '창성연석회의'로 공화국 역사에 기록됐다\"라고 보도했다. 이 밖에도 지역마다 당의 지방발전정책 관철을 위해 추진하고 있는 사업들이 소개됐다. 남포시에서는 구역, 군원료기지사업소의 작업반실과 축사, 온실건설공사를 본격적으로 하고 있다고 소개했다. 봉천군에서도 기름작물비배광리를 과학기술적으로 높이기 위한 사업에 힘을 싣고, 함주군에서는 현재 지방공업공장들의 정상 운영에 필요한 기능공들을 더 많이 키워내기 위한 사업의 일환으로 직업기술학교 교육수준 제고에 집중하고 있다는 소식을 전했다. 올해 1월 시정연설에서 김 총비서는 '지방발전 10x20 정책' 구상에서 지역별 특성에 맞는 경제적 자원 적극 개발을 강조했다. 이는 식량난 극복이 어려운 북한 주민들의 식량 수요를 채우기 위한 것으로 보인다. 이날 신문도 \"모든 일꾼은 자기 지역의 특성과 자원을 합리적으로 이용하는 것이 가지는 중요성과 의의를 깊이 명심하고 당의 '지방발전 20X10 정책' 실현의 성공적 결실을 위해 분투해야 할 것\"이라고 강조했다.",
        "date": "20240818",
        "keyword": ["경제", "수입", "노동"],
        "title": "\"머루, 다래, 산딸기 등으로 현금 수입 올려\"…지방발전 10x20 정책 일환",
        "url": "https://n.news.naver.com/mnews/article/421/0007735227?sid=101"
    }

    return render_template('news.html', news=news_data)

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
    