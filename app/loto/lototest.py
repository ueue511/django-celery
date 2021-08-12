# Create your tasks here
from __future__ import absolute_import, unicode_literals

from abc import ABC
from celery import shared_task  # celeryのimport
from celery_progress.backend import ProgressRecorder  # プログレスバーの進捗

import psycopg2
import time
import sys
from selenium import webdriver
import os
from .models import Selnium_data
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import chromedriver_binary
import sqlite3



def loto6():
    # headlessの設定
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.takarakujinet.co.jp/loto6/index2.html')

    # 要素が見つかるまで3秒待つ
    driver.implicitly_wait(3)

    # 各辞書の作成/初期化
    tyusen_day = []  # 抽選日
    tyusen_num = []  # 当選番号
    tyusen_kaisu = 1500  # 継続判定で使用

    # dbに存在するデータがあるか判定のために使用
    # https://dot-blog.jp/news/django-queryset-values-list/

    data_id = Selnium_data.objects.values_list('id', flat=True)
    data_id = list(data_id)

    # 　postgreSQLに接続
    conn = psycopg2.connect(
        host='localhost',
        database='selnium_data',
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
    )

    cur = conn.cursor()

    # conn = sqlite3.connect("/Users/ueue/django/test/test1/db.sqlite3")
    # cur = conn.cursor()
    # cur.execute("CREATE TABLE products(day INTEGER, num INTEGER, one INTEGER, one_money INTEGER,"
    #             "twe INTEGER, twe_money INTEGER,"
    #             "three INTEGER, three_money INTEGER,"
    #             "foru INTEGER, foru_money INTEGER,"
    #             "five INTEGER, five_money INTEGER)")

    # 全スクレイピング開始　while文で抽選回を判定と使い回していく
    while tyusen_kaisu >= 1400:

        # 抽選日のスクライピング開始
        keka_text = driver.find_elements_by_xpath(
            '//*[@id="contents2"]/div/table/tbody/tr/td[1]')

        # id="contents2"のtableにある全テキストを変数に代入
        keka_days = [x.text for x in keka_text]

        # kera_days内にある'第'から始まる文字列を検索
        # for s in keka_days:
        #    if '第' in s:
        #        day = s
        day = [s for s in keka_days if '第' in s]

        # 不要な文字（今回は'\n'を空白）に変改しリストtyusen_dayに追加
        for one_day in day:
            year_one_day = one_day.replace('\n', '  ')
            tyusen_day.append(year_one_day)

        # 抽選日から抽選回をtyusen_day_listから摘出
        first_tyusen_day = tyusen_day[0]

        # インデックスで”14××”とint型で指定
        tyusen_kaisu = int(first_tyusen_day[1:5])

        # 抽選回を摘出
        tyusen_kaisu_all = [int(kai[1:5]) for kai in tyusen_day]

        #  1等の賞金を摘出
        tyusen_kingaku_no1 = [s for s in keka_days if ('円' in s) or ('該当なし' in s)]

        # 当選番号スクライピング開始
        for keka_text in driver.find_elements_by_xpath('//*[@class="lotnum"]'):
            # keka_text_line=[]
            # for line in keka_text.text:
            # lines.append(line.strip)って意味
            # 取り出した抽選番号をkeka_text_line[]のリスト内に入れてます。
            # 参考url:https://qiita.com/poorko/items/9140c75415d748633a10

            keka_text_line = [line.strip() for line in keka_text.text.splitlines()]

            # for n in keka_text_line:
            #    tyusen_num = ' '.join(str(n))
            # 当選番号strに変換し、joinで空白区切りで並べリストtyusen_numに追加
            # 参考url:https://note.nkmk.me/python-string-concat
            nums = ' '.join([str(n) for n in keka_text_line])
            tyusen_num.append(nums)

        # 1等の当たる（口数）をスクライピング
        keka_kutis_one = driver.find_elements_by_xpath(
            '//*[@id="contents2"]/div/table/tbody/tr/td[3]')

        # /tr/td[3]の全テキストをtyusen_kutiリストに入れる
        tyusen_kuti_1 = [x.text for x in keka_kutis_one]

        # 2等の当たり（口数）をスクライピング
        keka_kutis_twe = driver.find_elements_by_xpath(
            '//*[@id="contents2"]/div/table/tbody/tr/td[4]')
        tyusen_kuti_2 = [x.text for x in keka_kutis_twe]

        # 2等の賞金を検出
        keka_syoukins_twe = driver.find_elements_by_xpath(
            '//*[@id="contents2"]/div/table/tbody/tr/td[2]')
        keka_syoukin_twe = [x.text for x in keka_syoukins_twe]
        tyusen_kingaku_no2 = [s for s in keka_syoukin_twe \
                              if ('円' in s) or ('該当なし' in s)]

        # 3等の当たり（口数）を検出
        keka_kutis_three = driver.find_elements_by_xpath(
            '//*[@id="contents2"]/div/table/tbody/tr/td[5]')

        tyusen_kuti_3 = [x.text for x in keka_kutis_three]

        # 3等の賞金を検出
        tyusen_kingaku_no3 = [s for s in tyusen_kuti_1 if "円" in s]

        # 4等の当たり（口数）を検出
        keka_kutis_four = driver.find_elements_by_xpath(
            '//*[@id="contents2"]/div/table/tbody/tr/td[6]')
        tyusen_kuti_4 = [x.text for x in keka_kutis_four]

        # 4等の賞金を検出
        tyusen_kingaku_no4 = [s for s in tyusen_kuti_2 if '円' in s]

        # 5等の当たり（口数）を検出
        keka_kutis_five = driver.find_elements_by_xpath(
            '//*[@id="contents2"]/div/table/tbody/tr/td[7]')
        tyusen_kuti_5 = [x.text for x in keka_kutis_five]

        # 5等の賞金を検出
        tyusen_kingaku_no5 = [s for s in tyusen_kuti_3 if '円' in s]

        for kaisu, day, num, one, one_money, twe, twe_money, three, three_money, \
            foru, foru_money, five, five_money \
                in zip(tyusen_kaisu_all, tyusen_day, tyusen_num,
                       tyusen_kuti_1[0::2], tyusen_kingaku_no1,
                       tyusen_kuti_2[0::2], tyusen_kingaku_no2[0::2],
                       tyusen_kuti_3[0::2], tyusen_kingaku_no3,
                       tyusen_kuti_4, tyusen_kingaku_no4,
                       tyusen_kuti_5, tyusen_kingaku_no5):
            # item = (day, num, one, one_money, twe, twe_money, three, three_money,\
            #         foru, foru_money, five, five_money)

            # print(item)
            if kaisu not in data_id:
                insert = "INSERT INTO loto_selnium_data VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cur.execute(insert, (kaisu, day, num, one, one_money, twe, twe_money, three, three_money,
                                     foru, foru_money, five, five_money))
        tyusen_kaisu = 1200

        # 抽選回数判定
        #    if len(tyusen_num) == 100:

        # ラジオボタン'回号'をクリック
        '''
        driver.find_element_by_xpath('//*[@id="kaigouRadio"]').click()
        time.sleep(3)

        # スクレイピングした最初の抽選回から-100をして入力する数値を代入
        tyusen_kaisu -= 100

        # 回号のテキストボックスに入力
        driver.find_element_by_xpath(
            '//*[@id="textfield"]').send_keys(tyusen_kaisu)
        time.sleep(3)

        # 検索ボタンをクリック
        driver.find_element_by_xpath(
            '//*[@id="contents"]/div/form/table/tbody/tr[3]/td[2]/input').click()
        time.sleep(5)

        # テキストボックス・各辞書をリセット
        driver.find_element_by_xpath(
            '//*[@id="textfield"]').clear()
        tyusen_day.clear()
        keka_days.clear()
        #        day.clear()
        tyusen_kingaku_no1.clear()
        tyusen_kingaku_no2.clear()
        tyusen_kingaku_no3.clear()
        tyusen_kingaku_no4.clear()
        tyusen_kingaku_no5.clear()
        keka_syoukin_twe.clear()
        keka_text_line.clear()
        keka_kutis_three.clear()
        tyusen_num.clear()
        tyusen_kuti_1.clear()
        tyusen_kuti_2.clear()
        tyusen_kuti_3.clear()
        tyusen_kuti_4.clear()
        tyusen_kuti_5.clear()
#    else:
        break
        '''
    print('スクレイピング終了')

    driver.quit()

    conn.commit()

    conn.close()
