from django import forms
from .models import Auction_data


class Auction_DataForm(forms.Form):
    seller_name = forms.CharField(label='出品者', max_length=50)
    search_name = forms.CharField(label='検索キーワード（商品名・ブランド等）', max_length=50)

    def clean_seller_name(self):
        seller_name = self.cleaned_data.get('seller_name')
        if not isascii(seller_name):
            self.add_error('seller_name', '英文字でお願いします')
        return seller_name

# python3.6のver変更に伴っての追加（英数字だとtrun)
def isascii(s):
    """Check if the characters in string s are in ASCII, U+0-U+7F."""
    return len(s) == len(s.encode())
