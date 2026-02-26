import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def split_address(address):
    """住所を都道府県、市区町村、番地、建物名に分割"""
    pattern = r"^(東京都|北海道|(?:京都|大阪)府|.{2,3}県)(.*?[市区町村])(.+)$"
    match = re.match(pattern, address)

    if match:
        prefecture = match.group(1)
        city = match.group(2)
        rest = match.group(3)

        # 番地と建物名を分割
        building_pattern = r"^(\D+)([0-9０-９\-ー−丁目番地号\s,，]+)(.*)$"
        building_match = re.match(building_pattern, rest)

        if building_match:
            town = building_match.group(1).strip()
            street = building_match.group(2).strip()
            building = building_match.group(3).strip()
        else:
            street = rest.strip()
            building = ""

        city += town

        return prefecture, city, street, building
    else:
        return "", "", address, ""

def get_shop_data(shop_url, headers, encoding):
    """1店舗のデータを取得"""
    time.sleep(3)
    try:
        response = requests.get(shop_url, headers=headers, timeout=15)
        response.raise_for_status()

        response.encoding = encoding
        soup = BeautifulSoup(response.text, "html.parser")

        # 店舗名
        name_element = soup.find("h1", class_="shop-info__name")
        if not name_element:
            name_element = soup.find("dt", class_="contact-term")
        name = name_element.text.strip() if name_element else ""

        # 電話番号
        phone_element = soup.find(class_="phone-guide__number")
        phone = phone_element.text.strip() if phone_element else ""

        # メールアドレス（ほとんどのページにない）
        email = ""

        # 住所
        address_element = soup.find(class_="region")
        full_address = address_element.text.strip() if address_element else ""

        # 住所を分割
        prefecture, city, street, building = split_address(full_address)

        # オフィシャルページのURL
        official_link = soup.find("a", title="オフィシャルページ")
        if not official_link:
            official_link = soup.find("a", string=re.compile("オフィシャル|ホームページ"))

        final_url = ""
        ssl_enabled = "FALSE"

        if official_link:
            official_url = official_link.get("href")
            time.sleep(3)
            try:
                official_response = requests.get(official_url, headers=headers, timeout=15, allow_redirects=True)
                final_url = official_response.url
                ssl_enabled = "TRUE" if final_url.startswith("https://") else "FALSE"
            except Exception as e:
                print("URL取得エラー: {}".format(e))
                final_url = ""
                ssl_enabled = "FALSE"

        return {
            "店舗名": name,
            "電話番号": phone,
            "メールアドレス": email,
            "都道府県": prefecture,
            "市区町村": city,
            "番地": street,
            "建物名": building,
            "URL": final_url,
            "SSL": ssl_enabled
        }
    except Exception as e:
        print("店舗データ取得エラー：{}".format(e))
        return None

# メイン処理
if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    all_shop_data = []
    target_count = 50

    # 複数ページから店舗を収集
    page = 1

    # 店舗一覧ページを取得
    search_url = "https://r.gnavi.co.jp"
    path = "/eki/0002922/western/rs/"
    query = {"r":"500","p":page}
    ENCODING = requests.get(search_url).apparent_encoding

    while len(all_shop_data) < target_count:
        query.update(p=page)
        print("\n=== ページ{}を取得中 ===".format(page))

        time.sleep(3)
        try:
            response = requests.get(search_url+path, headers=headers, params=query, timeout=15)
            response.raise_for_status()

            response.encoding = ENCODING
            soup = BeautifulSoup(response.text, "html.parser")

            # 店舗リンクを抽出
            shop_links = soup.find_all("a", class_="style_titleLink___TtTO")

            if not shop_links:
                print("店舗リンクが見つかりませんでした")
                break

            print("見つかった店舗数: {}".format(len(shop_links)))

            # 各店舗のデータを取得
            for i, link in enumerate(shop_links):
                    if len(all_shop_data) >= target_count:
                        break

                    shop_url = link.get("href")
                    print("\n[{}/{}] 取得中： {}".format(len(all_shop_data)+1,target_count,shop_url))

                    shop_data = get_shop_data(shop_url, headers,ENCODING)

                    if shop_data and shop_data["店舗名"]:
                        all_shop_data.append(shop_data)
                        print(" 成功： {}".format(shop_data["店舗名"]))
                        print("店舗URL：{}".format(shop_data["URL"]))
                    else:
                        print(" スキップ： データ取得失敗")


            page += 1

        except Exception as e:
            print("ページ取得エラー：{}".format(e))
            break


        # DataFrameに変換してCSV出力
    if all_shop_data:
        df = pd.DataFrame(all_shop_data)
        df.to_csv("1-1.csv", index=False, encoding="utf-8-sig")
        print("\n=== 完了 ===")
        print("取得件数：{}件".format(len(all_shop_data)))
        print("ファイル名： 1-1.csv")
    else:
        print("データが取得できませんでした")