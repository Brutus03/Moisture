#! /usr/bin/env python3
# _*_ coding: utf-8 _*_

# パスを通す
import sys
sys.path.append('/home/pi/.local/lib/python3.5/site-packages/')

# sqlite3、bokehをインポート
import sqlite3
import datetime
from bokeh.plotting import figure, output_file, show

# クラスを作成
class Moisture:
    x = []
    y = []

    def __init__(self):
        pass

    # データベースから取り出し
    def sqlite_select(self):
        dbname = '/home/pi/python/moisture.db'
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        cur.execute('SELECT date FROM moisture order by date desc limit 72')
        self.x = ([(x[0]) for x in cur.fetchall()])
        cur.execute('SELECT volts FROM moisture order by date desc limit 72')
        self.y = ([(y[0]) for y in cur.fetchall()])
        con.close()

    # グラフ描画
    def graph_draw(self):
    # prepare some data
        x = self.x[::-1]
        y = self.y[::-1]
    # output to static HTML file
        output_file("/home/pi/python/templates/lines.html")
    # create a new plot with a title and axis labels
        p = figure(title="moisture data", plot_width=1200, plot_height=500, x_axis_label='x', y_axis_label='y', x_range=x)
        p.vbar(x=x, top=y, width=0.3)
        p.y_range.start = 0
        p.xaxis.major_label_orientation = 1
    # add a line renderer with legend and line thickness
        p.line(x, y, line_width=5,legend="moisture:value", color="limegreen")
    # show the results
        show(p)

# インスタンス生成
moisture_ins = Moisture()
moisture_ins.sqlite_select()
moisture_ins.graph_draw()
