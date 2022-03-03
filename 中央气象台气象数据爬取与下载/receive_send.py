import json
from kafka_connect import KafkaConnet
from redis_connect import RedisConnet


class workLoad():
    def __init__(self) -> None:
        self.send_topic = 'download_bak'
        self.kafkaconnect = KafkaConnet()
        self.redisconnet = RedisConnet()

    def main(self):
        for item in self.kafkaconnect.mnc_receive:
            
            item_id = json.loads(item.key.decode())
            item_Value = json.loads(item.value.decode())
            redis_value = self.redisconnet.redisget(item_id)
            # 如果 redis 中有此项 id 的数据，则进行更新操作
            if redis_value is not None:
                # 判断当前的资源类型是否为图片 url
                if item_Value[:20] == "http://image.nmc.cn/":
                    item_time = int(item_Value[-37:-23])
                    redis_time = int(redis_value[-37:-23])
                    if item_time > redis_time:
                        self.work(item_id,item_Value)
                # 如果不是 url 则为 list 数据，先削去后 14 位时间戳，不然会造成每一条数据都因时间戳不唯一而无法比较
                elif item_Value[:-14] != redis_value[:-14]:
                    self.work(item_id,item_Value)
            # 若 redis 无此项 id 数据，则进行新增操作
            else:
                self.work(item_id,item_Value)
    
    def work(self, item_id, item_Value):
        # 确认 kafka 发送成功后再进行 redis 更新操作
        if self.kafkaconnect.sendfunc(item_id, item_Value, self.send_topic):
            self.redisconnet.redisset(item_id, item_Value)

if __name__ == '__main__':
    workload = workLoad()
    workload.main()