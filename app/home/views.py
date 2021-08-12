from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from .forms import InquiryForm
import logging
from django.urls import reverse_lazy
from django.contrib import messages

# Create your views here.
logger = logging.getLogger(__name__)


class TopView(TemplateView, FormView):
    template_name = 'index.html'
    form_class = InquiryForm
    success_url = reverse_lazy('top')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました。')
        logger.info('Home sent by {}'.format(form.cleaned_data['name']))
        return super().form_valid(form)
