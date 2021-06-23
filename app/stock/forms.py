from django import forms


class Stock_DataForm(forms.Form):
    stock_code = forms.IntegerField(label='企業コード')

    def clean_stock_code(self):
        stock_code = self.cleaned_data.get('stock_code')
        if 1000 > stock_code or 10000 < stock_code:
            self.add_error('stock_code', '整数は4桁でお願いします')
        return stock_code
