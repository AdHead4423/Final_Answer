import requests
from bs4 import BeautifulSoup
import time

url = "https://r.gnavi.co.jp"
NUMBER_OF_ITEM = 5
ENCODING = requests.get(url).apparent_encoding

path = "/eki/0002922/noodle/rs/"
query = {"r":"300","p":1}

headers = {
    "User-Agent": "Mozilla/5.0 (Window NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def now_loading():
    """取得元のサーバーへの負担回避"""
    IDLING_TIME = 2
    print("\nページを取得中")
    time.sleep(IDLING_TIME)

now_loading()

try:
    r = requests.get(url+path,params=query,headers=headers,timeout=3)

    if r.status_code == requests.codes.ok:
        print("成功：データを取得しました")
        print()

        soup = BeautifulSoup(r.text,"html.parser")

        shop_links = soup.find_all("a",class_="style_titleLink___TtTO")

    print("見つかった店舗数：{}".format(len(shop_links)))
    print("最初の{}個のリンクを表示：".format(NUMBER_OF_ITEM))
    for i, link in enumerate(shop_links[:NUMBER_OF_ITEM]):
        print("{}. {}【{}】".format(i+1,link.text.strip(),link.get("href")))


    print("\n試しに１つ、サイトにアクセスしてみます")
    first_shop_url = shop_links[0].get("href")

    now_loading()
    res = requests.get(first_shop_url, headers=headers,timeout=3)

    if r.status_code == requests.codes.ok:
        print("成功：データを取得しました")

        res.encoding = ENCODING
        shop_soup = BeautifulSoup(res.text,"html.parser")

        phone_element = shop_soup.find(class_="phone-guide__number")
        phone = phone_element.text.strip() if phone_element else ""
        print("電話番号：{}".format(phone))

        address_element = shop_soup.find(class_= "region")
        address = address_element.text.strip() if address_element else ""
        print("場所：{}".format(address))

        official_link_element = shop_soup.find("a", title="オフィシャルページ")
        official_url = official_link_element.get("href") if official_link_element else ""

        if official_url != "":
            print("\n公式サイトへのアクセスをしてみます")
            now_loading()
            try:
                official_res = requests.get(official_url,headers=headers,timeout=3)
                final_url = official_res.url
                print("最終的なURL：{}".format(final_url))
            except:
                final_url = ""

        ssl_enabled = final_url.startswith("https://") if final_url else False
        print("SSL：{}".format(ssl_enabled))





except:
    # print(f"失敗：ステータスコード{r.status_code}")
    r.raise_for_status()