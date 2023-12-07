from flask import Flask,render_template,request,make_response
from feapder.db.mysqldb import MysqlDB
from flask_cors import cross_origin
import datetime
import json
from threading import Thread
import requests
from task_item_spider import TaskItemSpider
from concurrent.futures import ThreadPoolExecutor

from handler.configHandler import ConfigHandler
app = Flask(__name__)
app.debug = True
config = ConfigHandler()
from concurrent.futures import ThreadPoolExecutor
from target_shop_spider import TargetShopSpider
from utils.token_manager import TokenManager

tm = TokenManager()
# token = tm.generate_random_pc_token()
db = MysqlDB(**config.mysql_settings)
@app.route("/",methods=['GET',"POST"])
def index():
    if request.method == "GET":
        sql = """SELECT `task_detail_item_table`.`goods_no`,       
        `task_detail_item_table`.`catalogue_name`,     
        `task_detail_item_table`.`goods_alias`,
        `task_detail_item_table`.`goods_name`,      
        `task_detail_item_table`.`goods_type_name`,
        `task_detail_item_table`.`goods_unit`,
        `task_detail_item_table`.`price_update_time`,
        
        `task_detail_item_table`.`sell_price`,    
        `task_detail_item_table`.`update_price`,
        `task_detail_item_table`.`sell_price` price_after_update
    FROM `price_compare`.`task_detail_item_table` where spec_status=1 and catalogue_name like "%(集采)%" ;
        """
        results = db.find(sql,to_json=True)
        shop_sql = "SELECT shop_no,shop_name FROM price_compare.shop_table"
        shop_results = db.find(shop_sql,to_json=True)
        total_record = len(results)
        shop_name="商铺名字/id"
        shop_name_init = ""
        offset_init = ""
        offset="差价"
        return render_template("index.html", results=results, shop_name_init=shop_name_init,
                               offset_init=offset_init, shop_name=shop_name, offset=offset, total_record=total_record, shop_results=shop_results)
    elif request.method == "POST":
        # print(request.form)
        shop_no = request.form.get("shop_name")
        price_offset = request.form.get("price_offset",0)
        print(shop_no,price_offset)
        sql = """SELECT 
            task.`goods_no`,
            task.`catalogue_name`,
            task.`goods_alias`,
            task.`goods_name`,
            task.`goods_type_name`,
            task.`goods_unit`,
         
            task.`price_update_time`,
            task.`sell_price`,
            a.sell_price update_price,
            a.sell_price + {}  price_after_update
        FROM
            `price_compare`.`task_detail_item_table` task
                LEFT JOIN
            (SELECT 
                shop_detail_table.*, RIGHT(goods_no, 5) goods_no_five
            FROM
                shop_detail_table
            WHERE
                shop_no = {}) a ON (a.goods_no_five = task.goods_no) where  task.spec_status=1 and task.catalogue_name like "%(集采)%"
        """.format(price_offset,shop_no)
        # print(sql)
        results = db.find(sql,to_json=True)
        shop_sql = "SELECT shop_no,shop_name FROM price_compare.shop_table"
        shop_results = db.find(shop_sql, to_json=True)
        total_record = len(results)
        return render_template("index.html", results=results, shop_name=shop_no, offset=price_offset, total_record=total_record, shop_results=shop_results)




@app.route("/spider",methods=['GET'])
def spider():
    TaskItemSpider(thread_count=15).start()
    message = "正在更新自家店铺数据"
    res = make_response(message)
    return res
