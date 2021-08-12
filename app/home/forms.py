from django import forms
from django.core.mail import EmailMessage
from django.conf import settings


class InquiryForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

    # bootstrapの設定['class'] ['placeholder']など__init__で設置している
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['class'] = ''
        self.fields['name'].widget.attrs['placeholder'] = 'Name'

        self.fields['email'].widget.attrs['class'] = ''
        self.fields['email'].widget.attrs['placeholder'] = 'Email'

        self.fields['message'].widget.attrs['class'] = 'col-12-mobile'
        self.fields['message'].widget.attrs['placeholder'] = 'Message'

        # メール送受信の設定
    def send_email(self):
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        message = self.cleaned_data['message']

        message = '送信者名： {0}\nメールアドレス：　{1}\nメッセージ：　{2}' \
            .format(name, email, message)
        from_email = 'nexnex07@gmail.com'
        to_list = [
            'nexnex07@gmail.com'
        ]
        cc_list = [
            email
        ]

        message = EmailMessage(body=message, from_email=from_email, to=to_list, cc=cc_list)
        message.send()
