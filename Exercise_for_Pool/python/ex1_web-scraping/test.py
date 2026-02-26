import requests
from bs4 import BeautifulSoup

url = "https://pig-data.jp"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")

if r.status_code == requests.codes.ok:
    print("成功：データを取得しました")
    print()

    print(r.encoding)
    titles = soup.find_all("h2")
    for title in titles:
        print(title.get_text())


else:
    print(f"失敗：ステータスコード{r.status_code}")