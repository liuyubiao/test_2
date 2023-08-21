 #!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/22 13:56
# @Author  : liuyb
# @Site    :
# @File    : all_product_rule_server.py
# @Software: PyCharm
# @Description: 品类规则服务

import json
from importlib import import_module
import time
import re

from gevent import monkey
from gevent.pywsgi import WSGIServer
monkey.patch_all()

from flask import Flask, request
from flask_cors import CORS
# from tornado.wsgi import WSGIContainer
# from tornado.httpserver import HTTPServer
# from tornado.ioloop import IOLoop

from category.ocr_util import getOCR
from category.util import GS1Utils,CapacityamountFormat,CapacitysumFormat
from category.utilWordSize import threadingSend

import sys
sys.path.append("category")


app = Flask(__name__)
CORS(app,  resources={r"/*": {"origins": "*"}})
PORT = 5031

# # 2022-08-25增加
# cu = ClassifyUie()
app.cu = None

def rule_inference(category_id,product_id,imagelist,barCode,writeTime):
    barCode = barCode.strip()
    result = {}
    module = None
    func = None
    try:
        if module is None or func is None:
            # 引入对应的处理程序
            module = import_module('category.category_{}'.format(category_id))
            func = getattr(module, 'category_rule_{}'.format(category_id))

        datasorted = []
        dataprocessed = []
        dataOCR = []
        ocrResults = getOCR(imagelist)["data"]
        for ocrResult in ocrResults:
            try:
                dataOCR.append(ocrResult["data"]["dataOriginal"])
                datasorted.append(ocrResult["data"]["datasorted"])
                dataprocessed.append(ocrResult["data"]["dataprocessed"])
            except Exception as e:
                pass

        item_result_dict = func(datasorted,dataprocessed,dataOCR,imagelist,app.cu)

        threadingSend(barCode, ocrResults)

        if category_id == "299":
            brand, goods_name = gs1.get_outside_gs1_data(barCode)
            goods_name = goods_name.strip()
            brand = brand.strip()
            goods_name = re.sub("^\w+[:：]","",goods_name)
            if len(goods_name) > 2 and "未公开" not in goods_name:
                if item_result_dict["info3"] != "不分" and "香型" not in goods_name:
                    item_result_dict["commodityname"] = goods_name + "，" + item_result_dict["info3"]
                else:
                    item_result_dict["commodityname"] = goods_name

            if len(brand) > 1 and "未公开" not in brand and brand != "不分":
                item_result_dict["brand1"] = brand

        if item_result_dict["brand1"] == "不分" or item_result_dict["commodityname"] == "不分":
            brand, goods_name = gs1.get_outside_gs1_data(barCode)
            item_result_dict["brand1"] = item_result_dict["brand1"] if item_result_dict["brand1"] not in ["不分",""] else brand
            item_result_dict["commodityname"] = item_result_dict["commodityname"] if item_result_dict["commodityname"] not in ["不分",""] else goods_name

        if item_result_dict["brand1"] == "不分" and 'brand_tmp' in item_result_dict.keys():
            item_result_dict["brand1"] = item_result_dict["brand_tmp"] if item_result_dict["brand_tmp"] not in ["不分",""] else item_result_dict["brand1"]
        if 'brand_tmp' in item_result_dict.keys():
            item_result_dict.pop('brand_tmp')

        if item_result_dict["commodityname"].startswith(item_result_dict["brand1"]) and category_id != "299":
            if len(item_result_dict["commodityname"]) - len(item_result_dict["brand1"]) > 3:
                tmp_name = item_result_dict["commodityname"].replace(item_result_dict["brand1"],"")
                if len(re.compile("^[\W牌A-Za-z]").findall(tmp_name)) == 0:
                    item_result_dict["commodityname"] = tmp_name

        item_result_dict["capacitysum"] = re.sub("[kK][gG]", "千克", item_result_dict["capacitysum"])
        item_result_dict["capacitysum"] = re.sub("[gG]", "克", item_result_dict["capacitysum"])
        item_result_dict["capacitysum"] = re.sub("[mM][Ll]", "毫升", item_result_dict["capacitysum"])
        item_result_dict["capacitysum"] = re.sub("L", "升", item_result_dict["capacitysum"])

        item_result_dict["capacityamount"] = re.sub("[kK][gG]", "千克", item_result_dict["capacityamount"])
        item_result_dict["capacityamount"] = re.sub("[gG]", "克", item_result_dict["capacityamount"])
        item_result_dict["capacityamount"] = re.sub("[mM][Ll]", "毫升", item_result_dict["capacityamount"])
        item_result_dict["capacityamount"] = re.sub("L", "升", item_result_dict["capacityamount"])

        if category_id not in ["218"]:
            item_result_dict["commodityname"] = re.sub("\d+(克|毫升|[gG]|[mM][Ll])?$", "", item_result_dict["commodityname"])
        item_result_dict["commodityname"] = re.sub("^\d+(克|毫升|[gG]|[mM][Ll])", "", item_result_dict["commodityname"])

        if category_id not in ["103"]:
            item_result_dict["capacitysum"] = CapacitysumFormat(item_result_dict["capacitysum"])
            item_result_dict["capacityamount"] = CapacityamountFormat(item_result_dict["capacitysum"],item_result_dict["capacityamount"])

        item_result_dict["categoryID"] = category_id
        item_result_dict["adid"] = product_id
        item_result_dict["barCode"] = barCode
        item_result_dict["imageList"] = imagelist
        item_result_dict["writeTime"] = writeTime

        detail_list = []
        # for ocr,ds,dp,img in zip(dataOCR,datasorted,dataprocessed,imagelist):
        #     tmp_dict = {}
        #     # tmp_dict["Infos"] = func([ds,], [dp,], [img,])
        #     tmp_dict["Infos"] = {}
        #     tmp_dict["Ocr"] = ocr
        #     tmp_dict["imagePath"] = img
        #     detail_list.append(tmp_dict)

        result['data'] = item_result_dict
        result['detail'] = detail_list
        result['result'] = 0
        result['msg'] = '处理成功'
    except Exception as e:
        result['result'] = -1
        result['msg'] = '处理失败,原因为: {}'.format(str(e))

    return result

