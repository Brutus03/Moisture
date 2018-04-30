#! /usr/bin/env python3
# _*_ coding: utf-8 _*_

# ADS1015の関数を読み込む
import time, signal, sys
import Adafruit_ADS1x15

# Messaging APIのパスを通す
sys.path.append('/home/pi/.local/lib/python3.5/site-packages/')

# Messaging APIのモジュールをインポート
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# sqlite3、bokehをインポート
import sqlite3
import datetime
from bokeh.plotting import figure, output_file, show

# channel access tokenを指定
line_bot_api = LineBotApi('<channel access token>')

# user IDとプッシュメッセージを指定
def message1():
    try:
      line_bot_api.push_message('<to>', TextSendMessage(text='お水ください'))
    except LineBotApiError as e:
    # error handle
      print("Error occurred")

# logに書き込み
def log_write():
    output_time = time.asctime()
    log_file = open("/var/log/python/moisture.log","a+", encoding="UTF-8")
    log_file.write(output_time + " : " + str(volts) + "V" + "\n")
    log_file.close()

# データベースに書き込み
def sqlite_insert():
    dbname = '/home/pi/python/moisture.db'
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    output_time = datetime.datetime.now()
    output_time = "{0:%Y-%m-%dT%H:%M:%SZ}".format(output_time)
    data = (output_time, (volts))
    cur.execute('insert into moisture (date, volts) values (?,?)', (data))
    con.commit()
    con.close()

# データベースから取り出し
def sqlite_select():
    dbname = '/home/pi/python/moisture.db'
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    cur.execute('SELECT date FROM moisture order by date desc limit 72')
    global x
    x = [(x[0]) for x in cur.fetchall()]
    cur.execute('SELECT volts FROM moisture order by date desc limit 72')
    global y
    y = [(y[0]) for y in cur.fetchall()]
    con.close()

# グラフ描画
def graph_draw():
    # prepare some data
    x.reverse()
    y.reverse()
    # output to static HTML file
    output_file("/home/pi/python/templates/lines.html")
    # create a new plot with a title and axis labels
    p = figure(title="moisture data", plot_width=1200, plot_height=500, x_axis_label='x', y_axis_label='y', x_range=x)
    p.vbar(x=x, top=y, width=0.3)
    p.y_range.start = 0
    p.xaxis.major_label_orientation = 1
    p.line(x, y, line_width=5,legend="moisture:value", color="limegreen")
    # show the results
    show(p)

# 計測の範囲を指定（1を指定した場合は-4.096Vから4.96Vまで計測可能）
GAIN = 1

abc = Adafruit_ADS1x15.ADS1015()

count = 0

while True:
    volts = abc.read_adc(0, gain=GAIN)
    if volts >= 100:
       print( "State with moistured : " + str(volts) + "V" )
       log_write()
       sqlite_insert()
       sqlite_select()
       graph_draw()
    elif volts < 100 and volts >= 1:
       print( "Condition with reduced moisture : " + str(volts) + "V" )
       log_write()
       sqlite_insert()
       sqlite_select()
       graph_draw()
    else:
       print( "No moisture condition : " + str(volts) + "V")
       log_write()
       sqlite_insert()
       sqlite_select()
       graph_draw()
       print(count)
       if count == 3:
           message1()
           break
       else:
           count += 1
    time.sleep(600)
