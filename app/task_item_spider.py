
import sys
import os
# os.path.abspath(__file__)
import datetime
from email.header import Header
from feapder.db.mysqldb import MysqlDB
import feapder
from feapder.utils.webdriver import  WebDriver
from handler.logHandler import LogHandler
from handler.configHandler import ConfigHandler
from lxml.html import tostring
from lxml import html as lh
config = ConfigHandler()
from utils.token_manager import TokenManager

class TaskItemSpider(feapder.AirSpider):
    __custom_setting__ = {
       # "SPIDER_SLEEP_TIME":[3,6],
        # "PROXY_EXTRACT_API":"https://v1.api.juliangip.com/dynamic/getips?num=10&pt=1&result_type=text&split=1&trade_no=1920119669277911&sign=f93cca1f5e536cb2952df708734fdf56",
        # "PROXY_ENABLE":True
    }


    def __init__(self,thread_count):
        super().__init__(thread_count)

        self.logger = LogHandler("Spider")
        # self.monitor = Monitor()
        self.config = ConfigHandler()
        self.token_manger = TokenManager()
        self.pc_token = self.token_manger.generate_random_pc_token()
        # self.phone_token = self.token_manger.generate_random_phone_token()
        self._mysql_db = MysqlDB(**config.mysql_settings)
    def start_requests(self):
      
        
        target_url = 'https://api.seller.sq12315.com/seller/goods/spec/list'
        
        # params = {
        #     'token': self.pc_token,
        #     'source': '1',
        #     'rows': '15',
           
        #     'keyword': '',
        #     'goods_type_name': '',
        # }
        
        """本店铺所有item状态更新"""
        # target_list_url = target_list_url_template.format(self.pc_token,str(1),task['catalogueNo'],task['title'])

        yield feapder.Request(target_url,callback=self.parse_task_list,page=1,total=0)


        

    def download_midware(self, request):

        headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=utf-8',
    'Origin': 'https://seller.sq12315.com',
    'Referer': 'https://seller.sq12315.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
        }
        params = {
            'token': self.pc_token,
            'source': '1',
            'rows': '15',
            'page': request.page,
            'keyword': '',
            'goods_type_name': '',
        }
        
        request.headers = headers
        request.params = params
    def validate(self, request, response):
        if "会话" in response.text:
            # self.phone_token = self.token_manger.generate_random_phone_token()
            self.pc_token = self.token_manger.generate_random_pc_token()
    def parse_task_list(self,request,response):
        print(response.json)
        # target_list_url_template = "https://api.seller.jsshyc.com/seller/goods/spec/list?token={}&source=1&rows=100&page={}&keyword=&goods_type_no={}&goods_type_name={}"

       
        result = response.json['result']
        current_page = request.page
        total = request.total
        total += len(result['list'])
        if current_page+1 <= result['pages']:
            
            yield feapder.Request(request.url,callback=self.parse_task_list,page=current_page+1,total=total)
        
        
        for good in result['list']:
            item = {}
            item['goods_name'] = good.get('goods_name','')
            # item['can_pricing'] = good.get('can_pricing','')
            # item['create_time'] = good.get('create_time', '')
            item['sell_price'] = good.get('sell_price', 0)
            # item['goods_pic'] = good.get('goods_pic', '')
            item['goods_no'] = good.get('goods_no', '')
            item['spec_no'] = good.get('spec_no', '')
            # item['goods_spell'] = good.get('goods_spell', '')
            # item['goods_type_no'] = good.get('goods_type_no', '')
            item['goods_type_name'] = good.get('goods_type_name', '')
            item['catalogue_name'] = good.get('catalogue_name', '')
            item['goods_unit'] = good.get('goods_unit', '')
            item['price_update_time'] = good.get('price_update_time',datetime.datetime.strftime(datetime.datetime.today(),"%Y-%m-%d %H:%M:%S"))
            item['goods_alias'] = good.get('goods_alias', '')
            item['catalogue_name'] = good.get('catalogue_name', '')
            # item['target_item_num'] = good.get('goods_type_no_1', '')
            item['spec_status'] = good.get('spec_status', '')
            # item['spec_name'] = good.get('spec_name', '')

            self._mysql_db.add_smart("task_detail_item_table",item,auto_update=True)
            
        



if __name__ == "__main__":





    TaskItemSpider(thread_count=30).start()




