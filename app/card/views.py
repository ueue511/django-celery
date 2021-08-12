from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Image_Fiel
from .mtg import mtg_card
from django.views.generic import TemplateView
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


@login_required
def card_data(request):
    """
    data1:画像データを入れ込み
　　　params:template用に変更
　　　return:結果の画像HP等
    """
    data1 = Image_Fiel.objects.all()
    if len(data1) == 0:
        mtg_card()
        data1 = Image_Fiel.objects.all()
        params = {'data1': data1, }
        return render(request, 'keka2.html', params)
    else:
        data1 = Image_Fiel.objects.all()
        params = {'data1': data1, }
        return render(request, "keka2.html", params)



# @require_POST
# @csrf_exempt
# def upload(request):
#     upload_file = request.FILES['file']
#     card_img = Image_Fiel(file=upload_file)
#     card_img.save()

# def test(request):
#     data1 = Image_Fiel.objects.all()
#     params = {'data1': data1, }
#     return render(request, "keka2.html", params)
