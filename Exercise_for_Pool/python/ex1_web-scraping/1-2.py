from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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

def get_shop_data(shop_url, driver):
    """1店舗のデータを取得"""
    time.sleep(3)
    try:
        driver.get(shop_url)

        # 店舗名
        try:
            name_element = driver.find_element(By.CLASS_NAME, "shop-info__name")
            name = name_element.text.strip()
        except:
            try:
                name_element = driver.find_element(By.CLASS_NAME, 'contact-term')
                name = name_element.text.strip()
            except:
                name = ""

        # 電話番号
        try:
            phone_element = driver.find_element(By.CLASS_NAME, 'phone-guide__number')
            phone = phone_element.text.strip()
        except:
            phone = ""

        # メールアドレス（ほとんどのページにない）
        email = ""

        # 住所
        try:
            address_element = driver.find_element(By.CLASS_NAME, 'region')
            full_address = address_element.text.strip()
        except:
            full_address = ""

        # 住所を分割
        prefecture, city, street, building = split_address(full_address)

        # オフィシャルページのURL
        final_url = ""
        ssl_enabled = "FALSE"

        try:
            # オフィシャルページのリンクが表示されるまで最大10秒待つ
            wait = WebDriverWait(driver,10)

            official_link = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "title")))

            official_url = official_link.get_attribute('href')
            print(official_url)

            # 新しいタブでオフィシャルページを開く
            original_window = driver.current_window_handle()
            driver.execute_script(f"window.open('{official_url}', '_blank');")
            time.sleep(3)

            # 新しいタブに切り替え
            windows = driver.window_handles
            driver.switch_to.window(windows[-1])

            # 最終的なURLを取得
            final_url = driver.current_url
            ssl_enabled = "TRUE" if final_url.startswith("https://") else "FALSE"

            # タブを閉じて元のウィンドウに戻る
            driver.close()
            driver.switch_to.window(original_window)

        except TimeoutException:
            print("オフィシャルページのリンクが見つかりませんでした（タイムアウト）")
        except Exception as e:
            print("  URL取得エラー: {}".format(e))
            final_url = ""
            ssl_enabled = "FALSE"

        return {
            '店舗名': name,
            '電話番号': phone,
            'メールアドレス': email,
            '都道府県': prefecture,
            '市区町村': city,
            '番地': street,
            '建物名': building,
            'URL': final_url,
            'SSL': ssl_enabled
        }
    except Exception as e:
        print("  店舗データ取得エラー: {}".format(e))
        return None


def main():
    # EdgeDriverのパス(msedgedriver.exeとスクリプトが同一階層にある前提)
    driver_path = "msedgedriver.exe"
    service = Service(driver_path)

    # User-Agentを設定
    options = webdriver.EdgeOptions()
    options.add_argument("user-agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 Edg/74.1.96.24")

    driver = webdriver.Edge(service=service, options=options)

    all_shop_data = []
    target_count = 50
    page = 1

    try:
        # 最初のページにアクセス
        url = "https://r.gnavi.co.jp/eki/0002922/western/rs/?r=500"
        driver.get(url)
        print("\n=== ページ{}を取得中 ===".format(page))
        time.sleep(3)

        while len(all_shop_data) < target_count:
            # 店舗リンクを抽出
            shop_links = driver.find_elements(By.CLASS_NAME, 'style_titleLink___TtTO')

            if not shop_links:
                print("店舗リンクが見つかりませんでした")
                break

            # URLを先に取得しておく（要素が古くなる問題を回避）
            shop_urls = [link.get_attribute('href') for link in shop_links]

            # 各店舗のデータを取得
            for shop_url in shop_urls:
                if len(all_shop_data) >= target_count:
                    break

                print("\n[{}/{}] 取得中: {}".format(len(all_shop_data)+1,target_count,shop_url))

                shop_data = get_shop_data(shop_url, driver)

                if shop_data and shop_data['店舗名']:
                    all_shop_data.append(shop_data)
                    print(f"  成功: {shop_data['店舗名']}")
                else:
                    print("  スキップ: データ取得失敗")

            # 次のページへ
            if len(all_shop_data) < target_count:
                # 一覧ページに戻る
                driver.get(url + f"?p={page + 1}")
                page += 1
                print(f"\n=== ページ{page}を取得中 ===")
                time.sleep(3)

        # DataFrameに変換してCSV出力
        if all_shop_data:
            df = pd.DataFrame(all_shop_data)
            df.to_csv('1-2.csv', index=False, encoding='utf-8-sig')
            print(f"\n=== 完了 ===")
            print(f"取得件数: {len(all_shop_data)}件")
            print(f"ファイル名: 1-2.csv")
        else:
            print("データが取得できませんでした")

    finally:
        driver.quit()

if __name__ == '__main__':
    main()