

def loto_being_elected_day(day):
    """
    strの配列で抽選番号と年月日を入れる
    '027120180629' →　0271 2018 0629
    """
    chunks, chunk_size = len(day), len(day) // 3  #
    loto_day = [day[i:i + chunk_size] for i in range(0, chunks, chunk_size)]
    loto_day = ' '.join(loto_day)
    return loto_day



def loto_being_elected(mouth):
    """
    strの配列で当選番号の連番を入れる
    "01091516193235(14)(31)"　→　01 09 15 16 19 32 35 (14) (31)
    """
    mouth_sabun = []
    mouth_sabun_all = []
    mouth_sabun.append(mouth[0:14])  # 1～15文字まで摘出
    mouth_sabun.append(mouth[14:22])  # 15～22文字まで摘出
    for mouth_sabun_one in mouth_sabun:
        if len(mouth_sabun_one) == 14:
            division_mouth = 7  # 7個に分割
        elif len(mouth_sabun_one) == 8:
            division_mouth = 2  # 2個に分割
        else:
            division_mouth = 1  # 分裂なし

        # ----分割処理
        chunks, chunk_size = len(mouth_sabun_one), len(mouth_sabun_one)//division_mouth
        mouth_list = [mouth_sabun_one[i:i+chunk_size] for i in range(0, chunks, chunk_size)]
        # ----ここまで

        # 2つのlistを mouth_sabun_allにまとめる
        mouth_sabun_all.extend(mouth_list)
    mouth_sabun_all = ' '.join(mouth_sabun_all)
    return mouth_sabun_all


def loto_being_elected_day_half(day):
    """
    20180629を 2018 06 29（ｓｔｒ）に分割
    """
    half = len(day) // 2
    year, month, make_day = day[:half], day[half:half + 2], day[half + 2:]
    make_day_ok = year + '/' + month + '/' + make_day
    return make_day_ok


def days(month, year):
    """
    :month: 選択した月 （28　29　30　31判定）
    :year: 選択した年（うるう年判定）
    :return: 月で判定した日数を返す
    """
    month = int(month)
    year = int(year)
    loto_days = {}
    num = 0
    day = 1
    # 28日
    if month == 2 and year % 4 != 0:
        while day <= 28:
            loto_days[num] = day
            num += 1
            day += 1
        return loto_days
    # 29日
    elif year % 2 == 0 and month == 2:
        while day <= 29:
            loto_days[num] = day
            num += 1
            day += 1
        return loto_days
    # 7月以前の31日
    elif month < 8 and month % 2 != 0:
        while day <= 31:
            loto_days[num] = day
            num += 1
            day += 1
        return loto_days
    # 8月以降31日
    elif month > 7 and month % 2 == 0:
        while day <= 31:
            loto_days[num] = day
            num += 1
            day += 1
        return loto_days
    # それ以外
    else:
        while day <= 30:
            loto_days[num] = day
            num += 1
            day += 1
        return loto_days


def loto_no_callback(len_re):
    repetition = []
    if len_re < 5:
        repetition.append(5)
        len_re_small = 5 - int(len_re)
        repetition.append(len_re_small)
        return repetition
    elif len_re == 5:
        repetition.append(len_re)
        return repetition
    elif len_re > 5:
        len_re_big = 10 - int(len_re)
        repetition.append(len_re_big)
        return repetition
