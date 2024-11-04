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
         "chart_list" : "ytmc-v2-app > ytmc-detailed-page > div:nth-of-type(2) > ytmc-chart-table-v2 > div > ytmc-entry-row",
         "title" : "ytmc-v2-app > ytmc-detailed-page > div:nth-of-type(2) > ytmc-chart-table-v2 > div > ytmc-entry-row > div > div > div:nth-of-type(2) > div > div:nth-of-type(1)",
         "artist" : "ytmc-v2-app > ytmc-detailed-page > div:nth-of-type(2) > ytmc-chart-table-v2 > div > ytmc-entry-row > div > div > div:nth-of-type(1) > span"
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
      "chart_list" : "tbody > tr",
      "title": "p.title > a",
      "artist": "p.artist > a"
    },
    "flo": "https://www.music-flo.com" # 셀레니움 필요
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def scrapy(chart_list, site_info, site_name, site_link):
    global rank
    rank = 0
    driver = webdriver.Chrome()
    time.sleep(3)
    driver.get(site_link)
    if site_name == "vibe":
        try:
            popup = driver.find_element(By.CLASS_NAME, "AdvertisingPopup_btn_close_3yEbw")
            popup.click()
        except:
            print("팝업이 없거나 이미 닫혀있습니다.")
        
        time.sleep(3)
        
        songs = driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
        
        for rankNum, song in enumerate(songs[:100], 1):
            try:
                title = song.find_element(By.CSS_SELECTOR, "div.title_badge_wrap > span").text.strip()
                artist = song.find_element(By.CSS_SELECTOR, "div.artist_sub > span").text.strip()
                rank = rankNum
                dir = db.reference(site_name)
                dir.update({rank: f"{title} - {artist}"})
                print(f"{rank}. {title} - {artist}")
            except Exception as e:
                print(f"Error processing rank {rankNum}: {str(e)}")
        
    else:
        for rankNum, song in enumerate(chart_list[rank:100], 1):
            title = song.select_one(site_info["title"]).text.strip()
            artist = song.select_one(site_info["artist"]).text.strip()
            rank = rankNum
            dir = db.reference(site_name)
            dir.update({rank: f"{title} - {artist}"})
            print(f"{rank}. {title} - {artist}")
        driver.quit()
    return rank

def crawl(site_name):
    if not isinstance(urls[site_name], dict):
        print(f"Error: {site_name}의 정보가 없습니다.")
        return
    site_info = urls[site_name]
    site_link = site_info["link"]
    res = requests.get(site_link, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    chart_list = soup.select(site_info["chart_list"])
    scrapy(chart_list, site_info, site_name, site_link)

crawl("vibe")