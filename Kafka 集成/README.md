# Python & Kafka

# KafkaProducer

## 示例项目

### 引用 kafka-python

```bash
pip install kafka-python==2.0.2
```

### 生产者

```bash
from kafka import KafkaProducer
from kafka.errors import kafka_errors
import traceback
import json
import time

def producer_demo():
    # 假设生产的消息为键值对（不是一定要键值对），且序列化方式为json
    producer = KafkaProducer(
        bootstrap_servers=['192.168.1.211:9092'],
        key_serializer=lambda k: json.dumps(k).encode(),
        value_serializer=lambda v: json.dumps(v).encode())
    
    for i in range(1,10):
        future = producer.send(
            'test',
            key='count_num',  # 同一个key值，会被送至同一个分区
            value=str(i),
            partition=0)  
        print("send {}".format(str(i)))
        try:
            future.get(timeout=10) # 监控是否发送成功
        except Exception as e:  # 发送失败抛出kafka_errors
            print(str(e))
if __name__ == "__main__":
    producer_demo()
```

### 消费者

```bash
from ast import Not
from kafka import KafkaConsumer

import json

def consumer_demo():
    consumer = KafkaConsumer(
        'test',
        bootstrap_servers='192.168.1.211:9092',
        group_id='test'
    )
    for message in consumer:
        if message.key is not None:
            print("receive, key: {}, topic: {}, value: {}".format(
                json.loads(message.key.decode('utf-8')),
                message.topic,
                json.loads(message.value.decode())
                )
            )
if __name__ == '__main__':
    consumer_demo()
```