@app.route('/all_category_text_rule', methods=['GET', 'POST'])
def upload():
    result = {}
    start = time.time()

    if request.method == 'POST':
        category_id = request.form.get('cat')
        product_id = request.form.get('adid')
        # base64strs = json.loads(request.form.get('base64strs'))
        imagelist = json.loads(request.form.get('imageList'))
        barCode = request.form.get('barCode')
        writeTime = request.form.get('writeTime')

        if category_id == None or category_id == '':
            print('识别出现异常: 传入参数为空')
            result['result'] = -1
            result['msg'] = '传入的文本参数为空'

            end = time.time()
            print('本次识别结束,耗时: {} s'.format(end - start))
            print('--------------------------------')

            return json.dumps(result, ensure_ascii=False)

        try:
            # 开始进行解析工作
            result_json = rule_inference(category_id,product_id,imagelist,barCode,writeTime)
            end = time.time()

            #print('识别结果: {}'.format(result_json))
            print('本次识别结束,耗时: {} s'.format(end - start))
            print('--------------------------------')

            return json.dumps(result_json, ensure_ascii=False)
        except Exception as e:
            print('识别出现异常: {}'.format(str(e)))
            result['result'] = -3
            result['msg'] = '识别出现异常: {}'.format(str(e))
    else:
        result['result'] = -2
        result['msg'] = '请使用POST提交'

    end = time.time()
    print('本次识别结束,耗时: {} s'.format(end - start))
    print('--------------------------------')

    return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':
    # cu = ClassifyUie()
    # app.cu = cu

    gs1 = GS1Utils()

    http_server = WSGIServer(('', PORT), app)
    http_server.serve_forever()

    # http_server = HTTPServer(WSGIContainer(app))
    # http_server.listen(PORT)
    # print('程序启动成功, 正在监听端口: {}'.format(PORT))
    # IOLoop.instance().start()
