from requests_html import HTMLSession
import re
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from .models import Stock_Code
from plotly.offline import plot
from django.conf import settings


def stock_price(price):
    """
    price… stock_code (HP上入力された値）
    stock_code… 企業コード （sqlの項目）
    stock_year… 上場から数えた年度 （sqlの項目）
    all_year… 年度のリスト (sql　stock_yearに入れるリスト)
    """
    try:
        session = HTMLSession()
        # ホーム画面に移動
        r = session.get('https://kabuoji3.com/stock/{}/'.format(price))
        # xpathで年度のボタンを摘出
        tox = r.html.xpath('//*[@id="base_box"]/div/ul/li/a')
        # 会社名の習得
        tox_name = r.html.find('.jp', first=True)
        # 不要な文字を削除
        tox_name = re.sub('[0-9 ]', '', tox_name.text)
        # http//***とテキストに変換後listに格納
        tox_links = [tox_one.attrs['href'] for tox_one in tox]

        # 企業コードがない場合　returnで返す
        if 0 == len(tox_links):
            return price - price

        # 初めの年数は直近300日なので除外
        all_year = []
        for tox_link in tox_links[1:]:
            res = session.get(tox_link)
            # res.html.render()
            # form_dataを指定　requestsではPOSTにて疑似クリックを促す
            data = {
                "code": price,
                "year": tox_link[-5:-1],
                "csv": ""
            }
            res_one = res.session.post('https://kabuoji3.com/stock/download.php', data=data)
            res_one_dll = res_one.session.post('https://kabuoji3.com/stock/file.php', data=data)
            contentDisposition = res_one_dll.headers['Content-Disposition']
            # attachment; filename="1234_2019.csv" → 1234_2019に変換
            fileName = re.sub('[a-z;=". ]', '', contentDisposition)
            with open(settings.MEDIA_ROOT + '/images/{}.csv'.format(fileName), 'wb') as f:
                f.write(res_one_dll.content)
            # 年度のリスト作成
            all_year.append(int(tox_link[-5:-1]))
        # dbに保存
        pk = Stock_Code(stock_code=price,
                        stock_name=tox_name,
                        stock_year=all_year)
        pk.save()

    except KeyError:
        return price - price


def stock_chart(code, year, stock_name):
    """　
    pandas使用
    日付　始値　高値　安値　終値　出来高　終値調整値
    """
    # stock_price()
    df = pd.read_csv(settings.MEDIA_ROOT + f"/images/{code}_{year}.csv", encoding="shift_jis")

    # ヘッダー行を削除して最初の行をヘッダー行にする
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header

    # indexが「日付」になっているので０からの連番に戻す
    df.reset_index(inplace=True)

    # index全体の名前を消す
    df.index.name = ''

    # columns全体の名前を消す
    df.columns.name = ''

    # 日付のcolumnsがindexになっているので日付に変更
    df.rename(columns={'index': '日付'}, inplace=True)

    # 日付をdatetimeに変更
    df['日付'] = [datetime.strptime(i, '%Y-%m-%d') for i in df['日付']]

    # indexを日付columnsに指定
    df.set_index('日付', inplace=True)

    # columns内の文字を数値に変更する
    df = df.astype(float)

    # ローソクチャートを表示
    df.reset_index(inplace=True)
    df = df.drop(['終値調整値'], axis=1)

    # print(df.head())
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']

    x = np.arange(len(df['date']))

    interval = 20
    vals = [df.index[i * interval] for i in range(len(df) // interval + 1)]
    labels = [df.loc[i * interval, 'date'] for i in range(len(df) // interval + 1)]

    fig = go.Figure(
        data=[go.Candlestick(
            name='ローソク足',
            x=x,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            hovertext=['date:{}<br>open:{}<br>high:{}<br>low:{}<br>close:{}'.format(
                df.loc[i, 'date'], df.loc[i, 'open'], df.loc[i, 'high'], df.loc[i, 'low'],
                df.loc[i, 'close'])
                for i in range(len(df))],
            hoverinfo='text',
            increasing_line_color='red',
            # increasing_fillcolor='red',
            increasing_line_width=1,
            decreasing_line_color='blue',
            # decreasing_fillcolor='blue',
            decreasing_line_width=1),
            go.Bar(name='出来高',
                   x=x,
                   y=df['volume'],
                   yaxis='y2',
                   marker={'color': '#979797'},
                   )
        ],

        layout=go.Layout(
            height=600,
            autosize=True,  # サイズを自動で合わせる
            margin=dict(autoexpand=True),  # LegendやSidebarが被ったときに自動で余白を増やすかどうか
            # title=code + ' ' + stock_name + ' ' + year + '年 ' + '株価の変動',
            title=f'{code} {stock_name} {year}年株価の変動',
            xaxis=dict(
                title='年間の変動',
                tickvals=vals,
                ticktext=labels,
                tickangle=-45
            ),
            yaxis=dict(title='株価',
                       ),
            yaxis2=dict(title='出来高',
                        overlaying='y',
                        side='right'
                        ),
            legend=dict(
                x=1.0,
                y=1.3,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            )
        )
    )
    plot_fig = plot(fig,
                    output_type='div',
                    include_plotlyjs=False,
                    config={
                        'displayModeBar': False,
                        'modeBarButtonsToRemove': ['sendDataToCloud', 'hoverCompareCartesian']}
                    )
    return plot_fig
