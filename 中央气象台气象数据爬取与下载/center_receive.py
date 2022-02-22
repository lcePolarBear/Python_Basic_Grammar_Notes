import datetime
import json
import os
import time
import urllib.request
from kafka_connect import KafkaConnet
from mysql_connect import DBConnet

class WorkLoad(object):
    def __init__(self) -> None:
        self.dbconnet = DBConnet()
        self.id_table = self.dbconnet.selectTablefunc()
        self.kafkaconnect = KafkaConnet()
        api_token = "fklasjfljasdlkfjlasjflasjfljhasdljflsdjflkjsadljfljsda"
        self.header = {"Authorization": "Bearer " + api_token} # 设置http header

    def download_img(self, id, img_url):
        # 这里以当前运行时间为基准，应该为以 url 带的时间为基准
        now = datetime.datetime.now()
        try:
            request = urllib.request.Request(img_url, headers=self.header)
            response = urllib.request.urlopen(request,timeout=4)      
            if (response.getcode() == 200):
                # 将图片路径生成放在确认图片 url 可以正常拉取之后，防止 url 错误导致路径生成失败
                file_path = "./downloadImage/" + str(now.year) + "/" + str(now.month) + "/" + str(now.day) + "/" + str(id) + "/"
                file_name = file_path + self.image_name(img_url) + ".jpg"
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                with open(file_name, "wb") as f:
                    f.write(response.read()) # 将内容写入图片
                return file_name
        except Exception as e:
            print(str(e))
            return None

    def image_name(self, image_url):
        ts = int(image_url[-13:-3])
        dt = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(ts))
        return str(dt)

    def main(self):
        for message in self.kafkaconnect.download_receive:
            message_id = json.loads(message.key.decode())
            message_value = json.loads(message.value.decode())
            # 首先确定 url 是否是图片链接（以 http 开头），先下载图片再返回图片路径入库。
            if message_value[:4] == "http":
                message_value = self.download_img(message_id, message_value)
            # json 数据直接入库，如果图片下载失败（返回 None）则不入库。
            if message_value is not None:
                for item in self.id_table:
                    if item[0] == message_id:
                        self.dbconnet.execfunc(item[1], message_value, str(item[0]))

if __name__ == '__main__':
    workload = WorkLoad()
    workload.main()