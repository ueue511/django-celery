from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .tasks import bing_search
from django.views.generic import FormView
from .forms import Search_Form, Search_Choice
from django.db.models import Q
from .models import Search_Img
import json
from django.http import HttpResponse, JsonResponse
import zipfile
import urllib.parse
import shutil


# Create your views here.


class Search_data(LoginRequiredMixin, FormView):
    form_class = Search_Form
    template_name = 'keka5.html'

    def post(self, request, *args, **kwargs):
        choice = []
        search_name = request.POST.get('search_name')
        search_name = str(search_name)

        # もしdbに同じキーワードがある場合、検索せずにファイルを表示
        if Search_Img.objects.filter(search_img_name=search_name).exists():
            # search_img_name(フォルダー名）をlist型で摘出 'distinct'は重複したものは取り出さないようにする
            search_list = Search_Img.objects.all().values_list('search_img_name', flat=True).order_by(
                'search_img_name').filter(search_img_name__startswith=search_name).distinct()
            for search_list_one in search_list:
                choice.append((search_list_one, search_list_one))
            form = Search_Choice(choice)
            context = {
                'search_list': search_list,
                'form': self.form_class,
                'form_choice': form
                }

            return render(request, 'keka5.html', context)
        print('stop')
        # if not search_all db検索語　空の場合
        Error_No = bing_search.delay(search_name)
        messages_in = "登録内容を受け付けました"
        f = self.form_class({'search_name': search_name})

        return render(request, 'progress_search.html', {'form': f, 'task_id': Error_No.task_id, 'message': messages_in})
        # -----
        # search_all = Search_Img.objects.all
        # # search_img_name(フォルダー名）をlist型で摘出 'distinct'は重複したものは取り出さないようにする
        # search_list = Search_Img.objects.all().values_list('search_img_name', flat=True).order_by('search_img_name').distinct()
        # for search_list_one in search_list:
        #     choice.append((search_list_one, search_list_one))
        # form = Search_Choice(choice)
        # context = {
        #     'search_list': search_list,
        #     'search_all': search_all,
        #     'form': self.form_class,
        #     'form_choice': form
        # }
        #
        # return render(request, 'progress_search', context)
        # ----


    # def post(self, request, *args, **kwargs):
    #     choice = []
    #     search_name = request.POST.get('search_name')
    #     search_name = str(search_name)
    #     bing_search.delay(search_name)
    #     search_all = Search_Img.objects.all
    #     # search_img_name(フォルダー名）をlist型で摘出 'distinct'は重複したものは取り出さないようにする
    #     search_list = Search_Img.objects.all().values_list('search_img_name', flat=True).order_by('search_img_name').distinct()
    #     for search_list_one in search_list:
    #         choice.append((search_list_one, search_list_one))
    #     form = Search_Choice(choice)
    #     context = {
    #         'search_list': search_list,
    #         'search_all': search_all,
    #         'form': self.form_class,
    #         'form_choice': form
    #     }
    #
    #     return render(request, self.template_name, context)


@login_required
def download_zip(request):
    if request.method == 'POST':
        one_select = request.POST.get('one')
        # file名を作成
        test_filename = one_select
        quoted_filename = urllib.parse.quote(test_filename)
        # selectで受け取ったvalueで検索 reverse()は重複はなし設定
        upload_files = Search_Img.objects.filter(search_img_name=str(one_select)).order_by('search_img_good').reverse()
        # zipファイル作成準備
        response = HttpResponse(content_type='application/zip')
        file_zip = zipfile.ZipFile(response, 'w')
        for upload_file in upload_files:
            file_zip.writestr(upload_file.search_img_good.name, upload_file.search_img_good.read())

        # Content-Dispositionでダウンロードの強制
        response['Content-Disposition'] = "attachment; filename='{}.zip'; filename*=UTF-8''{}.zip".format(quoted_filename, quoted_filename)

        return response
