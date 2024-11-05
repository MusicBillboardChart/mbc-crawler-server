import requests
from bs4 import BeautifulSoup
import os 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        "chart_list" : "tbody > tr",
        "title" : ".wrap_song_info .rank01 a",
        "artist" : ".wrap_song_info .rank02 a"
    },
    "youtubeMusic": { # 셀레니움 필요
         "link":"https://charts.youtube.com/charts/TopSongs/kr/weekly",
         "chart_list" : '/html/body/ytmc-v2-app/ytmc-detailed-page/div[2]/ytmc-chart-table-v2/div',
         "title" : '//*[@id="entity-title"]',
         "artist" : '//*[@id="artist-names"]'
         },
    "genie": { # 스크래핑은 되지만 50위 까지만 긁어와짐 (결론 : 셀레니움 필요)
              "link":"https://www.genie.co.kr/chart/top200?ditc=D&ymd=20241026&hh=21&rtm=Y&pg=1",
              "chart_list" : "tbody > tr",
              "title" : ".info > .title",
              "artist" : ".info > .artist"
    },
    "vibe" : { # 셀레니움 필요
      "link" :"https://vibe.naver.com/chart/total",
      "chart_list" : "tbody > tr",
      "title": "div.title_badge_wrap > span",
      "artist": "div.artist_sub > span"
    },
    "bugs" : {
      "link" :"https://music.bugs.co.kr/chart",
      "chart_list" : 'tbody > tr',
      "title": "p.title > a",
      "artist": "p.artist > a"
    },
    "flo": { # 셀레니움 필요
        "link":"https://www.music-flo.com/browse",
        "chart_list" : '/html/body/div[2]/div[1]/section/div/div[2]/div[2]/table',
        "title": '//*[@id="browseRank"]/div[2]/table/tbody/tr[1]/td[4]/div/div[2]/button/p/span/strong',
        "artist": '//*[@id="browseRank"]/div[2]/table/tbody/tr[1]/td[5]/p/span[1]'
    } 
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def vibeScrapy(driver) :
    try:
        popup = driver.find_element(By.CLASS_NAME, "AdvertisingPopup_btn_close_3yEbw")
        popup.click()
    except:
        print("팝업이 없거나 이미 닫혀있습니다.")
        return
        
def floClickButton(driver) :
    try:
        readMore = driver.find_element(By.XPATH, '//*[@id="browseRank"]/div[2]/div/button')
        readMore.click()
        print("더보기 버튼 클릭")
    except:
        print("팝업이 없거나 이미 닫혀있습니다.")
        return
    
def scrapy(chart_list, site_info, site_name, site_link):
    global rank
    rank = 0
    driver = webdriver.Chrome()
    driver.get(site_link)
    
    if site_name == "vibe":
        vibeScrapy(driver)
    
    if site_name == "flo" : 
        floClickButton(driver)
    time.sleep(3)
    
    songs = driver.find_elements(By.XPATH, chart_list)

    for rankNum, song in enumerate(songs[:100], 1):
        try:
            title = song.find_element(By.XPATH, site_info["title"]).text.strip()
            artist = song.find_element(By.XPATH, site_info["artist"]).text.strip()
            rank = rankNum
            # dir = db.reference(site_name)
            # dir.update({rank: f"{title} - {artist}"})
            print(f"{rank}. {title} - {artist}")
        except Exception as e:
            print(f"Error at rank {rankNum}: {str(e)}")
    
    driver.quit()
    return rank

def crawl(site_name):
    if not isinstance(urls[site_name], dict):
        print(f"Error: {site_name}의 정보가 없습니다.")
        return
    site_info = urls[site_name]
    site_link = site_info["link"]
    chart_list = site_info["chart_list"]
    scrapy(chart_list, site_info, site_name, site_link)

crawl("flo")