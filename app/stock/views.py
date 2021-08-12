from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from .forms import Stock_DataForm
from .stock_search import stock_price, stock_chart
from .models import Stock_Code
import re
from django.db.models import Q
from django.http import HttpResponse
import json
import pandas as pd
import numpy as np
from plotly.offline import plot


# Create your views here.
class Stock_Dataview(LoginRequiredMixin, FormView):
    form_class = Stock_DataForm
    template_name = 'keka4.html'

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = Stock_DataForm(request.POST)
            if form.is_valid():
                stock_code = form.cleaned_data['stock_code']
                stock_code = int(stock_code)
                # dbに被りがないか判定 ない場合は実行
                data = Stock_Code.objects.filter(stock_code=stock_code)
                if not data:
                    a = stock_price(stock_code)
                    # 該当する場合、stock_price関数は「0」を返すのでif文で判定
                    if a == 0:
                        chick_error = '該当する企業がありません。企業コードを確認の上、再度入力して下さい。'
                        return render(request, self.template_name,
                                      {'form': self.form_class, 'chick_error': chick_error})
                code_all = Stock_Code.objects.all()
                return render(request, self.template_name, {'form': self.form_class, 'code_all': code_all})

            else:
                return render(request, self.template_name,
                              {'form': form})


@login_required
def Stock_Dataview_test(request):
    if request.method == 'POST':
        code_year_dict = {}
        datal = request.POST.get('stock_code')
        # ajaxで送られたコードを元に年度を取り出す
        code_year = Stock_Code.objects.filter(stock_code=datal).order_by('stock_year').reverse()
        # 取り出したクエリセットをlistに変換
        for a in code_year:
            code_year_one = a.stock_year
            code_year_all = re.sub("[!-/:-@[-`{-~]", '', code_year_one)
            code_year_list = code_year_all.split()
        # jquery用に辞書に変換
        for x, y in enumerate(code_year_list):
            code_year_dict[x] = y
        # jsonファイルに変換
        code_year_dict = json.dumps(code_year_dict)
        # print(code_year_dict)
        return HttpResponse(code_year_dict, content_type='application/json')


@login_required
def Stock_chart_test(request):
    if request.method == 'POST':
        code = request.POST.get('stock_code')
        year = request.POST.get('stock_year')
        stock_name = Stock_Code.objects.filter(stock_code=code).order_by('stock_name')
        for a in stock_name:
            stock_name = str(a.stock_name)

        plotly_chart = stock_chart(code, year, stock_name)

        return HttpResponse(plotly_chart)
