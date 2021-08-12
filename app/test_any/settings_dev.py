from .settings_common import *

DEBUG = False

# emailのテスト用設定
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ALLOWED_HOSTS = [os.environ.get('DJANGO_ALLOWED_HOSTS')]

# 静的ファイルを配置する場所
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT =  os.path.join(BASE_DIR, 'mediafiles')

AWS_SES_ACCESS_KEY_ID = os.environ.get('AWS_SES_ACCESS_KEY_ID')
AWS_SES_SECRET_ACCESS_KEY = os.environ.get('AWS_SES_SECRET_ACCESS_KEY')
EMAIL_BACKEND = 'django_ses.SESBackend'

# ロギンス設定
LOGGING = {
    'version': 1,  # 1固定
    'disable_existing_loggers': False,

    # ロガー設定
    'loggers': {
        # djangoが利用するロガー
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        # homeアプリケーションが利用するロガー
        'home': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
    # ハンドラの設定
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'dev'
        },
    },

    # フォーマッタの設定
    'formatters': {
        'dev': {
            'format': '\t'. join([
                '%(asctime)s',
                '[%(levelname)s]',
                '%(pathname)s(Line:%(lineno)d)',
                '%(message)s'
            ])
        },
    }
}
