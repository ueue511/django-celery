#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# python manage.py makemigrations
python manage.py flush --no-input
# python pip install pillow==6.2.1
python manage.py migrate auth
python manage.py migrate
python manage.py sass static/scss/main.scss static/css/main.css
python manage.py collectstatic --no-input --clear
# djnago admin create_superuser実行
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('yuki', '', 'yx8qg6f5')"
# celery -A test_any worker --loglevel=info

exec "$@"
