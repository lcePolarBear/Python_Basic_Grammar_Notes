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
            if redis_value is not None:
                if item_Value[:20] == "http://image.nmc.cn/":
                    item_time = int(item_Value[-37:-23])
                    redis_time = int(redis_value[-37:-23])
                    if item_time > redis_time:
                        self.work(item_id,item_Value)
                elif item_Value[:10] != redis_value[:10] or item_Value[-10:] != redis_value[-10:]:
                    self.work(item_id,item_Value)
            else:
                self.work(item_id,item_Value)
    
    def work(self, item_id, item_Value):
        self.redisconnet.redisset(item_id, item_Value)
        self.kafkaconnect.sendfunc(item_id, item_Value, self.send_topic)

if __name__ == '__main__':
    workload = workLoad()
    workload.main()