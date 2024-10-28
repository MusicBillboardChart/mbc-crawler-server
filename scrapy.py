import requests
from bs4 import BeautifulSoup

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
    "genie": {
              "link":"https://www.genie.co.kr/chart/top200?ditc=D&ymd=20241026&hh=21&rtm=Y&pg=1",
              "chart_list" : "tbody > tr",
              "title" : ".info > .title",
              "artist" : ".info > .artist"
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

rank = 0


def scrapy(chart_list, site_info, rank) :
    for rankNum, song in enumerate(chart_list[rank:100], 1):
            title = song.select_one(site_info["title"]).text.strip()
            artist = song.select_one(site_info["artist"]).text.strip()
            rank = rankNum
            print(f"{rankNum}. {title} - {artist}")
    print(f"Rank : {rank}")
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
    scrapy(chart_list, site_info, rank)

crawl("youtubeMusic")

