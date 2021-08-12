from django import forms
from.models import Search_Img


class Search_Form(forms.Form):
    search_name = forms.CharField(label='検索したい画像を入力', max_length=30)

# choiceFieldを動的に変更するコード


class Search_Choice(forms.Form):
    def __init__(self, tag_choice, *args, **kwargs):
        super(Search_Choice, self).__init__(*args, **kwargs)
        self.fields['one'].choices = tag_choice  # tag_choiceは、この関数だけ！！検索したキーワードを全て取り出してます
        # formのclassやidを任意で変更
        self.fields['one'].widget.attrs["class"] = "form-control"
        self.fields['one'].widget.attrs["id"] = "exampleFormControlSelect"

    one = forms.ChoiceField(choices=(), required=True, label='', initial='検索したキーワード')
