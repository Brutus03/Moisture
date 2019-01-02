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

# sqlite3をインポート
import sqlite3
import datetime

# channel access tokenを指定
line_bot_api = LineBotApi('<channel access token>')

# user IDとプッシュメッセージを指定
def message1():
    try:
      line_bot_api.push_message('<to>', TextSendMessage(text='お水ください'))
    except LineBotApiError as e:
    # error handle
      print("Error occurred")

# クラスを作成
class Moisture:
    # 計測の範囲を指定（1を指定した場合は-4.096Vから4.96Vまで計測可能）
    def __init__(self):
        GAIN = 1
        abc = Adafruit_ADS1x15.ADS1015()
        volts = abc.read_adc(0, gain=GAIN)
        self.volts = volts

    # logに書き込み
    def log_write(self):
        output_time = time.asctime()
        log_file = open("/var/log/python/moisture.log","a+", encoding="UTF-8")
        log_file.write(output_time + " : " + str(self.volts) + "V" + "\n")
        log_file.close()

    # データベースに書き込み
    def sqlite_insert(self):
        dbname = '/home/pi/python/moisture.db'
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        output_time = datetime.datetime.now()
        output_time = "{0:%Y-%m-%dT%H:%M:%SZ}".format(output_time)
        data = (output_time, self.volts)
        cur.execute('insert into moisture (date, volts) values (?,?)', (data))
        con.commit()
        con.close()

# しきい値を設定
count = 0

while True:
    # インスタンス生成
    moisture_ins = Moisture()
    volts = moisture_ins.volts

    if volts >= 100:
       print( "State with moistured : " + str(volts) + "V" )
       moisture_ins.log_write()
       moisture_ins.sqlite_insert()
    elif volts < 100 and volts >= 1:
       print( "Condition with reduced moisture : " + str(volts) + "V" )
       moisture_ins.log_write()
       moisture_ins.sqlite_insert()
    else:
       print( "No moisture condition : " + str(volts) + "V")
       moisture_ins.log_write()
       moisture_ins.sqlite_insert()
       if count == 3:
           message1()
           break
       else:
           count += 1
    time.sleep(600)
