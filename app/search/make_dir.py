import os
from django.conf import settings


def content_file_name(tag):
    b = [1]
    try:
        os.mkdir(settings.MEDIA_ROOT + f'/images/{tag}')
        path_one = f'/images/{tag}'
    except FileExistsError:
        """
        重複用
        a ... フォルダー名の後の連番判定
        b ... リストの最後をフォルダー番号として使用
        """
        a = 1
        while os.path.exists(settings.MEDIA_ROOT + f'/images/{tag}({a})'):
            a += 1
            b.append(a)

        os.mkdir(settings.MEDIA_ROOT + f'/images/{tag}({b[-1]})')
        path_one = f'/images/{tag}({b[-1]})'

    path_dir_name = os.path.basename(path_one)
    return path_dir_name
