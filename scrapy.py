import os 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


load_dotenv()

cred = credentials.Certificate({
    "type": os.environ.get('type'),
    "project_id": os.environ.get('project_id'),
    "private_key_id": os.environ.get('private_key_id'),
    "private_key": os.environ.get('private_key').replace('\\n', '\n'),
    "client_email": os.environ.get('client_email'),
    "client_id": os.environ.get('client_id'),
    "auth_uri": os.environ.get('auth_uri'),
    "token_uri": os.environ.get('token_uri'),
    "auth_provider_x509_cert_url": os.environ.get('auth_provider_x509_cert_url'),
    "client_x509_cert_url": os.environ.get('client_x509_cert_url'),
    "universe_domain": os.environ.get('universe_domain')
})
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get('DB_URLS')
})

urls = {
    "melon": {
        "link" : "https://www.melon.com/chart/index.htm",
        "chart_list" : '//*[@id="frm"]/div/table/tbody/tr',
        "title" : ".wrap_song_info .rank01 a",
        "artist" : "td > div > div > div.ellipsis.rank02"
    },
    "youtubeMusic": {
        "link": "https://charts.youtube.com/charts/TopSongs/kr/weekly",
        "chart_list": "/html/body/ytmc-v2-app/ytmc-detailed-page/div[2]/ytmc-chart-table-v2/div/ytmc-entry-row/div/div",
        "title": "#entity-title",
        "artist": "#artist-names"
    },
    "youtubeMusicGlobal": {
        "link": "https://charts.youtube.com/charts/TopSongs/global/weekly",
        "chart_list": "/html/body/ytmc-v2-app/ytmc-detailed-page/div[2]/ytmc-chart-table-v2/div/ytmc-entry-row/div/div",
        "title": "#entity-title",
        "artist": "#artist-names"
    },
    "genie": {
        "link":"https://www.genie.co.kr/chart/top200?ditc=D&ymd=20241026&hh=21&rtm=Y&pg=1",
        "chart_list" : '//*[@id="body-content"]/div[6]/div/table/tbody/tr',
        "title" : '#body-content > div.newest-list > div > table > tbody > tr > td.info > a.title.ellipsis',
        "artist" : '#body-content > div.newest-list > div > table > tbody > tr > td.info > a.artist.ellipsis'
    },
    "vibe" : {
      "link" :"https://vibe.naver.com/chart/total",
      "chart_list" : '//*[@id="content"]/div[4]/div[2]/div/table/tbody/tr',
      "title": '#content > div.track_section > div:nth-child(2) > div > table > tbody > tr > td.song > div.title_badge_wrap > span',
      "artist": 'div.artist_sub > span'
    },
    "bugs" : {
      "link" :"https://music.bugs.co.kr/chart",
      "chart_list" : '//*[@id="CHARTrealtime"]/table/tbody/tr',
      "title": 'p.title > a',
      "artist": 'p.artist > a'
    },
}

def clickButton(driver, cssSelector) :
    try:
        popup = driver.find_element(By.XPATH, cssSelector)
        popup.click()
    except:
        print("팝업이 없거나 이미 닫혀있습니다.")

def genieTopAll(chart_list, site_info, site_name) :
    try:
        print("더보기 버튼 클릭")
        site_link = 'https://www.genie.co.kr/chart/top200?ditc=D&ymd=20241106&hh=10&rtm=Y&pg=2'
        page = 2
        scrapy(chart_list, site_info, site_name, site_link, page)
    except:
        print("더보기 버튼이 없습니다...")
        return

global rank, page
rank = 0
page = 1
    
def scrapy(chart_list, site_info, site_name, site_link, page):
    option = webdriver.ChromeOptions()
    headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    option.add_argument(f'user-agent={headers}')
    option.add_argument("--headless=new")
    driver = webdriver.Chrome(options=option)
    driver.get(site_link)
    if site_name == "vibe":
        clickButton(driver,'//*[@id="app"]/div[2]/div/div/a[2]')
    time.sleep(3)
    
    songs = driver.find_elements(By.XPATH, chart_list)
    for rankNum, song in enumerate(songs[:100], 1):
        try:
            title = song.find_element(By.CSS_SELECTOR, site_info["title"]).text.strip()
            artist = song.find_element(By.CSS_SELECTOR, site_info["artist"]).text.strip()
            rank = rankNum
            if page == 2 :
                rank = rank + 50           
            dir = db.reference(site_name)
            dir.update({rank: f"{title} - {artist}"})
            print(f"{rank}. {title} - {artist}")
            if rank == 50 and site_name == "genie":
                driver.quit()
                genieTopAll(chart_list, site_info, site_name)
        except Exception as e:
            print(f"Error at rank {rankNum}: {str(e)}")
    driver.quit()

def crawl(site_name):
    if not isinstance(urls[site_name], dict):
        print(f"Error: {site_name}의 정보가 없습니다.")
        return
    site_info = urls[site_name]
    site_link = site_info["link"]
    chart_list = site_info["chart_list"]
    page = 1
    scrapy(chart_list, site_info, site_name, site_link, page)

crawl("youtubeMusic")
crawl("youtubeMusicGlobal")
crawl("bugs")
crawl("genie")
crawl("melon")
crawl("vibe")