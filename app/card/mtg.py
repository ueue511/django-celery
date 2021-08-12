import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

import requests
from .models import Image_Fiel
from django.core.files import File
from django.core.files.base import ContentFile
import io
from PIL import Image
import urllib.request
import os
import random


def mtg_card():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get('https://mtg-jp.com/products/card-gallery/0000064/')

    time.sleep(5)

    a = 0
    # find_element_by_xpathでクラスのカードを摘出
    all_url = driver.find_elements_by_xpath('//*[@id="contents"]/section/div/div/\
    ul/li/a/figure/img')

    # 初期のpath設定
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # pathの作成
    # os_path = os.path.join(BASE_DIR, 'media')

    # 回数制限の変数
    limit = 0

    for url in all_url:
        if limit <= 5:
            limit += 1
            # 対象の画像にスクロールする
            taget = url
            actions = ActionChains(driver)
            actions.move_to_element(taget)
            actions.perform()
            time.sleep(1)

            # src属性(画像)を摘出
            src = url.get_attribute('src')

            # alt属性（画像名前）を摘出
            card_name = url.get_attribute('alt')
            # 機械的にならないようにrandomで乱数待ちにしてみる
            y = random.randrange(3, 5)

            if y <= 4:
                a += 1
            else:
                x = random.randrange(10, 25)
                time.sleep(x)
                a = 0

            # 画像をダウンロード
            card = urllib.request.urlopen(src).read()

            time.sleep(random.randrange(3, 10))

            # test
            # url = 'http://127.0.0.1:8000/home/top/card/'
            # file = {str(name): card}
            # requests.post(url, files=file)

            # 摘出した画像名前で保存

            # upload_file = forms.cleaned_data[card]
            # default_storage.save('{}.jpg'.format(str(name)), upload_file)

            # with open(os_path + '\\images\\{}.jpg'.format(str(card_name)), "wb") as f:
            #     f.write(card)

            # django imagefieldにpathを保存
            image = Image_Fiel()
            new_file = File(
                file=card,
                name=str(card_name),
                )
            image.picture.save(new_file.name + '.jpg', ContentFile(new_file.file))

    print('---get downlord---')

    time.sleep(1)

    driver.quit()