@app.route("/quote",methods=["GET","POST","OPTIONS"])
@cross_origin(supports_credentials=True)
def get_quote():
    if request.method == "GET":
        sql = """select catalogue_name from task_detail_item_table

                        group by catalogue_name"""
        results = db.find(sql, to_json=True)
        sql_for_detail = """
                    SELECT goods_no,catalogue_name,goods_name FROM price_compare.task_detail_item_table;
                    """
        result_for_detail = db.find(sql_for_detail, to_json=True)
        cate_result = {}
        for result in results:
            cate_result[result['catalogue_name']] = {}
            cate_result[result['catalogue_name']]['item'] = []
            for item in result_for_detail:
                if item['catalogue_name'] == result['catalogue_name']:
                    cate_result[result['catalogue_name']]['item'].append(item)
        for cate_name in cate_result.keys():
            if cate_name == "水产（集采）":
                cate_result[cate_name]['first_page'] = "true"

            else:
                cate_result[cate_name]['first_page'] = "false"
        return render_template("search.html", results=results, cate_result=cate_result)
    elif request.method == "OPTIONS":
        res = make_response("wowo")
        res.headers['Access-Control-Allow-Origin'] = '*'
        res.headers['Access-Control-Allow-Method'] = '*'
        res.headers['Access-Control-Allow-Headers'] = '*'
        return res
    elif request.method == "POST":
        result = {}
        # print(request.form)
        # print(request.data)
        # data = json.loads(request.data.decode("utf8"))
        for key,value in request.form.items():
            if value:
                result[key] = int(value)

        condition  = format_sql(result)
        sql = """
            
select
shop_no,shop_name,credit_grade,total
from
(
select shop_no ,{} total
from
(
select shop_no,
{}
from 
(
select shop_no,
{}
 

from shop_detail_table
where shop_no in 
(select shop_no from shop_detail_table

where {}

group by shop_no 
having count(goods_no) = {}) )a group by shop_no)c
)b left join shop_table using(shop_no)
order by total asc
        
        """.format(*condition)
        # print(sql)
        results = db.find(sql,to_json=True)
        for rank,item in enumerate(results):
            item["index"] = rank  + 1
        # print(results)
        return render_template('result.html',results=results)
@app.route("/target_shop",methods=["GET","POST","OPTIONS"])
@cross_origin(supports_credentials=True)
def update_target_shop_default_addr():




    TargetShopSpider(thread_count=50).start()
    res = make_response("开始抓取更新本店对应店铺")
    return res

@app.route("/target_shop_dynamic",methods=["GET","POST","OPTIONS"])
@cross_origin(supports_credentials=True)
def update_shop_base_on_geo():
    if request.method == "POST":
        coordinate = request.data.decode("utf8")
        print(coordinate)
        DynamicSpider(thread_count=15,coordinate=coordinate).start()
        res = make_response("开始抓取更新动态店铺")
        return res


@app.route("/geo",methods=["GET","POST","OPTIONS"])
@cross_origin(supports_credentials=True)
def task_items_get():
    if request.method == "GET":
        sql = """select catalogue_name from task_detail_item_table

                               group by catalogue_name"""
        results = db.find(sql, to_json=True)
        sql_for_detail = """
                           SELECT goods_no,catalogue_name,goods_name FROM price_compare.task_detail_item_table;
                           """
        result_for_detail = db.find(sql_for_detail, to_json=True)
        cate_result = {}
        coordinate_sql = "select coordinate from coordinate_using "
        coordinate_results = db.find(coordinate_sql, to_json=True)
        if not coordinate_results:
            coordinat_using = "第一次更新,无坐标"
        else:
            coordinat_using = coordinate_results[0]['coordinate']
        for result in results:
            cate_result[result['catalogue_name']] = {}
            cate_result[result['catalogue_name']]['item'] = []
            for item in result_for_detail:
                if item['catalogue_name'] == result['catalogue_name']:
                    cate_result[result['catalogue_name']]['item'].append(item)
        for cate_name in cate_result.keys():
            if cate_name == "水产（集采）":
                cate_result[cate_name]['first_page'] = "true"

            else:
                cate_result[cate_name]['first_page'] = "false"
        return render_template("search_geo.html", results=results, cate_result=cate_result,coordinat_using=coordinat_using)

@app.route("/geo_quote",methods=["GET","POST","OPTIONS"])
@cross_origin(supports_credentials=True)
def quote_with_geo():
    if request.method == "POST":
        result = {}
        print(request.form)
        # print(request.data)
        # data = json.loads(request.data.decode("utf8"))
        for key, value in request.form.items():
            if value:
                result[key] = int(value)

        condition = format_sql(result)
        sql = """

        select
        shop_no,shop_name,credit_grade,total
        from
        (
        select shop_no ,{} total
        from
        (
        select shop_no,
        {}
        from 
        (
        select shop_no,
        {}


        from template_shop_detail_table
        where shop_no in 
        (select shop_no from template_shop_detail_table

        where {}

        group by shop_no 
        having count(goods_no) = {}) )a group by shop_no)c
        )b left join template_shop_table using(shop_no)
        order by total asc

                """.format(*condition)
        # print(sql)
        results = db.find(sql, to_json=True)
        # print(results)
        return render_template('result.html', results=results)

