from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# EdgeDriverのパス（msedgedriver.exeと同じフォルダにこのスクリプトがある前提）
try:
    driver_path = "msedgedriver.exe"
    service = Service(driver_path)

    # User-Agentを設定してブラウザを起動
    options = webdriver.EdgeOptions()
    options.add_argument("user-agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 Edg/74.1.96.24")

    # Edgeブラウザを起動
    driver = webdriver.Edge(service=service, options=options)

    # ぐるなびにアクセス
    url = "https://r.gnavi.co.jp/eki/0002922/western/rs/?r=500"
    driver.get(url)

    print("ページ１にアクセスしました")

    # アイドリングタイム
    time.sleep(3)

    # ページ１の店舗数を確認
    shop_links = driver.find_elements(By.CLASS_NAME, "style_titleLink___TtTO")
    print("ページ１の店舗数：{}".format(len(shop_links)))

    # 最初の3件を表示
    for i in range(min(3, len(shop_links))):
        link = shop_links[i]
        print("\n{}件目：".format(i+1))
        print("店舗名：{}".format(link.text))
        print("URL：{}".format(link.get_attribute("href")))

    # ページを下までスクロール（ボタンが見えるようにする）
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # アイコンを見つける
    icon = driver.find_element(By.CLASS_NAME, "style_nextIcon__Ad_pH")
    # アイコンの親要素（aタグ）を取得
    next_button = icon.find_element(By.XPATH, "..")

    print("次ページボタンを見つけました！")

    # クリック
    next_button.click()
    print("ボタンをクリックしました")

    # アイドリングタイム
    time.sleep(3)

    # ページ遷移後のURLを表示
    print("遷移後のURL：{}".format(driver.current_url))
    print("成功！次ページに遷移できました")

    time.sleep(100)

except Exception as e:
    print("エラー：{}".format(e))

finally:
    # ブラウザを閉じる
    driver.quit()
    print("\nブラウザを閉じました")