from datetime import date, datetime
import math
from zhdate import ZhDate as lunar_date
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['DATE_YEAR'],
commemoration_day = os.environ['COMM_DATE']


app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

# 当地时间
def get_weather():
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  high = math.floor(weather['high'])
  if high >= 30 :
    high = str(high + "今天天气很热，注意防暑防晒哦！")
  return weather['weather'], math.floor(weather['temp']), high



# 在一起的时间
def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

# 周年纪念日
def get_commemorationDay():
  next = datetime.strptime(str(date.today().year) + "-" + commemoration_day, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days


#生日
def get_birthday(year):
  day = lunar_date(year, 6, 1)
  birthday = str(day.to_datetime().strftime("%m-%d"))
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  if (next - today).days == 0 :
    year = int(today.year - year)
  return (next - today).days

# 年份顺延
def get_year(birthday=birthday):
  year = int(datetime.strptime(birthday, "%Y-%m-%d").strftime("%Y"))
  day = lunar_date(year, 6, 1)
  birthday = str(day.to_datetime().strftime("%m-%d"))
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    num = date.today().year - year
    year = year + num + 1
    return get_birthday(year)

#文字
def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature, high = get_weather()
data = {"weather" : {"value" : wea},
        "temperature" : {"value" : temperature},
        "high" : {"value" : high},
        "love_days" : {"value" : get_count()},
        "commemoration_days" : {"value" : get_commemorationDay()},
        "birthday_left" : {"value" : get_year()},
        "words":{"value" : get_words(), "color" : get_random_color()}
        }
res = wm.send_template(user_id, template_id, data)
print(res)