@app.route("/shelf_update",methods=['GET',"OPTIONS","POST"])
@cross_origin(supports_credentials=True)
def shelf():
    if request.method == "GET":
        sql = """SELECT `task_detail_item_table`.`goods_no`,
                `task_detail_item_table`.`spec_no`,
                `task_detail_item_table`.`catalogue_name`,

                `task_detail_item_table`.`goods_alias`,
                `task_detail_item_table`.`goods_name`,

                `task_detail_item_table`.`goods_type_name`,

               
                `task_detail_item_table`.`goods_unit`,
                `task_detail_item_table`.`price_update_time`,
                `task_detail_item_table`.`sell_price`,

                `task_detail_item_table`.`update_price`,
                `task_detail_item_table`.`sell_price` price_after_update
            FROM `price_compare`.`task_detail_item_table` where spec_status != 1 and spec_status !=2;
                """
        results = db.find(sql, to_json=True)
        shop_sql = "SELECT shop_no,shop_name FROM price_compare.shop_table"
        shop_results = db.find(shop_sql, to_json=True)
        total_record = len(results)
        shop_name = "商铺名字/id"
        offset = "差价"
        return render_template("shelf_update.html", results=results, shop_name=shop_name, offset=offset,shop_name_init="",
                               total_record=total_record, shop_results=shop_results,offset_init="")
    elif request.method == "POST":
        shop_no = request.form.get("shop_name")
        price_offset = request.form.get("price_offset", 0)
        # print(shop_no,price_offset)
        sql = """SELECT 
                   task.`goods_no`,
                    task.`spec_no`,
                   task.`catalogue_name`,
                   task.`goods_alias`,
                   task.`goods_name`,
                   task.`goods_type_name`,
                   task.`rational_max_price`,
                   task.`rational_min_price`,
                   task.`goods_unit`,
                   task.`price_update_time`,
                   task.`sell_price`,
                   a.goods_price update_price,
                   a.goods_price + {}  price_after_update
               FROM
                   `price_compare`.`task_detail_item_table` task
                       LEFT JOIN
                   (SELECT 
                       shop_detail_table.*, RIGHT(goods_no, 5) goods_no_five
                   FROM
                       shop_detail_table
                   WHERE
                       shop_no = {}) a ON (a.goods_no_five = task.goods_no)
                       where task.spec_status != 1
               """.format(price_offset, shop_no)
        # print(sql)
        results = db.find(sql, to_json=True)
        shop_sql = "SELECT shop_no,shop_name FROM price_compare.shop_table"
        shop_results = db.find(shop_sql, to_json=True)
        total_record = len(results)
        return render_template("shelf_update.html", results=results, shop_name=shop_no, offset=price_offset,
                               total_record=total_record, shop_results=shop_results,shop_name_init=shop_no,offset_init=price_offset)

@app.route("/geo_shelf",methods=['GET',"OPTIONS","POST"])
@cross_origin(supports_credentials=True)
def shelf_dynamic():
    coordinate_sql = "select coordinate from coordinate_using "
    coordinate_results = db.find(coordinate_sql, to_json=True)
    if not coordinate_results:
        coordinat_using = "第一次更新,无坐标"
    else:
        coordinat_using = coordinate_results[0]['coordinate']
    if request.method == "GET":
        sql = """SELECT `task_detail_item_table`.`goods_no`,
                `task_detail_item_table`.`spec_no`,
                `task_detail_item_table`.`catalogue_name`,

                `task_detail_item_table`.`goods_alias`,
                `task_detail_item_table`.`goods_name`,

                `task_detail_item_table`.`goods_type_name`,

                `task_detail_item_table`.`rational_max_price`,
                `task_detail_item_table`.`rational_min_price`,
                `task_detail_item_table`.`goods_unit`,
                `task_detail_item_table`.`price_update_time`,
                `task_detail_item_table`.`sell_price`,

                `task_detail_item_table`.`update_price`,
                `task_detail_item_table`.`sell_price` price_after_update
            FROM `price_compare`.`task_detail_item_table` where spec_status != 1;
                """
        results = db.find(sql, to_json=True)
        shop_sql = "SELECT shop_no,shop_name FROM price_compare.template_shop_table"
        shop_results = db.find(shop_sql, to_json=True)

        total_record = len(results)
        shop_name = "商铺名字/id"
        offset = "差价"
        return render_template("shelf_update_geo.html", results=results, shop_name=shop_name, offset=offset,shop_name_init="",
                               total_record=total_record, shop_results=shop_results,offset_init="",coordinat_using=coordinat_using)
    elif request.method == "POST":
        shop_no = request.form.get("shop_name")
        price_offset = request.form.get("price_offset", 0)
        # print(shop_no,price_offset)
        sql = """SELECT 
                   task.`goods_no`,
                    task.`spec_no`,
                   task.`catalogue_name`,
                   task.`goods_alias`,
                   task.`goods_name`,
                   task.`goods_type_name`,
                   task.`goods_unit`,
                   task.`rational_max_price`,
                   task.`rational_min_price`,
                   task.`price_update_time`,
                   task.`sell_price`,
                   a.goods_price update_price,
                   a.goods_price + {}  price_after_update
               FROM
                   `price_compare`.`task_detail_item_table` task
                       LEFT JOIN
                   (SELECT 
                       template_shop_detail_table.*, RIGHT(goods_no, 5) goods_no_five
                   FROM
                       template_shop_detail_table
                   WHERE
                       shop_no = {}) a ON (a.goods_no_five = task.goods_no)
                       where task.spec_status != 1
               """.format(price_offset, shop_no)
        # print(sql)
        results = db.find(sql, to_json=True)
        shop_sql = "SELECT shop_no,shop_name FROM price_compare.template_shop_table"
        shop_results = db.find(shop_sql, to_json=True)
        total_record = len(results)
        return render_template("shelf_update_geo.html", results=results, shop_name=shop_no, offset=price_offset,
                               total_record=total_record, shop_results=shop_results,shop_name_init=shop_no,offset_init=price_offset,coordinat_using=coordinat_using)


