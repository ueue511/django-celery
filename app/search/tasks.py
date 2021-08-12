# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task  # celeryのimport
from celery_progress.backend import ProgressRecorder  # プログレスバーの進捗

import time
import random
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .models import Search_Img
from .make_dir import content_file_name
from django.core.files import File
from django.core.files.base import ContentFile
import urllib.request
from urllib.error import HTTPError
import re
import os


@shared_task(bind=True)
def bing_search(self, tag):
    # test用のdick
    # search_test = {}

    # 進捗のプログレスバーリセット
    progress_recorder = ProgressRecorder(self)

    # seleniumのおなじない
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
    driver.implicitly_wait(3)

    # num_sheets…枚数判定　b…重なったファイルの連番
    num_sheets = 0
    # b = [1]

    # 指定のURLに移動する
    driver.get("https://www.bing.com/")

    # urlに対して最大3秒待つように設定する
    wait = WebDriverWait(driver, 3)

    # 検索テキストボックスを取得
    # element = driver.find_element_by_xpath('//*[@id="sb_form_q"]')

    # 検索ボックスが表示するまで待機
    element = wait.until(expected_conditions.visibility_of_element_located((By.ID, "sb_form_q")))

    # 検索テキストボックスに入力
    element.send_keys(tag)

    # enterキーを押してます
    element.send_keys(Keys.ENTER)

    # 指定した文字がクリック出来る状態になるまで待機
    wait.until(expected_conditions.element_to_be_clickable((By.ID, "b-scopeListItem-images")))

    # クリックする'画像'を取得
    element = driver.find_element_by_xpath('//*[@id="b-scopeListItem-images"]')

    # '画像'をクリック
    element.click()

    # 指定した文字がクリック出来る状態になるまで待機
    try:
        wait.until(expected_conditions.element_to_be_clickable((By.ID, "mmComponent_images_2")))
    except TimeoutException:
        element = driver.find_element_by_xpath('//*[@id="b-scopeListItem-images"]')
        element.click()

    # 画像データの取り出しのため、最初の画像をクリック
    element = driver.find_element_by_xpath('//*[@id="mmComponent_images_2"]/ul[1]/li[1]/div/div/a')
    element.click()

    # iframeのxpathを指定 iframe使用のhtmlでは切り替えが必要
    iframe = driver.find_element_by_xpath('//*[@id="OverlayIFrame"]')

    # driverを切り替える
    driver.switch_to.frame(iframe)

    time.sleep(2)

    # 指定した画像が出るまで待機
    wait.until(expected_conditions.visibility_of_element_located((By.ID, "mainImageWindow")))

    # 一枚目の画像だけを取り出し
    element = driver.find_element_by_xpath('//*[@id="mainImageWindow"]/div[1]/div/div/div/img')

    # 画像取り出し
    img = element.get_attribute('src')

    # はじかれる画像はpass
    try:
        pic = urllib.request.urlopen(img).read()
    except HTTPError:  # HTTPError 弾かれる画像
        pass

    # 名前摘出　名前のclassが2種類ある為、tryで書き分ける
    try:
        element_name = driver.find_element_by_css_selector('.ptitle.vid')
    except NoSuchElementException:
        element_name = driver.find_element_by_css_selector('.ptitle.novid')
    pic_name = re.sub('[!-/:-@[-`{-~] ', '', element_name.text)

    # フォルダーを作成　重複している場合番号を打つ
    # try:
    #     os.mkdir(r'C:\Users\ueue\django\selnium\selnium\media\images\{}'.format(tag))
    #     path = r'C:\Users\ueue\django\selnium\selnium\media\images\{}'.format(tag)
    #     path_one = 'images\{}'.format(tag)
    # except FileExistsError:
    #     """
    #     重複用
    #     a ... フォルダー名の後の連番判定
    #     b ... リストの最後をフォルダー番号として使用
    #     """
    #     a = 1
    #     while os.path.exists(r'C:\Users\ueue\django\selnium\selnium\media\images\{}({})'.format(tag, a)):
    #         a += 1
    #         b.append(a)
    #
    #     os.mkdir(r'C:\Users\ueue\django\selnium\selnium\media\images\{}({})'.format(tag, b[-1]))
    #     path = r'C:\Users\ueue\django\selnium\selnium\media\images\{}({})'.format(tag, b[-1])
    #
    #     #　保存用path
    #     path_one = 'images\{}({})'.format(tag, b[-1])

    # フォルダー作成
    path_name = content_file_name(tag)

    # 画像がサイト上にない場合、pass
    try:
        # with open(path + f'\{pic_name}.jpg', "wb") as f:
        #     f.write(pic)

        image = Search_Img()
        new_file = File(
            file=pic,
            name=pic_name,
        )
        image.search_img_name = path_name
        image.save()
        image.search_img_good.save(new_file.name + '.jpg', ContentFile(new_file.file))

    except OSError:
        pass

    # while文で指定枚数分、画像を回していく
    while num_sheets < 3:
        # プログレスバー実行
        progress_recorder.set_progress(num_sheets + 1, 3)

        # 次の画像に移動
        element_next_pic = driver.find_element_by_css_selector('.navReg.navRegR')
        driver.execute_script("arguments[0].click();", element_next_pic)  # 画像とクリック箇所が被る為、javascriptでクリック
        num_sheets += 1

        # 一枚目以降はこちらのxpathで取り出す
        element = driver.find_element_by_xpath('//*[@id="mainImageWindow"]/div[2]/div/div/div/img')

        # 画像取り出し
        img = element.get_attribute('src')

        # はじかれる画像はpass
        try:
            pic = urllib.request.urlopen(img).read()
        except HTTPError:  # HTTPError 弾かれる画像
            pass

        # 名前摘出　名前のclassが2種類ある為、tryで書き分ける
        try:
            element_name = driver.find_element_by_css_selector('.ptitle.vid')
        except NoSuchElementException:
            element_name = driver.find_element_by_css_selector('.ptitle.novid')

        # ファイル名を取り出した際、半角記号を取り除く（保存時エラーが出やすい為）
        pic_name = re.sub('[!-/:-@[-`{-~] ', '', element_name.text)

        # djangoでdbに保存
        image = Search_Img()
        new_file = File(
            file=pic,
            name=pic_name,
        )
        image.search_img_name = path_name
        image.save()
        image.search_img_good.save(new_file.name + '.jpg', ContentFile(new_file.file))
        # 画像がサイト上にない場合、pass
        # try:
        #     with open(path + f'\{pic_name}.jpg', "wb") as f:
        #         f.write(pic)
        # except OSError:
        #     pass
    driver.quit()
    return tag
