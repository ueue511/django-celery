import time
import re

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import chromedriver_binary  # パスを通すためのコード
from .lotoNo_split import loto_being_elected,  loto_no_callback  # 分割の関数 　摘出する回数を返す関数
from .models import Selnium_data
from django.db.models import Q
import random


def loto_new2(loto, year, month, day, *args):
    """
    loto: loto6 or 7
    year.month,day: selectで入力された年月日
    *args
       loto_no: viewsで検索し検索日時に近い当選発表日時の抽選回
       loto_overcoat: loto_no以下の抽選回で摘出、以前調べ保存したdataの数
    :title no1～5:  '0271'(0271回）　抽選回　str
    :day ''20180629'(2018/06/29）　抽選日時　str'
    :keka_num: 　'01091516193235(14)(31)'(01 09 15 16 19 32 35 (14) (31)) 当選番号　ｓｔｒ
    :1～6等:　賞金金額
    :1～6等口:　当選数
    """
    # 初期設定
    global loto_no_first
    options = Options()

    # 必要なlistを作成
    box_list = ['year', 'month', 'day']
    input_list = [str(year), str(month), str(day)]
    tyusen_keka_all = []

    # 回数指定
    table_num = 1  # 基本の１回目を指定
    list_no = 0  # listの初めの番号を指定
    if len(args) == 2:
        table_num_list = loto_no_callback(args[1])
    else:
        table_num_list = [5, 5]

    # UAをいくつか格納しておく
    user_agent = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    ]

    # ここにuser_agentからランダムで読み込み
    options.add_argument('--user-agent=' + user_agent[random.randrange(0, len(user_agent), 1)])

    # ----headlessモード
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1200x600')
    driver = webdriver.Chrome(options=options)

    # 要素が見つかるまで3秒待つ
    driver.implicitly_wait(3)

    # urlに対して最大3秒待つように設定する
    wait = WebDriverWait(driver, 3)

    # 指定したページの読み込み
    driver.get('https://www.takarakujinet.co.jp/{}/past.html'.format(loto))

    # ラジオボックスが出るまで待機
    wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "box01")))

    # ----if文　新規以外　抽選回数を入力
    if len(args) >= 1:
        # チェックボタンの要素を摘出
        element = driver.find_element_by_xpath('/html/body/section/article[1]/div[3]/p[2]/input[1]')
        # クリック
        element.click()
        # 抽選回数を入力
        element = driver.find_element_by_id('round')
        element.send_keys(int(args[0])-1)

    # ---- 新規　年月日を入力
    else:
        for as_of_day, input_as_of_day in zip(box_list, input_list):
            # year month day と順番に数値を入力
            element = driver.find_element_by_id(as_of_day)
            # セレクトタグの要素を指定してSelectクラスのインスタンスを作成
            select = Select(element)
            # セレクトタブのオプションに入力
            select.select_by_visible_text(input_as_of_day)

    time.sleep(1)
    element = driver.find_element_by_id('search-button')
    element.click()
    time.sleep(1)

    # ページネーションを摘出
    try:
        element_next = driver.find_element_by_id('next')
    except NoSuchElementException:
        pass

    # スクレイピング開始
    while table_num <= table_num_list[list_no]:
        tyusen_keka = {}
        element_list = driver.find_element_by_xpath(f'//*[@id="past-result"]/table[{table_num}]/tbody')

        # titleを摘出　'027120180629'(読み0271回2018年06月29日）　loto_no(0271) day(20180629)にstr型加工
        element_title = element_list.find_element_by_class_name('title')
        element_title_ok = re.sub('[第回の抽せん結果年月日（）]', '', element_title.text)
        tyusen_keka['loto_no'], tyusen_keka['day'] = element_title_ok[:4], element_title_ok[4:]
        # 分割関数を使用
        # tyusen_keka['title no'] = loto_being_elected_day(element_title_ok)

        # 抽選数字を摘出 '01091516193235(14)(31)'(01 09 15 16 19 32 35 (14) (31))にstr型に加工
        element_num = element_list.find_element_by_class_name('lotnum')
        element_num_ok = element_num.text.replace('\n', '').replace(' ', '')
        # 分割関数を使用
        tyusen_keka['keka_num'] = loto_being_elected(element_num_ok)

        table_no = 4  # tabelの1～6等を摘出ために必要

        # 各等金額・口数を摘出 4～9(1等～6等)
        while table_no <= 9:
            # 共通するXpathを変数に入力
            url = f'//*[@id="past-result"]/table[{table_num}]/tbody/tr[{table_no}]'
            # 1等、2等・・・等を摘出
            element_tou = element_list.find_element_by_xpath(url + '/th')
            # 当選金額を摘出
            element_no1 = element_list.find_element_by_xpath(url + '/td[1]')
            # 口数を摘出
            element_no1_kuti = element_list.find_element_by_xpath(url + '/td[2]')
            # element_no1_ok: 金額をｓｔｒの数値変換　element_no1_kuti_ok： 口数をstrの数値に変換
            element_no1_ok = re.sub('[,円]', '', element_no1.text)
            element_no1_kuti_ok = re.sub('[,口]', '', element_no1_kuti.text)
            tyusen_keka[element_tou.text] = element_no1_ok
            tyusen_keka[element_tou.text + '口'] = element_no1_kuti_ok
            table_no += 1
        table_num += 1
        # table事にまとめたdictをlistに入れ込む
        tyusen_keka_all.append(tyusen_keka)

        # 次のページがあるか判定
        try:
            if element_next and table_num == 6 and len(table_num_list) == 2:  # #nextがあり、かつテーブルの判定が「6」の場合
                element_next.click()
                time.sleep(2)
                table_num = 1  # テーブル判定リセット
                list_no += 1
                # try:
                #     element_next = driver.find_element_by_id('next')
                # except NoSuchElementException:
                #     pass
                wait.until(expected_conditions.visibility_of_element_located((By.ID, "past-result")))
        # #nextが見つからない、押せないエラーが出たときスクレイピングのループは終了
        except NoSuchElementException:
            break
        except StaleElementReferenceException:
            break

    # print(tyusen_keka_all)
    driver.quit()

    # ---dbにデータを入れ保存 被り防止のためifを使用 del loto_overwrite_saveは変数内をリセット
    for i, tyusen_keka_one in enumerate(tyusen_keka_all):
        # 抽選日時で被り検索
        loto_overwrite_save = Selnium_data.objects.filter(loto_type__iexact=loto,
                                                          loto_no__iexact=tyusen_keka_one['loto_no']).distinct()
        # 抽選日時の被りあり、最初の抽選会はloto_firstに代入
        if len(loto_overwrite_save) > 0 and i == 0:
            loto_no_first = tyusen_keka_one['loto_no']
            del loto_overwrite_save
            continue
        # 抽選日時の被りのみ
        elif len(loto_overwrite_save) > 0:
            del loto_overwrite_save
            continue
        # 被りなし　最初の抽選日時はloto_firstに代入
        elif i == 0:
            loto_no_first = tyusen_keka_one['loto_no']
            del loto_overwrite_save
            try:
                pk = Selnium_data(
                    loto_type=loto,
                    loto_no=tyusen_keka_one['loto_no'],
                    day=tyusen_keka_one['day'],
                    num=tyusen_keka_one['keka_num'],
                    one=tyusen_keka_one['1等口'],
                    one_money=tyusen_keka_one['1等'],
                    twe=tyusen_keka_one['2等口'],
                    twe_money=tyusen_keka_one['2等'],
                    three=tyusen_keka_one['3等口'],
                    three_money=tyusen_keka_one['3等'],
                    foru=tyusen_keka_one['4等口'],
                    foru_money=tyusen_keka_one['4等'],
                    five=tyusen_keka_one['5等口'],
                    five_money=tyusen_keka_one['5等'],
                    six=tyusen_keka_one['6等口'],
                    six_money=tyusen_keka_one['6等'])
            except KeyError:
                pk = Selnium_data(
                    loto_type=loto,
                    loto_no=tyusen_keka_one['loto_no'],
                    day=tyusen_keka_one['day'],
                    num=tyusen_keka_one['keka_num'],
                    one=tyusen_keka_one['1等口'],
                    one_money=tyusen_keka_one['1等'],
                    twe=tyusen_keka_one['2等口'],
                    twe_money=tyusen_keka_one['2等'],
                    three=tyusen_keka_one['3等口'],
                    three_money=tyusen_keka_one['3等'],
                    foru=tyusen_keka_one['4等口'],
                    foru_money=tyusen_keka_one['4等'],
                    five=tyusen_keka_one['5等口'],
                    five_money=tyusen_keka_one['5等'])
            pk.save()
        # 被りなし、2回目以降の新規保存
        else:
            del loto_overwrite_save
            try:
                pk = Selnium_data(
                    loto_type=loto,
                    loto_no=tyusen_keka_one['loto_no'],
                    day=tyusen_keka_one['day'],
                    num=tyusen_keka_one['keka_num'],
                    one=tyusen_keka_one['1等口'],
                    one_money=tyusen_keka_one['1等'],
                    twe=tyusen_keka_one['2等口'],
                    twe_money=tyusen_keka_one['2等'],
                    three=tyusen_keka_one['3等口'],
                    three_money=tyusen_keka_one['3等'],
                    foru=tyusen_keka_one['4等口'],
                    foru_money=tyusen_keka_one['4等'],
                    five=tyusen_keka_one['5等口'],
                    five_money=tyusen_keka_one['5等'],
                    six=tyusen_keka_one['6等口'],
                    six_money=tyusen_keka_one['6等'])
            except KeyError:
                pk = Selnium_data(
                    loto_type=loto,
                    loto_no=tyusen_keka_one['loto_no'],
                    day=tyusen_keka_one['day'],
                    num=tyusen_keka_one['keka_num'],
                    one=tyusen_keka_one['1等口'],
                    one_money=tyusen_keka_one['1等'],
                    twe=tyusen_keka_one['2等口'],
                    twe_money=tyusen_keka_one['2等'],
                    three=tyusen_keka_one['3等口'],
                    three_money=tyusen_keka_one['3等'],
                    foru=tyusen_keka_one['4等口'],
                    foru_money=tyusen_keka_one['4等'],
                    five=tyusen_keka_one['5等口'],
                    five_money=tyusen_keka_one['5等'])
            pk.save()
    return loto_no_first  # 最初の抽選日時を戻す