@app.route("/up_shelf",methods=['POST',"OPTIONS"])
@cross_origin(supports_credentials=True)
def up_shelf():
    if request.method == "OPTIONS":
        res = make_response("wowo")
        res.headers['Access-Control-Allow-Origin'] = '*'
        res.headers['Access-Control-Allow-Method'] = '*'
        res.headers['Access-Control-Allow-Headers'] = '*'
        return res
    elif request.method == "POST":
        # print(request.form)
        to_update_data = request.data.decode("utf8")
        error_result = {}


        print(list(json.loads(to_update_data).items()))
        handle_result = []
        for spec_no,price in json.loads(to_update_data).items():
            up_shelf_status(spec_no,price)
        message = "上架结束"
        res = make_response(message)


        return res


@app.route("/update", methods=['POST', "OPTIONS"])
@cross_origin(supports_credentials=True)
def update():
    if request.method == "OPTIONS":
        res = make_response("wowo")
        res.headers['Access-Control-Allow-Origin'] = '*'
        res.headers['Access-Control-Allow-Method'] = '*'
        res.headers['Access-Control-Allow-Headers'] = '*'
        return res
    elif request.method == "POST":
        # print(request.form)
        to_update_data = json.loads(request.data.decode("utf8"))
        error_result = {}

        print(to_update_data)
        token = tm.generate_random_pc_token()
        with ThreadPoolExecutor(max_workers=15) as executor:
            executor.map(update_price,)
        for goods_no, price in to_update_data.items():
            update_price(goods_no, price, token)
        message = "价格更新中"
        res = make_response(message)

        return res

