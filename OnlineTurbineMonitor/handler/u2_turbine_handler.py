'''
Created on 2018年4月27日

@author: user
'''
import tornado.web
import tornado.websocket
import json

import scr.GetDataFromRedis as rd
import app_global as glb

clients = []

rowindex = 2
uicoldescindex = 1
uicolsiindex = 2
uicolidindex = 4   # 2号机组对应id在E列

colvalueindex = 6  # 数据从G列开始读取

datafile = './cs_tag_all.xlsx'
sheet_name = u'DCS2AI'
uifile = './useful_data.xlsx'
by_name = u'rh_draw'
s = rd.generalsheet(datafile, sheet_name, uifile, by_name, rowindex,
                    uicolidindex, uicolsiindex, uicoldescindex, colvalueindex)  # 开始循环读取数据


def gettagdata():
    tagvaluelist = s.TagSnapshot()
    response_to_send = {}
    response_to_send['value'] = tagvaluelist
    return response_to_send


def sendmessage2client():
    response_to_send = gettagdata()
    for c in clients:
        c.write_message(json.dumps(response_to_send))  # python->json data structure


class realtimeHandler(tornado.web.RequestHandler):

    def get(self):
        title = '2号汽轮机高压缸性能概况'
        self.taglist = s.GetTagDefFromExcel()

        glb.clients_machine_ip.append(self.request.remote_ip)
        print('Client IP:', self.request.remote_ip)

        self.render("realtime_HPturbine.html", title=title,
                    tagname=self.taglist, devices='unit2')

    def post(self):
        pass


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def on_message(self, message):
        print("message received" + message)

    def open(self):
        if self not in clients:
            clients.append(self)
            self.write_message(u"connected")
            glb.clients_monitor_count += 1
            print("TurbineUnit2 WS open " + str(len(clients)) +
                  " Total Client: ", str(glb.clients_monitor_count))

    def on_close(self):
        if self in clients:
            clients.remove(self)
            glb.clients_monitor_count -= 1
            print("TurbineUnit2 WS close " + str(len(clients)) +
                  " Total Client: ", str(glb.clients_monitor_count))
