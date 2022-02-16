import sys
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from kafka_connect import KafkaConnet
from mysql_connect import DBConnet

class WorkLoad():
    def __init__(self) -> None:
        dbconnect = DBConnet()
        self.results_url = dbconnect.selectUrlfunc()
        self.results_tag = dbconnect.selectTagfunc()
        self.kafkaconnet = KafkaConnet()
        self.kafka_topic = 'mnc_bak'

    def main(self):
        for urlitem in self.results_url:
            url_id = urlitem[0]
            url = urlitem[1] #要访问的网址
            # html = self.getHTMLText(url) #获取 HTML
            html = self.getHTMLText(url) #获取 HTML
            
            if html is not None:
                for tagitem in self.results_tag:
                    if url_id == tagitem[0]:
                        label = tagitem[1]
                        attribute_key = tagitem[2]
                        attribute_value = tagitem[3]
                        src_value = tagitem[4]
                        element_tag = self.fillUnivlist(html, label, attribute_key, attribute_value, src_value)
                        if element_tag is not None:
                            content = self.getContent(element_tag, src_value)
                            if content is not None:
                                self.kafkaconnet.sendfunc(url_id, content, self.kafka_topic)

    def getHTMLText(self, url):
        try:
            driver = webdriver.PhantomJS(executable_path='/opt/mnc2/phantomjs')  # phantomjs的绝对路径
            driver.set_page_load_timeout(10)
            driver.set_script_timeout(10)
            driver.get(url)  # 获取网页
            return driver.page_source
        except Exception as e:
            print(str(e), file = sys.stderr)
            return None
    
    def fillUnivlist(self, html, label, attribute_key, attribute_value, src_value):
        try:
            soup = BeautifulSoup(html, 'html.parser')  # 用HTML解析网址
        except Exception as e:
            print(str(e), file = sys.stderr)
            return None            
        if src_value == "src":
            tag = soup.find_all(label, attrs={attribute_key: attribute_value})
        elif src_value is None:
            tag = soup.find(label, attrs={attribute_key: attribute_value})
        return tag
    
    def getContent(self, element_tag, src_value):
        if src_value == "src":
            url = None
            for pageOptionEle in element_tag:
                # 获取img标签的src中的url
                url = pageOptionEle.get('src', None)
                if url is not None:
                    url = re.sub('medium/','',url)
            return url
        if src_value is None:
            spanlList = list()
            for pageOptionEle in element_tag.children:
                if pageOptionEle is None:
                    return None
                span = pageOptionEle.find_all("span", class_="sname")[0].string + " - " + pageOptionEle.find_all("span", class_="sname")[1].string + " - " + pageOptionEle.find("div", class_="col-xs-4 text-right").string
                spanlList.append(span)
            return str(spanlList)

if __name__ == '__main__':
    workload = WorkLoad()
    while True:
        # 循环执行 main 函数
        workload.main()