def update_price(goods_no, sellprice, token):

    # token = tm.generate_random_pc_token()
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': 'https://seller.sq12315.com',
        'Pragma': 'no-cache',
        'Referer': 'https://seller.sq12315.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    url = f"https://api.seller.sq12315.com/seller/goods/detail/{goods_no}"
    detail_para = {
        "token": token,
        "source": 1
    }
    detail_response = requests.get(url, params=detail_para, headers=headers)

    detail = detail_response.json()['result']

    url = "https://api.seller.sq12315.com/seller/goods/update"
    params = {
        "token": token,
        "source": "1"
    }
    try:
        spec = detail['specs']
        goods_catalogue_no = spec[0]['goods_catalogue_no']
        spec_no = spec[0]['spec_no']
        spec_status = spec[0]['spec_status']
        net_amount_unit = spec[0]['net_amount_unit']
        net_amount = spec[0]['net_amount']
        barcode = spec[0].get('barcode', '')
        basic_prop = spec[0]['basic_prop']
        basic_status = spec[0]['basic_status']
        buy_price = spec[0]['buy_price']
        remark = spec[0]['remark']
        scale_kg = spec[0].get("scale_kg", 0)
        quantity = spec[0]['quantity']
        maximum_quantity = spec[0]['maximum_quantity']
        quality_guarantee_period = spec[0]['quality_guarantee_period']
        is_main = spec[0]['pics'][0]['is_main']
        name = spec[0]['pics'][0]['name']
        pic_cert_name = spec[0]['pics_cert'][0]['name'] if spec[0]['pics_cert'] else ''
        shop_nos = [spec[0]['shops'][0]['shop_no']]
        data = {"goods_no": goods_no, "specs": [{"goods_catalogue_no": goods_catalogue_no,
                                                "spec_no": spec_no,
                                                 "spec_status": spec_status,
                                                 "net_amount_unit": net_amount_unit,
                                                 "net_amount": net_amount,
                                                 "barcode": barcode,
                                                 "basic_prop": basic_prop,
                                                 "basic_status": basic_status,
                                                 "buy_price": buy_price,
                                                 "sell_price": sellprice,
                                                 "remark": remark,
                                                 "scale_kg": scale_kg,
                                                 "quantity": quantity,
                                                 "maximum_quantity": maximum_quantity,
                                                 "quality_guarantee_period": quality_guarantee_period,
                                                 "producing_area": detail['producing_area'],
                                                 "production_date": datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d"),
                                                 "expiration_date": datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d"),
                                                 "pics": [{"is_main": is_main,
                                                          "name": name}],
                                                 "pics_cert": [{"name": pic_cert_name}],
                                                 "shop_nos": shop_nos}],
                "token": token,
                "source": 1}

        # data = {"goods_no":22979,"specs":[{"goods_catalogue_no":6129,"spec_no":23996,"spec_status":1,"net_amount_unit":3,"net_amount":1,"barcode":"","basic_prop":1,"basic_status":1,"buy_price":0,"sell_price":3.62,"remark":"","scale_kg":0.5,"quantity":None,"maximum_quantity":0,"quality_guarantee_period":2,"producing_area":"中国","production_date":"2022-02-28","expiration_date":"2022-03-02","pics":[{"is_main":1,"name":"goodsSpecOaEgmtrlmpKsCOG"}],"pics_cert":[{"name":"goodsCert7FIZDT04DI1oX9T.png"}],"shop_nos":[383]}],"token":"483CE437D6CAFE60E5C2D4C630BD4CC4","source":1}
        data = json.dumps(data)

        response = requests.post(url, headers=headers,
                                 params=params, data=data)
        if response.json()['code'] == "0":
            print("goods_no :{},price:{} 价格更新成功".format(goods_no, sellprice))

        else:
            print(goods_no)
            print(response.json())
    except:
        return False


def up_shelf_status(spec_no,price):

    token = tm.generate_random_pc_token()
    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua": "^\\^",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "sec-ch-ua-platform": "^\\^Windows^^",
        "Origin": "http://seller.jsshyc.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "http://seller.jsshyc.com/",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"
    }
    url = "https://api.seller.jsshyc.com/seller/goods/batch/update/sellPriceAndStatus"
    params = {
        "token": token,
        "source": "1"
    }
    data = {"shelf_status":1,"specs":[{"spec_no":spec_no,"sell_price":price}],"token":token,"source":1}
    data = json.dumps(data)
    response = requests.post(url, headers=headers, params=params, data=data)
    if response.json()['code'] == "0":
        print("spec : {}, price : {}  上架成功".format(spec_no,price))
    else:
        print(response.json())
        print("spec : {}, price : {}  上架失败".format(spec_no, price))





def format_sql(result):
    item_number = len(result)
    shop_no_where_condition =" or ".join( ["right(goods_no,5)={}".format(goods_no) for goods_no in result.keys()])
    # print(shop_no_where_condition)

    case_condition =",".join( ["""case when right(goods_no,5) = {} then 
            goods_price*{} else 0 end total_price_{}""".format(goods_no,item_number,goods_no) for goods_no,item_number in result.items()])
    # print(case_condition)
    sum_statement = ",".join(["sum(total_price_{})  total_price_{} ".format(goods_no,goods_no) for goods_no in result.keys()])
    # print(sum_statement)
    total_sum = "+".join(["total_price_{}".format(goods_no) for goods_no in result.keys()])
    # print(total_sum)
    return total_sum,sum_statement,case_condition,shop_no_where_condition,item_number

if __name__ == "__main__":
    app.run()
