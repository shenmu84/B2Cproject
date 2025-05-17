from django.shortcuts import render

# Create your views here.
# views.py
from django.http import JsonResponse
from apps.Management.models import (DateHourBehavior, PathResult)
from django.utils import timezone
from collections import defaultdict
# 每天总计数据
def get_behavior_daily_data(request):
    records = DateHourBehavior.objects.using('uba').all().order_by('dates', 'hours')
    daily_data = defaultdict(lambda: {'pv': 0, 'cart': 0, 'fav': 0, 'buy': 0})

    for record in records:
        date_str = str(record.dates)
        daily_data[date_str]['pv'] += record.pv or 0
        daily_data[date_str]['cart'] += record.cart or 0
        daily_data[date_str]['fav'] += record.fav or 0
        daily_data[date_str]['buy'] += record.buy or 0

    sorted_dates = sorted(daily_data.keys())
    return JsonResponse({
        'xAxis': sorted_dates,
        'pv': [daily_data[d]['pv'] for d in sorted_dates],
        'cart': [daily_data[d]['cart'] for d in sorted_dates],
        'fav': [daily_data[d]['fav'] for d in sorted_dates],
        'buy': [daily_data[d]['buy'] for d in sorted_dates]
    })

# 最新一天的小时数据
def get_behavior_latest_day_data(request):
    latest_date = DateHourBehavior.objects.using('uba').latest('dates').dates
    records = DateHourBehavior.objects.using('uba').filter(dates=latest_date).order_by('hours')

    x_axis = []
    pv_data, cart_data, fav_data, buy_data = [], [], [], []

    for record in records:
        label = f"{record.hours}:00"
        x_axis.append(label)
        pv_data.append(record.pv)
        cart_data.append(record.cart)
        fav_data.append(record.fav)
        buy_data.append(record.buy)

    return JsonResponse({
        'xAxis': x_axis,
        'pv': pv_data,
        'cart': cart_data,
        'fav': fav_data,
        'buy': buy_data,
        'date': str(latest_date)
    })

def get_latest_conversion(request):
    # 获取数据库中记录的最新一天的日期
    latest_date = DateHourBehavior.objects.using('uba').order_by('-dates').values_list('dates', flat=True).first()


    # 查询该日期的所有小时记录
    records = DateHourBehavior.objects.using('uba').filter(dates=latest_date).order_by('hours')

    # 准备返回的数据结构
    hours = []
    buy_conversion = []
    cartFav_conversion = []

    for record in records:
        hour_label = f"{record.hours.zfill(2)}:00"  # 保证小时格式为 00:00
        hours.append(hour_label)

        pv = record.pv or 0
        buy_rate = (record.buy / pv * 100) if pv > 0 else 0
        cartFav_rate = (record.cart+record.fav / pv * 100) if pv > 0 else 0

        buy_conversion.append(round(buy_rate, 2))
        cartFav_conversion.append(round(cartFav_rate, 2))

    # 生成智能提示信息（以平均值为依据）
    avg_buy = sum(buy_conversion) / len(buy_conversion) if buy_conversion else 0
    avg_cart = sum(cartFav_conversion) / len(cartFav_conversion) if cartFav_conversion else 0

    suggestion = []
    if avg_buy < 5:
        suggestion.append("购买转化率较低，建议进行价格促销。")
    else:
        suggestion.append("购买转化率良好，请继续保持。")

    if avg_cart < 10:
        suggestion.append("加购和收藏转化率较低，考虑优化商品展示或促销活动。")
    else:
        suggestion.append("加购和收藏转化率良好，请继续保持。")

    return JsonResponse({
        "date":  latest_date,
        "hours": hours,
        "buyConversion": buy_conversion,
        "cartFavConversion": cartFav_conversion,
        "suggestion": suggestion
    })


# views.py
from django.http import JsonResponse
from .models import PathResult


def behaviorPath(request):
    records = PathResult.objects.using('uba').all()
    stage_labels = ['浏览了', '收藏了', '加购了', '购买了']

    color_map = {}  # 每种path_type分配一个颜色
    predefined_colors = [
        '#5470C6', '#91CC75', '#EE6666', '#73C0DE', '#FAC858',
        '#3BA272', '#FC8452', '#9A60B4', '#EA7CCC'
    ]
    color_index = 0

    links = []
    node_names = set()

    for r in records:
        if r.path_type not in color_map:
            color_map[r.path_type] = predefined_colors[color_index % len(predefined_colors)]
            color_index += 1

        color = color_map[r.path_type]
        stages = [stage_labels[i] for i, v in enumerate(r.path_type) if v == '1']
        for i in range(len(stages) - 1):
            path_label = " → ".join(stages)
            links.append({
                'source': stages[i],
                'target': stages[i + 1],
                'value': r.num,
                'lineStyle': {
                    'color': color
                },
                'pathLabel': path_label
            })
            node_names.update([stages[i], stages[i + 1]])

    nodes = [{'name': name} for name in node_names]

    return JsonResponse({
        'nodes': nodes,
        'links': links
    })
# backend/views.py
from django.http import JsonResponse

# app/views.py
from django.http import JsonResponse
from .models import RFMModel


# views.py
from django.http import JsonResponse
from .models import RFMModel

def get_rfm_data(request):
    queryset = RFMModel.objects.using('uba').all().values('user_id', 'fscore', 'rscore', 'class_field')
    data = [
        {
            "user_id": item["user_id"],
            "fscore": item["fscore"],
            "rscore": item["rscore"],
            "class": item["class_field"]
        }
        for item in queryset
    ]
    return JsonResponse({"status": "success", "data": data})
def getData(request):
    # Fetch the data from the database
    paths = PathResult.objects.using('uba').all()
    des = [path.description for path in paths]
    num = [path.num for path in paths]

    # Return data as JSON
    return JsonResponse({
        'des': des,
        'num': num
    })