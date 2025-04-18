from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
import requests
import json

def login_page(request):
    if 'user_data' in request.session:
        return redirect('profile')
    return render(request, 'login.html')

def social_login(request, provider):
    base_url = "https://baoxian18.com/connect.php"
    params = {
        'act': 'login',
        'appid': settings.APP_ID,
        'appkey': settings.APP_KEY,
        'type': provider,
        'redirect_uri': settings.REDIRECT_URI
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if data['code'] == 0:
        return redirect(data['url'])
    return JsonResponse({'error': data['msg']})

def callback(request):
    provider = request.GET.get('type')
    code = request.GET.get('code')
    
    if not provider or not code:
        messages.error(request, 'Invalid login parameters')
        return redirect('login')
    
    base_url = "https://baoxian18.com/connect.php"
    params = {
        'act': 'callback',
        'appid': settings.APP_ID,
        'appkey': settings.APP_KEY,
        'type': provider,
        'code': code
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if data['code'] == 0:
        request.session['user_data'] = {
            'social_uid': data['social_uid'],
            'nickname': data['nickname'],
            'avatar': data['faceimg'],
            'provider': provider
        }
        return redirect('profile')
    
    messages.error(request, data['msg'])
    return redirect('login')

def profile(request):
    if 'user_data' not in request.session:
        messages.warning(request, 'Please login first')
        return redirect('login')
    
    return render(request, 'profile.html', {
        'user_data': request.session['user_data']
    })

def logout(request):
    if 'user_data' in request.session:
        del request.session['user_data']
        messages.success(request, 'Successfully logged out')
    return redirect('login')