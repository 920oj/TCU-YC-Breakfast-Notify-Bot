import requests, re, sys, datetime
from time import sleep
from bs4 import BeautifulSoup

# 各種認証情報
SITE_ID = 'xxxxx' # 学食情報サイトのログインIDを入力
SITE_PASS = 'xxxxx' # 学食情報サイトのログインPASSを入力
LINE_TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' # LINE Notify APIのTokenを入力
LINE_API_URL = "https://notify-api.line.me/api/notify" # LINE Notify APIのエンドポイントURIを入力

now_date = datetime.datetime.now()
today_data = str(now_date.date()).replace('-','/')

def get_sessionid():
    # 初期Cookieの取得処理
    r = requests.get('https://livexnet.jp/local/default.asp')
    first_access_cookie = str(r.headers['Set-Cookie'])
    
    # "ASPSESSIONID+任意の8桁の英大文字"(英大文字24文字)の取得
    asp_session = str(first_access_cookie[first_access_cookie.find("ASPSESSIONID"):first_access_cookie.find("; secure")])
    asp_session_key = str(asp_session[0:asp_session.find("=")])
    asp_session_id = str(asp_session[asp_session.find("="):].replace('=',''))
    return asp_session_key, asp_session_id

def get_breakfast_info(key,id):
    # Cookieを用意（今後情報が変更される可能性あり）
    site_cookies = {
        key: id, 
        'KCD': '02320', 
        'company_id': SITE_ID, 
        'company_pw': SITE_PASS, 
        'wrd': 'jp', 
        'dip': '0', 
        'ink': 'a', 
        'bcd': '02320', 
        'val': 'daily'
    }
    
    # メニュー・栄養表ページにアクセス
    url = 'https://reporting.livexnet.jp/eiyouka/menu.asp?val=daily&bcd=02320&ink=a&col=&str=' + today_data
    r = requests.get(url, cookies=site_cookies)
    r.encoding = r.apparent_encoding
    
    # HTML解析
    all_html = r.text.replace('<br>','')
    souped_html = BeautifulSoup(all_html, 'lxml')
    
    try:
        breakfast = souped_html.find('p', class_="img_comment6").string
        return breakfast
    except:
        return False

def post_line(result):
    post_data = '本日(' + today_data + ')の100円朝食は、' + result + 'です。'
    
    line_api_headers = {"Authorization" : "Bearer "+ LINE_TOKEN}
    line_payload = {"message" :  post_data}
    
    r = requests.post(LINE_API_URL ,headers = line_api_headers ,params=line_payload)
    return r.status_code

def main():
    print('東京都市大学100円朝食メニュー表示プログラム by 920OJ')
    print('今日は' + today_data + 'です。')
    
    session = get_sessionid()
    session_key = session[0]
    session_id = session[1]
    
    print('初期認証情報を取得しました。' + session_key + 'は' + session_id + 'です。3秒間待機します……')
    sleep(3)
    
    result = get_breakfast_info(session_key,session_id)
    
    if not result:
        print('情報を取得できませんでした。100円朝食が実施されていない可能性があります。')
        sys.exit()

    print('今日の100円朝食は、' + result + 'です。LINEに通知を送信します。')
    
    post_status = post_line(result)
    if post_status == 200:
        print('LINE通知に成功しました。プログラムを終了します。')
    else:
        print('LINE通知に失敗しました。レスポンスは' + str(post_status) + 'です。プログラムを終了します。')
    
if __name__ == "__main__":
    main()