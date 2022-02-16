import json
from kafka import KafkaConsumer, KafkaProducer


class KafkaConnet(object):
    def __init__(self):
        """
        初始化 kafka 连接：mnc 消费者、download 消费者、KafkaProducer 生产者
        """
        host = '192.168.102.242:9092'
        self.mnc_receive = KafkaConsumer(
            'mnc_bak',
            bootstrap_servers = host,
            group_id='mnc_bak'
        )
        self.download_receive = KafkaConsumer(
            'download_bak',
            bootstrap_servers = host,
            group_id='download_bak'
        )
        self.producer = KafkaProducer(
            bootstrap_servers=[host],
            key_serializer=lambda k: json.dumps(k).encode(),
            value_serializer=lambda v: json.dumps(v).encode()
        )

    def sendfunc(self, id, value, kafka_topic):
        """
        通过指定 key,value 和 topic 发送 生产消息
        """
        future = self.producer.send(
            kafka_topic,
            key=id,  # 同一个key值，会被送至同一个分区
            value=value,
            partition=0)
        print("kafka-" + kafka_topic + " send {}".format(value))
        try:
            future.get(timeout=10) # 监控是否发送成功
        except Exception as e:  # 发送失败抛出kafka_errors
            print(str(e))
