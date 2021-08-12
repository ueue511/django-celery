import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from .models import Selnium_data
from .loto_new_2 import loto_new2
from .lotoNo_split import loto_being_elected_day_half  # 分割の関数
from datetime import date

import json

# Create your views here.


def days(month, year):
    """
    :month: 選択した月 （28　29　30　31判定）
    :year: 選択した年（うるう年判定）
    :return: 月で判定した日数を返す
    """
    month = int(month)
    year = int(year)
    loto_days = {}
    num = 0
    day = 1
    # 28日
    if month == 2 and year % 4 != 0:
        while day <= 28:
            loto_days[num] = day
            num += 1
            day += 1
        return loto_days
    # 29日
    elif year % 2 == 0 and month == 2:
        while day <= 29:
            loto_days[num] = day
            num += 1
            day += 1
        return loto_days
    # 7月以前の31日
    elif month < 8 and month % 2 != 0:
        while day <= 31:
            loto_days[num] = day
            num += 1
            day += 1
        return loto_days
    # 8月以降31日
    elif month > 7 and month % 2 == 0:
        while day <= 31:
            loto_days[num] = day
            num += 1
            day += 1
        return loto_days
    # それ以外
    else:
        while day <= 30:
            loto_days[num] = day
            num += 1
            day += 1
        return loto_days


class Loto_Choice(LoginRequiredMixin, TemplateView):
    template_name = 'keka.html'

    def post(self, request, *args, **kwargs):
        # 各項目をPOSTで受け取る
        loto_type_post = request.POST.get('loto_type')
        loto_year_post = request.POST.get('loto_year')
        loto_month_post = request.POST.get('loto_month')
        loto_day_post = request.POST.get('loto_day')

        # ----試験的　各postdataをdatatimeに変換
        loto_time = date(int(loto_year_post), int(loto_month_post), int(loto_day_post))

        # 入力した日付を確認
        check_error = check_days(loto_time, loto_type_post)
        if check_error:
            params = {'check_error': check_error}
            return render(request, 'keka.html', params)

        # データの年月日とpostした年月日の近い数値を判断するときに使用する　loto7=7日間隔に1回抽選 loto6=4日間隔に1回抽選
        if loto_type_post == 'loto6':
            loto_interval = 4
        else:
            loto_interval = 7

        # 検索用search_month 加工2018, 6, 10 = 20180610に加工 zfill()は0埋め　6 => 06みたいな
        search_month = loto_year_post + str(loto_month_post.zfill(2)) + str(loto_day_post.zfill(2))

        # loto7 or loto6 の　データを受け取り __lte=x x以下を取り出す(strでいけるみたい）
        data = Selnium_data.objects.filter(loto_type__iexact=loto_type_post, day__lte=search_month).order_by('-day')[:10]

        # 一番最初のdayを取り出す
        if data:
            data_day_one = data[0].day
            loto_time_file = date(int(data_day_one[:4]), int(data_day_one[4:6]), int(data_day_one[6:]))

            # 直近4日or7日を調べtrueの場合pass　felseの場合　dataを空にする
            if not (loto_time - loto_time_file).days <= loto_interval:
                data = []
        # search_month(201806)で年月での受け取り
        # data_one = data.filter(day__startswith=search_month)
        if len(data) < 10:
            if not data:
                loto_no_first = loto_new2(loto_type_post, loto_year_post, loto_month_post, loto_day_post)
                data_ten = Selnium_data.objects.all().filter(loto_type__iexact=loto_type_post,
                                                             loto_no__lte=loto_no_first).order_by('-day')[:10]
            else:
                loto_new2(loto_type_post, loto_year_post, loto_month_post, loto_day_post, data[len(data)-1].loto_no, len(data))
                data_ten = Selnium_data.objects.filter(loto_type__iexact=loto_type_post,
                                                       loto_no__lte=data[0].loto_no).order_by('-day')[:10]
            day1 = data_ten[0]
            day1 = loto_being_elected_day_half(day1.day)
            day2 = data_ten[9]
            day2 = loto_being_elected_day_half(day2.day)
            params = {'data': data_ten, 'day1': day1, 'day2': day2, 'loto_type': loto_type_post}
            return render(request, 'keka.html', params)

        elif len(data) == 10:
            day1 = data[0]
            day1 = loto_being_elected_day_half(day1.day)
            day2 = data[9]
            day2 = loto_being_elected_day_half(day2.day)
            params = {'data': data, 'day1': day1, 'day2': day2, 'loto_type': loto_type_post}
            return render(request, 'keka.html', params)




@login_required()
def loto_no(request):
    if request.method == 'POST':
        loto7_year = {1: 2013,
                      2: 2014,
                      3: 2015,
                      4: 2016,
                      5: 2017,
                      6: 2018,
                      7: 2019,
                      8: 2020
                      }

        loto6_year = {1: 2000,
                      2: 2001,
                      3: 2002,
                      4: 2003,
                      5: 2004,
                      6: 2005,
                      7: 2006,
                      8: 2007,
                      9: 2008,
                      10: 2009,
                      11: 2010,
                      12: 2011,
                      13: 2012,
                      14: 2013,
                      15: 2014,
                      16: 2015,
                      17: 2016,
                      18: 2017,
                      19: 2018,
                      20: 2019,
                      21: 2020
                      }
        data_year = request.POST.get('loto_no')
        if data_year == 'loto7':
            data_year = json.dumps(loto7_year)
            return HttpResponse(data_year, content_type='application/json')
        else:
            data_year = json.dumps(loto6_year)
            return HttpResponse(data_year, content_type='application/json')


@login_required()  # dayの指定
def loto_year(request):
    if request.method == 'POST':
        data_uru = request.POST.get('loto_year')
        data_month = request.POST.get('loto_month')
        loto_days = days(data_month, data_uru)
        data_days = json.dumps(loto_days)
        return HttpResponse(data_days, content_type='application/json')


# 入力した日付をチェック
def check_days(loto_time, loto_type_post):
    if loto_time < date(2013, 6, 7) and loto_type_post == 'loto7':
        error_code = 'loto7は2013年6月7日以前の日付で検索できません。'
    elif loto_time < date(2000, 12, 7) and loto_type_post == 'loto6':
        error_code = 'loto6は2000年12月7日以前の日付で検索できません。'
    elif loto_time > date.today():
        error_code = '未来予測はできません。本日より以前の日付指定をお願いします'
    else:
        return
    return error_code


# @login_required
# def loto_data(request):
#     data = Selnium_data.objects.all()
#     if len(data) == 0:
#         loto_new2()
#         data = Selnium_data.objects.all()
#         day1 = Selnium_data.objects.first()
#         day2 = Selnium_data.objects.last()
#         params = {'data': data, 'day1': day1, 'day2': day2}
#         return render(request, 'keka.html', params)
#
#     else:
#         day1 = Selnium_data.objects.first()
#         day2 = Selnium_data.objects.last()
#         params = {'data': data, 'day1': day1, 'day2': day2}
#         return render(request, 'keka.html', params)
