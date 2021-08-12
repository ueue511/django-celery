# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task  # celeryのimport
from celery_progress.backend import ProgressRecorder  # プログレスバーの進捗

import re
import time
import json
import urllib.request

from celery import Task
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from .models import Auction_data, Photo_Goods
from django.contrib import messages
from django.core.files import File
from django.core.files.base import ContentFile
import random
import chromedriver_binary  # パスを通すためのコード


# def save_point(file_name_all):
#     for file_name in file_name_all:
#
#         pk = Auction_data(seller_name=file_name['seller_name'],
#                           search_name=file_name['search_name'],
#                           shop_good=file_name['chick_good'],
#                           price=file_name['price'],
#                           price_tax=file_name['price_tax'],
#                           bid_numder=file_name['bid_number_text'],  # textに注意
#                           goods_quantity=file_name['goods_quantity_text'],  # textに注意
#                           price_start=file_name['price_start'],
#                           auction_starttime=file_name['auction_starttime'],
#                           auction_endtime=file_name['auction_endtime'])
#         pk.save()
# 試験的に入れてみる
# class MyCalculator(Task):
#     def on_success(self, retval, task_id, args, kwargs):
#         messages.success(self.request, "登録内容を保存しました。")
#         return self.request


# @shared_task(bind=True, base=MyCalculator)
@shared_task(bind=True)
def auction(self, name, goods):
    """
    # seller_name…出品者 （検索する出品者）
    # search_name…検索商品 （検索する出品者の過去出した特定商品）
    # chick_good…複数のキーワードで割り出された商品名
    # shop_good…商品名
    # price…落札値段
    # price_tax…消費税
    # bid_numder…入札数
    # goods_quantity…出品個数
    # price_start…開始値段
    # auction_starttime…開始時間
    # auction_endtime…終了時間
    # photo_goods　オークションの写真
    # 
    # cleaned_data 入力された文字判定
    # 
    # shop_good_list 各商品のdict（詳細）が入ったlist
    # shop_good_the_details 商品の詳細
    # img_url 画像のurl 名前等
    # progress_recorder　celery_progressでの関数
    #
    """
    # dictリセット
    shop_good_list = {}
    img_url = []

    # 進捗のプログレスバーリセット
    result = 0
    progress_recorder = ProgressRecorder(self)

    # 受け取ったserach_fileを辞書に変換
    # search_file = json.load(search_file_j)

    seller_name = name  # search_file['file']['seller_name']
    search_name = goods
    # UAをいくつか格納しておく
    user_agent = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    ]
    options = Options()
    # ここにuser_agentからランダムで読み込み
    options.add_argument('--user-agent=' + user_agent[random.randrange(0, len(user_agent), 1)])

    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1200x600')
    driver = webdriver.Chrome(options=options)

    # 要素が見つかるまで3秒待つ
    driver.implicitly_wait(10)

    # urlに対して最大3秒待つように設定する
    wait = WebDriverWait(driver, 25)

    # 指定したページの読み込み
    driver.get(f"https://auctions.yahoo.co.jp/seller/{seller_name}")

    # ウインドウを最大化
    driver.maximize_window()

    # 「評価」が表示するまで待機
    wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "seller__rating")))

    # 指定された出品者の「評価」をクリック
    element = driver.find_element_by_link_text("評価")
    element.click()
    wait.until(expected_conditions.visibility_of_element_located((By.XPATH, '//*[@id="allContents"]/div[2]/p[2]'
                                                                            '/table[2]/tbody/tr/td')))

    # 落札された品物を摘出
    try:
        shop_all_goods = driver.find_elements_by_xpath("//*[@id='allContents']"
                                                       "/div[2]/p[2]/table[2]/tbody/tr/td/table/tbody/tr[2]/td/small/a")

    # 落札された品物がない場合、ストアの可能性もあり。ストアのxpathは違う
    except NoSuchElementException:
        shop_all_goods = driver.find_elements_by_xpath("/html/body/div[5]/table/tbody/tr[2]/td[2]/table/tbody/tr/td"
                                                       "/table/tbody/tr/td/p/table[2]/tbody/tr/td/table/tbody/tr[2]"
                                                       "/td/small/a")
        if not shop_all_goods:
            shop_all_goods = driver.find_elements_by_xpath("/html/body/div[5]/table/tbody/tr[2]/td/table/tbody/tr/td"
                                                           "/table/tbody/tr/td/p/table[2]/tbody/tr/td/table[5]/tbody/tr[2]"
                                                           "/td/small/a")
        # リスト内包容でのテキスト摘出
    shop_goods = [x.text for x in shop_all_goods]

    # リスト内包容でキーワードによりテキスト検索
    shop_good_keyword = [shop_good for shop_good in shop_goods for search_name_one in search_name
                         if search_name_one in shop_good]

    # テキスト検索で該当商品がない場合
    if not shop_good_keyword:
        driver.quit()
        error_no = 2
        return 'onTaskError'

    goods_no = len(shop_good_keyword)
    # list内に検索された商品の詳細を入れたdictを入れ込む
    for i_no in range(goods_no):

        wait.until(expected_conditions.visibility_of_element_located((By.LINK_TEXT, shop_good_keyword[i_no])))
        element = driver.find_element_by_link_text(shop_good_keyword[i_no])
        element.click()
        wait.until(expected_conditions.visibility_of_element_located((By.ID, 'pageTop')))

        try:
            # プログレスバー実行
            progress_recorder.set_progress(i_no + 1, goods_no)

            # 落札値段を摘出
            price_all = driver.find_element_by_xpath(
                "//*[@id='l-sub']/div[1]/ul/li[2]/div/dl/dd[@class='Price__value']")
            # price = price_all.text.replace('円', '').replace(',', '')

            # 税を摘出
            price_tax_all = driver.find_element_by_xpath("//*[@id='l-sub']/div[1]/ul/li[2]/div/dl/dd[1]/span")
            price_tax = price_tax_all.text.replace('（税込', '').replace('円）', '').replace(',', '').replace('（税', '')

            # 落札価格のみを摘出
            price = price_all.text.replace(price_tax_all.text, '').replace('円', '').replace(',', '')

            # 入札件数を摘出
            bid_number = driver.find_element_by_xpath("//*[@id='l-sub']/div[1]/ul/li[1]/div/ul/li[1]/dl/dd")
            bid_number_text = bid_number.text.replace('入札履歴', '')

            # 個数を摘出
            goods_quantity = driver.find_element_by_xpath("//*[@id='l-main']/div/div[2]/div/div/div[1]/ul/li[1]/dl/dd")
            goods_quantity_text = goods_quantity.text.replace('：', '')

            # 開始時の値段を摘出
            price_start_all = driver.find_element_by_xpath(
                "//*[@id='l-main']/div/div[2]/div/div/div[2]/ul/li[5]/dl/dd")

            price_start = price_start_all.text.replace(' 円', '').replace(',', '').replace('：', '')

            # 開始時間・終了時間を摘出
            auction_starttime_all = driver.find_element_by_xpath(
                "//*[@id='l-main']/div/div[2]/div/div/div[1]/ul/li[2]/dl/dd")

            # auction_strattime = re.sub('[月日（）時分 ]', '', auction_starttime_all.text)

            auction_starttime = auction_starttime_all.text.replace('\n', '').replace(' ', '').replace('：', '')

            auction_endtime_all = driver.find_element_by_xpath(
                "//*[@id='l-main']/div/div[2]/div/div/div[1]/ul/li[3]/dl/dd")

            # auction_endtime = re.sub('[月日（）時分カレンダーに追加\n ]', '', auction_endtime_all.text)
            auction_endtime = auction_endtime_all.text.replace('\n', '').replace(' ', '').replace('：', '')

            # dictに入れ込む
            shop_good_details = {'seller_name': seller_name, 'search_name': search_name,
                                 'shop_good': shop_good_keyword[i_no],
                                 'price': price, 'price_tax': price_tax, 'bid_numder': bid_number_text,
                                 'goods_quantity': goods_quantity_text, 'price_start': price_start,
                                 'auction_starttime': auction_starttime, 'auction_endtime': auction_endtime}
            # 本番用保存
            pk = Auction_data(seller_name=seller_name,
                              search_name=search_name,
                              shop_good=shop_good_keyword[i_no],
                              price=price,
                              price_tax=price_tax,
                              bid_numder=bid_number_text,  # textに注意
                              goods_quantity=goods_quantity_text,  # textに注意
                              price_start=price_start,
                              auction_starttime=auction_starttime,
                              auction_endtime=auction_endtime)

            pk.save()

            """
            ここから画像摘出及びｄｂ保存
            """
            # 画像を摘出
            all_imgs = driver.find_elements_by_xpath("//*[@id='l-main']/div/div[1]/div[2]/div/ul/li/a/img")
            # 画像クリック用に画像を摘出
            # click_imgs = driver.find_elements_by_xpath("//*[@id='imageinfo']/div/div[2]/div[1]"
            #                                            "/ul/li/a/img")
            # 移動用に１つ画像を摘出
            # img_move_one = driver.find_element_by_xpath("//*[@id='imageinfo']/div/div[2]/div[2]"
            #                                             "/table/tbody/tr[1]/td/img[1]")

            # 移動用に1つのファイルを取り出す

            img_move_one = all_imgs[0]
            # 画像のページまで移動（1回のみ）
            # target = img_move_one
            img_action = ActionChains(driver)
            img_action.move_to_element(img_move_one)
            img_action.perform()
            wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "ProductImage__footer")))
            # 対象の画像にスクロール
            for img in all_imgs:
                # time.sleep(2)
                img.click()
                # time.sleep(1)
                # src属性（画像） alt属性（名前）を摘出
                src = img.get_attribute('src')
                img_name = img.get_attribute('alt')
                img_name = re.sub(r'[!-/:-@-`{-~]', '', img_name)
                img_name = str(img_name)
                img_url += [src, img_name]
                time.sleep(1)
                # 新しいタブを開き画像をｄｌｌ
                driver.execute_script("window.open()")  # make new tab
                driver.switch_to.window(driver.window_handles[1])  # switch new tab
                driver.get(src)

                # 画像をダウンロード
                auction_img = urllib.request.urlopen(src).read()

                # 新しいタブを閉じる
                driver.close()
                driver.switch_to.window(driver.window_handles[0])  # switch original tab
                # djangoでのdb保存
                image = Photo_Goods()
                new_file = File(
                    file=auction_img,
                    name=str(img_name),
                )
                # pk_id = Auction_Data.objects.filter(seller_name=seller_name).values_list('id', flat=True)
                # pk_id = list(pk_id)
                # image.auction_id = pk_id[-1]

                # 本番用
                image.img_seller = shop_good_keyword[i_no]
                image.save()
                image.photo_goods.save(new_file.name + '.jpg', ContentFile(new_file.file))

                # with open(r'C:\Users\ueue\Desktop\引き継ぎ\画像\{}.jpg'.format(str(img_name)), 'wb') as f:
                #     f.write(auction_img)
            shop_good_details['image_gathering'] = img_url
            shop_good_list[str(i_no)] = shop_good_details

            time.sleep(1)
            driver.back()
            time.sleep(1)
        # 要素やページが見つからない場合、戻る
        except NoSuchElementException:
            time.sleep(1)
            driver.back()
            time.sleep(1)
    driver.quit()
    return f'出品者{seller_name}、商品名{search_name}'
