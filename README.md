# Django-docker-starter

*  此專案用到 Django + gunicorn + nginx + postgres + redis + celery + docker
* 可再加上flower
* Django版本為2.2.11
### demo的API
* `/`：計算使用此頁面的次數(by redis) 和 member列表(by postgres)
* `/addmember/<name>`：建立member和其名稱 by postgres
* `/add/<int>/<int>`：執行兩數相加的任務 by celery

### 開發指令
* 更改python程式會自動重build環境
#### 重啟指令，建立新的containers
docker-compose up -d --build
* 啟動在 127.0.0.1:8000
#### 關閉指令，移除之前建立的containers
docker-compose down -v
##### 在container中下建立admin的指令
docker-compose exec web python manage.py admin
##### 查看log
docker-compose -f docker-compose.yml logs -f 
##### 建立project資料夾
sudo docker-compose run web django-admin startproject project ./app
* sudo docker-compose run web [shell命令]

### 正式環境指令
##### 重啟指令，建立新的containers
docker-compose -f docker-compose.prod.yml up -d --build
* 啟動在 127.0.0.1:1337
##### 關閉指令，移除之前建立的containers
docker-compose -f docker-compose.prod.yml down -v

##### 在container中下建立admin的指令
docker-compose exec web python manage.py admin

##### 查看log
docker-compose -f docker-compose.prod.yml logs -f 

### 參考資料
* [Testing in Django](https://docs.djangoproject.com/en/2.2/topics/testing/)
* [Attempt to write a readonly database - Django w/ SELinux error](https://stackoverflow.com/questions/21054245/attempt-to-write-a-readonly-database-django-w-selinux-error)
* [使用 supervisor 管理进程](http://liyangliang.me/posts/2015/06/using-supervisor/)
* [docker-django-celery-tutorial](https://github.com/twtrubiks/docker-django-celery-tutorial)
* [Django + Celery + Redis + Gmail 實現異步寄信](https://medium.com/@zoejoyuliao/django-celery-redis-gmail-%E5%AF%84%E4%BF%A1-375904d4224c)
* [查看 Linux TCP Port 被哪隻程式(Process)佔用](https://blog.longwin.com.tw/2013/12/linux-port-process-check-2013/)

* [Dockerizing Django with Postgres, Gunicorn, and Nginx](https://testdriven.io/dockerizing-django-with-postgres-gunicorn-and-nginx)
* 這篇文章的原始碼：[testdrivenio/django-on-docker](https://github.com/testdrivenio/django-on-docker)
* 寫得很棒，任何新的名詞都會額外解釋
