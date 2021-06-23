from django.shortcuts import render
from django.views.generic import FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .tasks import auction
from .forms import Auction_DataForm
from .models import Auction_data, Photo_Goods
from django.db.models import Q
from celery.result import AsyncResult
from celery_progress.backend import ProgressRecorder
from django.contrib import messages
import time
import json

# Create your views here.
"""
seller_name = 検索するアカウント名
search_name = 検索する　ブランド・商品名など
data = スクレイピング後にseller_nameとsearch_nameに該当するセル
data2 = 取り出したセルに該当するimg_files
template_no = progress.htmlに渡す際のtemplate.html
"""


class Auction_Dataview(LoginRequiredMixin, ListView, FormView):
    form_class = Auction_DataForm
    model = Auction_data
    template_name = 'keka3.html'

    def post(self, request, *args, **kwargs):
        # data2の初期化
        data2 = []

        form = Auction_DataForm(request.POST)
        if form.is_valid():
            seller_name = form.cleaned_data['seller_name']
            search_name = form.cleaned_data['search_name']

            search_name = search_name.split()

            # 取り出したform_dataを大小関係なくdb検索　「Q」はｏｒ検索で使用するらしい
            data = Auction_data.objects.filter(Q(seller_name__iexact=seller_name)).distinct()

            data_one = data.filter(Q(search_name__in=[search_name]))

            if not data_one:
                try:
                    # jsonファイルを作成するため辞書を準備
                    # search_file = {'file': {'seller_name': seller_name,
                    #                'search_name': search_name}
                    #                }
                    # search_file_j = json.dumps(search_file)
                    # selenium 実行
                    # Error_No = auction(seller_name, search_name)
                    Error_No = auction.delay(seller_name, search_name)
                    result = AsyncResult(Error_No)
                    if result:
                        messages_in = "登録内容を受け付けました"
                        # form入力を更新しても引き継ぐ
                        f = self.form_class({'seller_name': seller_name, 'search_name': ' '.join(search_name)})
                        # プログレスバーのtask_idを取り出す
                        # task_id = Error_No.task_id
                        return render(request, 'progress.html', {'form': f, 'task_id': Error_No.task_id, 'message': messages_in})


                    if Error_No == 1:
                        chick_error = 'そのような出品者は見当たりませんでした。'
                        f = self.form_class({'seller_name': seller_name, 'search_name': ' '.join(search_name)})
                        return render(request, self.template_name,
                                      {'form': f, 'chick_error': chick_error})
                    elif Error_No == 2:
                        chick_error = '出品者がその商品名に該当する商品を出品していません'
                        f = self.form_class({'seller_name': seller_name, 'search_name': ' '.join(search_name)})
                        return render(request, self.template_name,
                                      {'form': f, 'chick_error': chick_error})

                    # スクレイピング後にseller_nameとsearch_nameに該当するセルの検索
                    data = Auction_data.objects.filter(Q(seller_name__iexact=seller_name)).distinct()
                    data_one = data.filter(Q(search_name__in=[search_name]))


                    # data == 0（何も検出されなかった場合）の処理
                    if not data:
                        chick_error = '商品名に該当がございません。'
                        f = self.form_class({'seller_name': seller_name, 'search_name': ' '.join(search_name)})
                        return render(request, self.template_name,
                                      {'form': f, 'chick_error': chick_error})

                    # 該当するセルに関係する画像を検索。ｌｉｓｔとして変数に代入
                    for data_sell in data_one:
                        data2_one = Photo_Goods.objects.filter(img_seller__iexact=data_sell.shop_good)
                        data2.append(data2_one)

                    # templateにzipとして渡す
                    data_all = zip(data_one, data2)

                    return render(request, self.template_name,
                                  {'data': data_all, 'form': self.form_class})
                except NameError:
                    error_text = '検出されませんでした'
                    f = self.form_class({'seller_name': seller_name, 'search_name': ' '.join(search_name)})
                    return render(request, self.template_name, {'form': f,
                                                                'error_text': error_text})

            else:
                # data = Auction_data.objects.filter(Q(seller_name__iexact=seller_name))
                # data = [data.filter(Q(search_name__iexact=search_name_one)).distinct()
                #         for search_name_one in search_name]

                for data_sell in data_one:
                    data2_one = Photo_Goods.objects.filter(img_seller__iexact=data_sell.shop_good)
                    data2.append(data2_one)

                data_all = zip(data_one, data2)

                f = self.form_class({'seller_name': seller_name, 'search_name': ' '.join(search_name)})
                return render(request, self.template_name,
                              {'data': data_all, 'form': f})
        else:

            return render(request, self.template_name,
                          {'form': form})


# # プログレスバー進捗の関数
# def get_progress(request, task_id):
#     result = AsyncResult(task_id)
#     response_data = {
#         'state': result.state,
#         'details': result.info,
#     }
#     return HttpResponse(json.dump(response_data), content_type='application/json')

