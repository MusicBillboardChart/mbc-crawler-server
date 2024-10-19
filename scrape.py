import requests
from bs4 import BeautifulSoup

url = "https://open.spotify.com/playlist/37i9dQZEVXbNxXF4SkHj9F"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

res = requests.get(url, headers=headers)
print("Status : ", res.status_code)

if res.status_code == 200:
    soup = BeautifulSoup(res.text, 'html.parser')
    print(soup.title)
    print(soup.title.getText())