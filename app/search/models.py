from django.db import models
from django.conf import settings
from django.utils._os import safe_join
import os
# 任意のMEDIA_ROOTを作成。今回はimage/検索した言葉のフォルダー/ファイル名


def user_directory_path(instance, filename):
    # MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', None)  # settingsの変数を使用する方法
    return f'images/{instance.search_img_name}/{filename}'


class Search_Img(models.Model):
    """
    検索した画像をDBに保存しzipフォルダーの準備をする
    """
    search_img_good = models.ImageField(upload_to=user_directory_path)
    search_img_name = models.CharField(verbose_name='画像', max_length=75, null=True, blank=True)

    class Meta:
        verbose_name_plural = '検索した画像'

        def __str__(self):
            return self.search_img_name
