from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from .test_map import Map_App, get_name, gurunavi_app
import json

# Create your views here.


class Make_Map(LoginRequiredMixin, TemplateView):
    template_name = 'keka6.html'


@login_required
def make_map_post(request):
    if request.method == 'POST':
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        print(lat, lng)
        map_data = gurunavi_app(lat, lng)
        read_data = json.loads(map_data)["rest"]
        name_all = get_name(read_data)
        name_all_json = json.dumps(name_all)
        return HttpResponse(name_all_json, content_type='application/json')
