

from feapder.db.mysqldb import MysqlDB

import feapder

from feapder.utils.tools import  make_batch_sql
from utils import tools

from handler.logHandler import LogHandler
from handler.configHandler import ConfigHandler

config = ConfigHandler()
from utils.token_manager import TokenManager


class TargetShopSpider(feapder.AirSpider):
    __custom_setting__ = {
       # "SPIDER_SLEEP_TIME":[3,6],
        # "PROXY_EXTRACT_API":"https://v1.api.juliangip.com/dynamic/getips?num=10&pt=1&result_type=text&split=1&trade_no=1920119669277911&sign=f93cca1f5e536cb2952df708734fdf56",
        # "PROXY_ENABLE":True
    }


    def __init__(self,thread_count,coordinate=None):
        super().__init__(thread_count=thread_count)

        self.logger = LogHandler("Spider")
        # self.monitor = Monitor()
        self.config = ConfigHandler()
        self.tokenmanager = TokenManager()
        self.pc_token = self.tokenmanager.generate_random_pc_token()
        self.phone_token = self.tokenmanager.generate_random_phone_token()
        self.coordinate = coordinate
        self._mysql_db = MysqlDB(**config.mysql_settings)

        self.init_db()
    def init_db(self):
        shop_table_sql = "delete from shop_table"
        self._mysql_db.execute(shop_table_sql)
        shop_detail_table_sql = "delete from shop_detail_table"
        self._mysql_db.execute(shop_detail_table_sql)


    def start_requests(self):

        if not self.coordinate:
            self.coordinate = "33.888541,118.673728"

        shop_list_url_template = "https://api.mall.sq12315.com/shop/all/list/20-1"
        """抓取所有店铺的数据"""
        params = {
            "coordinate": self.coordinate,
            "sort_type": "25",
            "filters": "",
            "voucher_no": "null",
            "token": self.phone_token,
            "source": "2",
            "device_id": "358035084692361"
        }
        yield feapder.Request(shop_list_url_template, params=params, callback=self.parse_target_shop, page=1)

        

    def download_midware(self, request):
        

        headers = {
            'Host': 'api.mall.sq12315.com',
            'User-Agent': 'okhttp/3.11.0',
        }
        request.headers = headers
    def download_shop_list_midware(self,request):
        params = {
            "coordinate": self.coordinate,
            "sort_type": "25",
            "filters": "",
            "voucher_no": "null",
            "token": self.phone_token,
            "source": "2",
            "device_id": "358035084692361"
        }
        request.params = params
    def validate(self, request, response):
        if "会话" in response.text:
            self.phone_token = self.tokenmanager.generate_random_phone_token()
            self.pc_token = self.tokenmanager.generate_random_pc_token()
    def parse_task_list(self,request,response):
        """pc 端"""
        target_list_url_template = "https://api.seller.jsshyc.com/seller/goods/spec/list?token={}&source=1&rows=100&page={}&keyword=&goods_type_no={}&goods_type_name={}"

        goods_type_no = request.goods_type_no
        goods_type_name = request.goods_type_name
        result = response.json['result']
        current_page = request.page
        if current_page+1 <= result['pages']:
            target_list_url = target_list_url_template.format(self.pc_token,str(current_page+1), goods_type_no, goods_type_name)
            yield feapder.Request(target_list_url,callback=self.parse_task_list,page=current_page+1,goods_type_no=goods_type_no,goods_type_name=goods_type_name)

        for good in result['list']:
            item = {}
            item['goods_name'] = good.get('goods_name','')
            item['can_pricing'] = good.get('can_pricing','')
            item['create_time'] = good.get('create_time', '')
            item['sell_price'] = good.get('sell_price', '')
            item['goods_pic'] = good.get('goods_pic', '')
            item['goods_no'] = good.get('goods_no', '')
            item['spec_no'] = good.get('spec_no', '')
            item['goods_spell'] = good.get('goods_spell', '')
            item['goods_type_no'] = good.get('goods_type_no', '')
            item['goods_type_name'] = good.get('goods_type_name', '')
            item['catalogue_name'] = good.get('catalogue_name', '')
            item['goods_unit'] = good.get('goods_unit', '')
            item['price_update_time'] = good.get('price_update_time', '')
            item['goods_alias'] = good.get('goods_alias', '')
            item['catalogue_name'] = good.get('catalogue_name', '')
            item['target_item_num'] = good.get('goods_type_no_1', '')
            item['spec_status'] = good.get('spec_status', '')
            item['spec_name'] = good.get('spec_name', '')

            self._mysql_db.add_smart("task_detail_item_table",item,auto_update=True)


    def parse_target_shop(self,request,response):

        target_shop_name = ['江苏天天美味餐饮有限公司','泗阳联创农业发展有限公司','江苏午硕生态农业发展有限公司',
                            '宿迁硕品商贸有限公司','泗阳金易采商贸有限公司','宿迁市泽青生鲜配送有限公司','宿迁市进奎食品有限公司',
                            '江苏五鲜供应链管理有限公司','泗阳富禄德食品商贸有限公司','江苏京盛原网络科技有限公司',
                            '泗阳优家餐饮配送有限公司','宿迁桃李生鲜配送有限公司','宿迁菜鸟生鲜配送有限公司',
                            '宿迁东时代农业发展有限公司','宿迁市大举商贸有限公司','江苏永态农副产品有限公司','泗阳久恒生鲜配送有限公司','泗阳县百春锦蔬菜专业合作社','泗阳广源健康食品有限公司'
                            ]
        result = response.json['result']

        pages = result['pages']
        current_page = request.page
        for shop in result['list']:
            # if shop.get('shop_name','') not in target_shop_name:
            #     continue
            item = {}
            item['shop_no'] = shop.get('shop_no','')
            item['shop_name'] = shop.get('shop_name','')
            item['shop_distance_max'] = shop.get('shop_distance_max',-1)
            item['credit_grade'] = shop.get('credit_grade','')
            item['delivery_type'] = shop.get('delivery_type',-1)
            item['delivery_type_text'] = shop.get('delivery_type_text','')
            item['shop_distance'] = shop.get('shop_distance',-1)
            item['minimum_order_amount'] = shop.get('minimum_order_amount',-1)
            item['main_products'] = shop.get('main_products','')
            # item['shop_logo'] = shop.get('shop_logo','')
            
            item['monthly_sales'] = shop.get('monthly_sales',0)
            item['insure'] = shop.get('insure',-1)
            item['evaluate_score'] = shop.get('evaluate_score',0)
            shop_no = shop.get('shop_no','')
            sql = tools.make_insert_sql("shop_table",item,auto_update=True)
            url = f"https://api.mall.sq12315.com/shop/goods/list/{shop_no}"
            self._mysql_db.add(sql)
            yield feapder.Request(url,download_midware=self.download_middware_detail,callback=self.parse_detail)
            
            

        if current_page+1 <= pages:
            shop_list_url_template = "https://api.mall.sq12315.com/shop/all/list/20-{}".format(str(current_page+1))
            yield feapder.Request(shop_list_url_template,page=current_page+1,callback=self.parse_target_shop,download_midware=self.download_shop_list_midware)
        for shop in result['list']:
            shop_no = shop['shop_no']
            url = f"https://api.mall.sq12315.com/shop/goods/list/{shop_no}"
            yield feapder.Request(url,download_midware=self.download_middware_detail,callback=self.parse_detail)

    def download_midware_item_detail(self,request):

        headers = {
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "http://seller.jsshyc.com",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "http://seller.jsshyc.com/",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        params = {
            "token": self.pc_token,
            "source": "1"
        }
        request.headers = headers
        request.params = params
    def download_middware_detail(self,request):
        headers = {
    'Accept': 'application/json',
    'Accept-Language': 'zh',
    'Host': 'api.mall.sq12315.com',
    'User-Agent': 'okhttp/3.11.0',
}

        params = {
        "source": "2",
        "device_id": "358035084692361",
        "token": self.phone_token
    }
        request.headers = headers
        request.params = params
    def parse(self, request, response):
        result = response.json['result']
        # print(result)
        first_page = request.first_page
        if first_page:
            for page in range(2,result['pages']+1):
                shop_list_url = "https://api.mall.jsshyc.com/shop/all/list/20-{}".format(str(page),callback=self.parse)

                yield feapder.Request(shop_list_url,callback=self.parse,first_page=False)

        for shop in result['list']:
            item = {}
            item['shop_no'] = shop['shop_no']
            item['shop_distance_max'] = shop['shop_distance_max']
            item['credit_grade'] = shop['credit_grade']
            item['delivery_type'] = shop['delivery_type']
            item['delivery_type_text'] = shop['delivery_type_text']
            item['shop_distance'] = shop['shop_distance']
            item['minimum_order_amount'] = shop['minimum_order_amount']
            item['main_products'] = shop['main_products']
            item['shop_logo'] = shop['shop_logo']
            item['shop_name'] = shop['shop_name']
            item['monthly_sales'] = shop['monthly_sales']
            item['insure'] = shop['insure']
            item['evaluate_score'] = shop['evaluate_score']

            sql = tools.make_insert_sql("shop_table",item,auto_update=True)
            self._mysql_db.add(sql)
            shop_no = shop['shop_no']
            shop_detail_info_url = f"https://api.mall.jsshyc.com/shop/goods/list/{shop_no}"
            if shop_no == "444":
                priority = 100
            else:
                priority = 300
            yield feapder.Request(shop_detail_info_url,download_midware=self.download_middware_detail,callback=self.parse_detail,priority=priority)
        
   
    def parse_detail(self,request,response):
        result = response.json['result']
        goods = []
        if request.url == "https://api.mall.sq12315.com/shop/goods/list/640":
            print("reusult :",result)
        for good in result.get('goods',[]):
            item = {}
            
            item['goods_no'] = good.get('goods_no','')
            item['goods_name'] = good.get('goods_name','')
            # item['goods_pic'] = good.get('goods_pic','')
            # item['favorable_rate'] = good.get('favorable_rate','')
            # item['sku_no'] = good.get('sku_no','')
            # item['barcode'] = good.get('barcode','')
            item['goods_unit'] = good.get('goods_unit','')
            # item['spec_name'] = good.get('spec_name','')
            # item['net_amount'] = good.get('net_amount','')
            # item['net_amount_unit'] = good.get('net_amount_unit','')
            # item['sale_by_weight'] = good.get('sale_by_weight','')
            item['good_unit_remark'] = good.get('good_unit_remark','')
            # item['quantity'] = good.get('quantity','')
            item['monthly_sales'] = good.get('monthly_sales','')
            # item['goods_original_price'] = good.get('goods_original_price','')
          
            item['shop_no'] = good.get('shop_no','')
            item['spec_no'] = good.get('catalogue_no','')
            # item['goods_unit_complex'] =good.get('goods_unit_complex','')
            # item['catalogues'] = good.get('catalogues','')
            item['sell_price'] = good.get('goods_price','')
            # item['goods_price_type'] = good.get('goods_price_type','')
            # item['member_price'] = good.get('member_price','')
           
            goods.append(item)
        # print(goods)
        if goods:
            self._mysql_db.add_batch_smart("shop_detail_table",goods)


