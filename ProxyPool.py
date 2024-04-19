import requests  # 导入模块
from lxml import etree
from fake_useragent import UserAgent
import sys
import traceback
import random


class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]


@Singleton
class ProxyPool(object):
    def __init__(self) -> None:
        # 创建两个列表用来存放代理ip
        self.all_ip_list = []  # 用于存放从网站上抓取到的ip
        self.usable_ip_list = []  # 用于存放通过检测ip后是否可以使用
        self.biliurl = 'https://www.baidu.com/' #'https://api.live.bilibili.com/xlive/fuxi-interface/ExploreController/actInitial'
        self.biliheaders = {
            #'Cookie': '',
        }

    def request_header(self):
        headers = {
            'User-Agent': UserAgent().Chrome  # 谷歌浏览器
        }
        return headers

    # 发送请求，获得响应
    def send_request(self):
        self.all_ip_list.clear()
        self.usable_ip_list.clear()
        # 爬取7页
        for i in range(1, 8):
            print(f'正在抓取第{i}页……')
            response = requests.get(
                url=f'http://www.ip3366.net/free/?page={i}', headers=self.request_header())
            text = response.text.encode('ISO-8859-1')
            # print(text.decode('gbk'))
            # 使用xpath解析，提取出数据ip，端口
            html = etree.HTML(text)
            tr_list = html.xpath('/html/body/div[2]/div/div[2]/table/tbody/tr')
            for td in tr_list:
                ip_ = td.xpath('./td[1]/text()')[0]  # ip
                port_ = td.xpath('./td[2]/text()')[0]  # 端口
                proxy = ip_ + ':' + port_  # 115.218.5.5:9000
                self.all_ip_list.append(proxy)
                self.test_ip(proxy)  # 开始检测获取到的ip是否可以使用
        # print('抓取完成！')
        # print(f'抓取到的ip个数为：{len(all_ip_list)}')
        # print(f'可以使用的ip个数为：{len(usable_ip_list)}')
        print('分别有：\n', self.usable_ip_list)

    # 检测ip是否可以使用

    def test_ip(self, proxy):
        # 构建代理ip
        proxies = {
            "http": "http://" + proxy,
            # "https": "https://" + proxy,
            # "http": proxy,
            # "https": proxy,
        }
        try:
            response = requests.get(url=self.biliurl, headers=self.biliheaders, proxies=proxies, timeout=1)  # 设置timeout，使响应等待1s
            # print(proxy, response.json()['_ts_rpc_return_']['data']['roundInfo'])
            if response.status_code == 200:
                self.usable_ip_list.append(proxy)
                print(proxy, '\033[31m可用\033[0m')
            else:
                print(proxy, '不可用')
        except Exception as e:
            print(proxy, '请求异常')
            traceback.print_exc()

    def chooseProxy(self):
        proxies_len = len(self.usable_ip_list)
        pindex = random.randint(0, proxies_len-1)
        proxy = self.usable_ip_list[pindex]
        proxies = {
            "http": "http://" + proxy,
        }
        return proxies, pindex

    def tick(self):
        proxies, pindex = self.chooseProxy()
        try:
            while len(self.usable_ip_list) > 0:
                response = requests.get(url=self.biliurl, headers=self.biliheaders, proxies=proxies, params={
                    '_ts_rpc_args_': '[30539515,"292933285",101814]'}, timeout=1)

                if response.status_code == 200:
                    print(proxies, '\033[31m可用\033[0m')
                    print(response.json()[
                        '_ts_rpc_return_']['data']['roundInfo'])
                    break
                else:
                    print(proxies, '不可用')
                    self.usable_ip_list.pop(pindex)

            if len(self.usable_ip_list) == 0:
                self.send_request()
                proxies, pindex = self.chooseProxy()
                while len(self.usable_ip_list) > 0:
                    response = requests.get(url=self.biliurl, headers=self.biliheaders, proxies=proxies, params={
                                            '_ts_rpc_args_': '[30539515,"292933285",101814]'}, timeout=1)
                    if response.status_code == 200:
                        print(proxies, '\033[31m可用\033[0m')
                        print(response.json()[
                            '_ts_rpc_return_']['data']['roundInfo'])
                        break
                    else:
                        print(proxies, '不可用')
                        self.usable_ip_list.pop(pindex)

        except Exception as e:
            print(proxies, '请求异常')
            traceback.print_exc()
