from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from tutorial.authhelper import get_signin_url, get_token_from_code, get_access_token
from tutorial.outlookservice import get_me, get_my_messages, get_my_events, get_my_tasks
import time
import datetime
import requests

# Create your views here.

def home(request):
  redirect_uri = request.build_absolute_uri(reverse('tutorial:gettoken'))
  sign_in_url = get_signin_url(redirect_uri)
  return HttpResponse('<a href="' + sign_in_url +'">Click here to sign in and view your mail</a>')

def gettoken(request):
  auth_code = request.GET['code']
  redirect_uri = request.build_absolute_uri(reverse('tutorial:gettoken'))
  token = get_token_from_code(auth_code, redirect_uri)
  access_token = token['access_token']
  user = get_me(access_token)
  refresh_token = token['refresh_token']
  expires_in = token['expires_in']

  # expires_in is in seconds
  # Get current timestamp (seconds since Unix Epoch) and
  # add expires_in to get expiration time
  # Subtract 5 minutes to allow for clock differences
  expiration = int(time.time()) + expires_in - 300

  # Save the token in the session
  request.session['access_token'] = access_token
  request.session['refresh_token'] = refresh_token
  request.session['token_expires'] = expiration
  return HttpResponseRedirect(reverse('tutorial:mail'))

def mail(request):
    access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
  # If there is no token in the session, redirect to home
    if not access_token:
        return HttpResponseRedirect(reverse('tutorial:home'))
    else:
        messages = get_my_messages(access_token)
    #Получаем список непрочитанных писем
        i=0
        while i in range(len(messages['value'])):
            if messages['value'][i]['isRead']!=False:
                messages['value'].pop(i)
            else:
                i+=1
    #сделали список

        events = get_my_events(access_token)
        i=0
        while i<len(events['value']):
            t = events['value'][i]['start']['dateTime'][11:19]
            d = events['value'][i]['start']['dateTime'][:10]
            if d == str(datetime.date.today()):
                events['value'][i]['start']['date']=d
                events['value'][i]['start']['time']=t
                i+=1
            else:
                events['value'].pop(i)

        me = get_me(access_token)

#получаем погоду
        link_to_site = 'https://community-open-weather-map.p.rapidapi.com/weather'
        headers={
            'X-RapidAPI-Host': 'community-open-weather-map.p.rapidapi.com',
            'X-RapidAPI-Key': '5aabc22e25msh45d6df4abdd28d0p1a4479jsn10ea7369318e'
                }
        parameters = {
                'q':'Ryazan,ru',
                'units':'metric',
                }
        weather = requests.get(link_to_site, headers=headers, params=parameters)
        current_weather = weather.json()

        try:
            context = {
                    'messages': messages['value'],
                    'emails_counter': len(messages['value']),
                    'events': events['value'],
                    'events_counter': len(events['value']),
                    'user_name': me['displayName'],
                    'city_weather': current_weather['main']['temp']
                    }
            return render(request, 'tutorial/mail.html', context)
        except:
            print(messages)


"""
def events(request):
  access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
# If there is no token in the session, redirect to home
  if not access_token:
    return HttpResponseRedirect(reverse('tutorial:home'))
  else:
    events = get_my_events(access_token)

    i=0
#    print('@@@@@', datetime.date.today(), len(str(datetime.date.today())))
    while i<len(events['value']):
        t = events['value'][i]['start']['dateTime'][10:19]
        d = events['value'][i]['start']['dateTime'][:10]
        print(d, len(d))
        if d == str(datetime.date.today()):
            events['value'][i]['start']['date']=d
            events['value'][i]['start']['time']=t
            i+=1
        else:
            events['value'].pop(i)
#    print('!!!!!!!!!!!', events)
    context = { 'events': events['value'],
                'events_counter': len(events['value'])
                }

    return render(request, 'tutorial/mail.html', context)
"""
#попытка подключиться к задачам, которая пока не работает
def tasks(request):
  access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
  # If there is no token in the session, redirect to home
  if not access_token:
    return HttpResponseRedirect(reverse('tutorial:home'))
  else:
    tasks = get_my_tasks(access_token)
    print('!!!', tasks)
    context = { 'tasks': tasks['value'] }
    return render(request, 'tutorial/tasks.html', context)
