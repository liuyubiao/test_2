import re
import requests
import base64
import json
from collections import Counter
from PIL import Image
from io import BytesIO
import threading
import numpy as np
# from paddlenlp import Taskflow
import datetime

url_classify = "http://127.0.0.1"
url_search = "http://127.0.0.1"

Taste_Abort_List = ["有","回味","够味","滋味","调味","或","别有","美味","品味","更多","专吃","好口味","本味","年味","资味","大味","后风味","健味",
                    "知味","产品","多味","老味","选择","發味","好味","用","方味","妙","珍味","一味","味味","机味","其","态味","尔味","克味","捕味",
                    "姿味","命味","趣味","包装","旺味","小味","哆味","多样化","饮","型味","特","仅","粮味","事味","么","少味","合成","明味",
                    "分享","化味","生产","的","变","真","飞味","梦味","款","鼻味","级味","源味","熟悉","教","吃","晾","可味","像","好茶味","抿味",
                    "单味","理味","聚味","那","不同","炫味","楚味","入味","寻味","之味","县味","异味","大馅","这味","润味","匡味","民间","百草味",
                    "色风味","大口","如味","鼎味","个味","宝味","三味","一味","右味","每味","到味","首味","友味","佰味","保持","百味","分钟口味"]
Taste_Abort_List_Text = ["味更佳","味道更佳","味示意"]
Taste_Abort_List_pres = ["风味","口味","新口味"]

FRUIT_LIST = [
    "平安果","雪莲果","苹果","沙果","海棠","野樱莓","枇杷","欧楂","山楂","温柏","黑加仑","蔷薇果","花楸","香梨","雪梨","杏","樱桃","水蜜桃","蜜桃","黄桃","油桃","蟠桃等","李子","梅子","青梅","西梅","白玉樱桃",
    "黑莓","沃柑","覆盆子","云莓","甘蔗","罗甘莓","白里叶莓","草莓","菠萝莓","橘子","砂糖桔","橙子","柠檬","青柠","柚子","金桔","青桔","葡萄柚","香橼","佛手","指橙","黄皮果","哈密瓜","香瓜","白兰瓜","刺角瓜",
    "金铃子","香蕉","木瓜","枣","葡萄","提子","蓝莓","蔓越莓","越橘","芒果","猕猴桃","奇异果","金果","菠萝蜜","菠萝","凤梨","杨梅","柿子","桑葚","无花果","牛油果","火龙果","荔枝","龙眼","桂圆",
    "榴莲","石榴","椰子","椰蓉","槟榔","蛇皮果","山竹","圣女果","小番茄","沙棘","西瓜","脐橙","香橙","车厘子","网纹瓜","百香果","西柚","树莓","橙","桃","橘","蜜瓜","梨","柑","酸梅","刺梨","桑椹"
]

# class ClassifyUie(object):
#
#     def __init__(self, schemas=[]):
#         self.ie = Taskflow('information_extraction', schema=schemas)
#
#     def predict_info(self, texts_list):
#         try:
#             result = self.ie(texts_list)
#         except Exception as e:
#             result = []
#         return result
#
#     def get_info_UIE(self,texts_list):
#         self.set_schemas(['品牌', '产品名称'])
#         uie_brand = "不分"
#         uie_productname = "不分"
#         uie_brand_list = []
#         uie_productname_list = []
#
#         # full_text = [",".join(texts) for texts in texts_list if len(texts) > 0]
#         full_text = []
#         for texts in texts_list:
#             if len(texts) == 0 or texts == [""]:
#                 continue
#             tmp_str = ""
#             l = len(texts)
#             for index,txt in enumerate(texts):
#                 if len(txt) <= 2:
#                     split_flag = ""
#                 else:
#                     split_flag = ","
#                 tmp_str += txt
#                 if index != l -1:
#                     tmp_str += split_flag
#             full_text.append(tmp_str)
#         if len(full_text) >= 6:
#             split_num = int(len(full_text) / 2 + 1)
#             full_text = full_text[:split_num]
#
#         # uie_predict_list = self.predict_info(full_text)
#         uie_predict_list = []
#         for t in full_text:
#             uie_predict_list.extend(self.predict_info(t))
#
#         for uie_info in uie_predict_list:
#             if uie_info != None and '品牌' in uie_info.keys():
#                 uie_brand_list.append(uie_info["品牌"][0]["text"])
#             if uie_info != None and '产品名称' in uie_info.keys():
#                 uie_productname_list.append(uie_info["产品名称"][0]["text"])
#
#         uie_productname_list.sort(key=len,reverse=True)
#
#         if len(uie_brand_list) > 0:
#             count = Counter(uie_brand_list).most_common(2)
#             uie_brand = count[0][0]
#         if len(uie_productname_list) > 0:
#             count = Counter(uie_productname_list).most_common(2)
#             uie_productname = count[0][0]
#
#         return uie_brand, uie_productname
#
#     def set_schemas(self, schemas):
#         self.ie.set_schema(schemas)

class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        threading.Thread.join(self) # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None

# class GS1Utils(object):
#     def __init__(self):
#         self.outside_url = 'https://ali-barcode.showapi.com/barcode'
#         self.outside_appcode = "1fb56623de844f1bb2de46c28a2db5cf"
#         self.headers = {'Authorization': 'APPCODE ' + self.outside_appcode, 'Content-Type': 'application/x-www-form-urlencoded'}
#
#     def get_outside_gs1_data(self, barcode):
#         brand, goods_name = '不分', '不分'
#         params = {'code': barcode}
#         result = requests.get(self.outside_url, params=params, headers=self.headers)
#
#         try:
#             infos = json.loads(result.text)
#
#             showapi_res_code = infos['showapi_res_code']
#             if showapi_res_code != 0:
#                 raise Exception('请求接口出现异常')
#
#             showapi_res_body = infos['showapi_res_body']
#
#             brand, goods_name = showapi_res_body['trademark'], showapi_res_body['goodsName']
#         except Exception as e:
#             print('调用外部数据出现异常: {}'.format(str(e)))
#         return brand, goods_name

class GS1Utils(object):

    def __init__(self):
        self.outside_url = 'http://127.0.0.1:8080/ProductGs1/getValue/getGs1Result?barcode={}'
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    def get_outside_gs1_data(self, barcode):
        '''
        从gs1接口中获取品牌和商品全称
        Args:
            barcode:

        Returns:

        '''
        brand, goods_name = '不分', '不分'
        result = requests.get(self.outside_url.format(barcode), headers=self.headers)

        try:
            infos = json.loads(result.text)

            showapi_res_code = infos['showapi_res_code']
            if showapi_res_code != 0:
                raise Exception('请求接口出现异常')

            showapi_res_body = infos['showapi_res_body']

            brand, goods_name = showapi_res_body['trademark'], showapi_res_body['goodsName']
        except Exception as e:
            print('调用外部数据出现异常: {}'.format(str(e)))

        goods_name = goods_name.strip()
        brand = brand.strip()
        goods_name = re.sub("^\w+[:：]", "", goods_name)
        if "未公开" in goods_name or "暂无" in goods_name:
            goods_name = "不分"
        if "未公开" in brand:
            brand = "不分"
        return brand, goods_name

def get_brand_list(texts_list,Brand_list_1,Brand_list_2,keyWords,abortWords,num = 2):
    brand_1_tmp_list = []
    brand_1_txt_list = []
    brand_1_merge_tmp_list = []
    brand_1_merge_list = []
    brand_1_merge_absort_list = []
    brand_2 = []
    for texts in texts_list:
        # text_str = TextFormatNormal(texts)
        text_str = "".join(texts)
        text_str_ori = ",".join(texts)
        for bb in Brand_list_1:
            if bb in text_str :
                if len(bb) > 2 and len(re.compile("[\u4e00-\u9fa5]").findall(bb)) > 0:
                    brand_1_merge_tmp_list.append(bb)
                elif len(re.compile("(,|^)%s($|,)"%(",?".join(list(bb)))).findall(text_str_ori)) > 0:
                    brand_1_merge_tmp_list.append(bb)

        for text in texts:
            if text in keyWords:
                brand_1_txt_list.append(text)
            for b1 in Brand_list_1:
                if b1.upper() in text.upper() or b1 in text:
                    if b1 == text and b1 not in abortWords:
                        brand_1_txt_list.append(text)
                    if len(b1) > num or (len(re.compile("[市省镇区村县请勿]|大道|街道").findall(text)) == 0 and "地址" not in text):
                        brand_1_tmp_list.append(b1)
                    else:
                        brand_1_merge_absort_list.append(b1)

        for b2 in Brand_list_2:
            if b2 in texts:
                brand_2.append(b2)

    if len(brand_2) > 0:
        brand_2 = ",".join(list(set(brand_2)))
    else:
        brand_2 = "不分"

    for bm in brand_1_merge_tmp_list:
        if bm not in brand_1_tmp_list:
            brand_1_merge_list.append(bm)

    if len(brand_1_merge_list) > 0:
        count = Counter(brand_1_merge_list).most_common(1)
        brand_1 = count[0][0]
        if brand_1 not in brand_1_merge_absort_list:
            return brand_1,brand_2

    if len(brand_1_txt_list) > 0:
        # brand_1_tmp_list.sort(key=len, reverse=True)
        count = Counter(brand_1_txt_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0]:
            brand_1 = count[1][0]
        else:
            brand_1 = count[0][0]
    else:
        brand_1_list = []
        for i in brand_1_tmp_list:
            flag = True
            for j in brand_1_tmp_list:
                if j != i and i in j:
                    flag = False
                    break
            if flag:
                brand_1_list.append(i)

        if len(brand_1_list) == 0:
            brand_1 = "不分"
        else:
            brand_1_list.sort(key=len, reverse=True)
            count = Counter(brand_1_list).most_common(1)
            brand_1 = count[0][0]
    return brand_1,brand_2

def CapacityamountFormat(capacitysum,capacityamount):
    if capacitysum == "不分" or capacityamount == "不分" or len(re.compile("[*xX]").findall(capacityamount)) > 1:
        return capacityamount
    try:
        unit = re.compile("千克|克|毫升|升").findall(capacitysum)[0]
        sum = float(re.compile("\d+\.?\d*").findall(capacitysum)[0])
        amount = re.compile("(\d+\.?\d*)").findall(capacityamount)

        if len(amount) == 1:
            if sum % float(amount[0]) == 0:
                return str(sum//float(amount[0])) + unit + "*" + amount[0]
            else:
                return '%.2f' % (float(sum) / float(amount[0])) + unit + "*" + amount[0]
        elif len(amount) == 2:
            unit = re.compile("千克|克|毫升|升").findall(capacityamount)[0]
            if sum == float(amount[0]):
                if sum % float(amount[1]) == 0:
                    return str(int(sum) // int(amount[1])) + unit + "*" + amount[1]
                else:
                    # return '%.1f' %(float(sum)/float(amount[1])) + unit + "*" + amount[1]
                    return "不分"
            if sum == float(amount[1]) * float(amount[0]):
                amount_1 = re.compile("(\d+\.?\d*)"+unit).findall(capacityamount)[0]
                amount_2 = amount[1] if amount_1 == amount[0] else amount[0]
                return amount_1 + unit + "*" + amount_2
    except:
        pass
    return capacityamount

def CapacitysumFormat(capacitysum):
    if capacitysum == "不分":
        return capacitysum
    try:
        p_res = re.compile("(\d+\.?\d*)(千克|克|毫升|升)").findall(capacitysum)
        if len(p_res) > 0:
            p_res = p_res[0]
            num = float(p_res[0])
            unit = p_res[1]

            if unit == "千克":
                return str(int(num * 1000)) + "克"
            elif unit == "升":
                return str(int(num * 1000)) + "毫升"
            else:
                if num - int(num) == 0:
                    return str(int(num)) + unit
                else:
                    return str(num) + unit
    except:
        pass
    return capacitysum

def isNutritionalTable(text,texts,index):
    capacity_pattern = "^\d+\.\d+\.?[g克][^\u4e00-\u9fa5]|^\d+\.\d+\.?[g克]$"
    Nutrition_pattern = "(^[\u4e00-\u9fa5][白自百]质|^蛋白\w$|^脂肪|^[\u4e00-\u9fa5]水化[合台][\u4e00-\u9fa5]|^能量|能量$|^钠$|\d+[千k]?[焦J]|^\(m?[g]\)$|^\d+\.?\d*mg$|克\(.?\)|毫克\(.{0,2}\)|成分表|参考值|[nN][Rr][Vv])"
    if "克(g)" in text or "克(9)" in text or "每" in text or "J/100" in text or "g/100" in text or "营养" in text or "g/克" in text or "毫克" in text or "mg" in text:
        return False
    if len(re.compile("(^|\D+)0+[g克]").findall(text)) > 0:
        return False
    if len(re.compile(Nutrition_pattern).findall(text)) > 0:
        return False
    if len(re.compile("\d+[a-zA-Z\W]+\d+[g克]").findall(text)) > 0 and len(re.compile("\d+[g克\(]+\d+[g克]").findall(text)) == 0:
        return False
    if len(re.compile("^[a-zA-Z\W]+\d+[G]").findall(text)) > 0:
        return False
    if "的" in text or "产品" in text or "入" in text or "取" in text:
        return False
    if len(re.compile("^100[gG克][\u4e00-\u9fa5]$|^[\u4e00-\u9fa5]100[gG克]$").findall(text)) > 0:
        return False

    total_len = len(texts)
    for i in [-3, -2, -1]:
        if index + i >= 0 and index + i < total_len:
            p_res_tmp = re.compile(Nutrition_pattern).findall(texts[index + i])
            if len(p_res_tmp) > 0:
                return False

    if len(re.compile(capacity_pattern).findall(text)) > 0:
        for i in [1, 2, 3]:
            if index + i >= 0 and index + i < total_len:
                p_res_tmp = re.compile(Nutrition_pattern).findall(texts[index + i])
                if len(p_res_tmp) > 0:
                    return False
        num = 0
        for i in [-2, -1, 1, 2]:
            if index + i >= 0 and index + i < total_len:
                p_res_tmp = re.compile(capacity_pattern).findall(texts[index + i])
                if len(p_res_tmp) > 0:
                    num += 1
                if num > 0:
                    return False

    word_len_res = re.compile("[^\u4e00-\u9fa5\(\)]*\d+\.?\d*\s?[Gg克][^\u4e00-\u9fa5\(\)]*").findall(text)
    if len(word_len_res) > 0 and len(re.compile("wet|weight",re.IGNORECASE).findall(text)) == 0:
        num_len_list = [len(i) for i in word_len_res]
        if max(num_len_list) > 8:
            return False
    return True

def get_EXP_store(kvs_list,texts_list):
    pattern = r'(储存|贮藏|贮存)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    p_res = re.compile("-?\d{1,2}[-至]\d{1,2}[度C]?以?下?|零下\d+以?下?").findall(kv[k])
                    if len(p_res) > 0:
                        if len(re.compile("\d$").findall(p_res[0])) > 0:
                            return p_res[0] + "度"
                        else:
                            return p_res[0]

    pattern = r'(-?\d{1,2}[-至]\d{1,2}[度C]|零下\d{1,2}[度C]?以?下?|-18以?下?|0[cC度]?-4)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if len(re.compile("\d$").findall(p_res[0])) > 0:
                    return p_res[0] + "度"
                else:
                    return p_res[0]


    pattern = r'(冷藏|冷冻)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = r'常温'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

def get_EXP(kvs_list,texts_list):
    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    p_1 = re.compile(r'[0-9一-十]+个?[年天月]')
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    p_res_1 = p_1.findall(kv[k])
                    if len(p_res_1) > 0:
                        if len(re.compile(r'20[12]\d年[01]?\d月[0123]?\d日?').findall(kv[k])) > 0:
                            continue
                        return kv[k]

    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    if kv[k] in ["12","18"]:
                        return kv[k] + "个月"

    pattern = "-?\d{0,2}[-至]\d+[度C]?以?下?\d+个月|零下\d+以?下?\d+个月|-\d+以?下?\d+个月"
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                tmp_list.append(p_res[0])
        if len(tmp_list) > 0:
            return ",".join(tmp_list)

    pattern = r'(\D+[12]年|^[12]年|\d+个月|[一-十]+个月|\d+天)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "无理由" not in text and "退" not in text:
                return p_res[0]

    pattern = r'20[12]\d[-\\/\s\.]?[01]\d[-\\/\s\.]?[0123][\d]'
    date_list = []
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                p_res[0] = re.sub("\D", "", p_res[0])
                try:
                    d0 = datetime.datetime.strptime(p_res[0], "%Y%m%d")
                    tmp_list.append(p_res[0])
                    date_list.append(p_res[0])
                except:
                    pass
        if len(tmp_list) >= 2:
            tmp_list = list(set(tmp_list))
            tmp_list.sort(reverse=True)
            d0 = datetime.datetime.strptime(tmp_list[0], "%Y%m%d")
            df = datetime.datetime.strptime(tmp_list[-1], "%Y%m%d")
            d_res = (d0 - df).days
            if d_res > 1 and d_res < 367:
                return str(d_res) + "天"

    date_list = list(set(date_list))
    date_list.sort(reverse=True)
    if len(date_list) >= 2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y%m%d")
        df = datetime.datetime.strptime(date_list[-1], "%Y%m%d")
        d_res = (d0 - df).days
        if d_res > 1 and d_res < 367:
            return str(d_res) + "天"

    pattern = r'20[12]\d年[01]?\d月[0123]?\d日?'
    date_list = []
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "日" not in p_res[0]:
                    p_res[0] = p_res[0] + "日"
                try:
                    d0 = datetime.datetime.strptime(p_res[0], "%Y年%m月%d日")
                    tmp_list.append(p_res[0])
                    date_list.append(p_res[0])
                except:
                    pass
        if len(tmp_list) >= 2:
            tmp_list = list(set(tmp_list))
            tmp_list.sort(reverse=True)
            d0 = datetime.datetime.strptime(tmp_list[0], "%Y年%m月%d日")
            df = datetime.datetime.strptime(tmp_list[-1], "%Y年%m月%d日")
            d_res = (d0 - df).days
            if d_res > 1 and d_res < 367:
                return str(d_res) + "天"

    date_list = list(set(date_list))
    date_list.sort(reverse=True)
    if len(date_list) >= 2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y年%m月%d日")
        df = datetime.datetime.strptime(date_list[-1], "%Y年%m月%d日")
        d_res = (d0 - df).days
        if d_res > 1 and d_res < 367:
            return str(d_res) + "天"

    return "不分"

def TextFormatNormal(texts):
    if len(texts) == 0:
        return ""
    tmp_str = ""
    l = len(texts)
    for index, txt in enumerate(texts):
        if len(re.compile("^[a-zA-Z0-9\W]+$").findall(txt)) > 0 and len(re.compile("^[0-9]+$").findall(txt)) == 0:
            continue
        if len(re.compile("[0-9]{5,}").findall(txt)) > 0:
            continue
        if len(txt) <= 2:
            split_flag = ""
        else:
            split_flag = ","
            if tmp_str != "" and tmp_str[-1] != ",":
                tmp_str += ","
        tmp_str += txt
        if index != l - 1:
            tmp_str += split_flag
    return tmp_str

def get_keyValue(kvs_list,keys):
    result_list = []
    for kvs in kvs_list:
        for kv in kvs:
            for key in keys:
                for k in kv.keys():
                    if len(key) == 1:
                        if key == k:
                            result_list.append(kv[k])
                    else:
                        if key in k and  len(k) < 6 and len(kv[k]) > 1:
                            result_list.append(kv[k])

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) >1 and count[0][1] == count[1][1] and len(count[0][0]) < len(count[1][0]) and len(re.compile("[0-9,，、]").findall(count[1][0])) == 0:
        return count[1][0]
    else:
        return count[0][0]

def get_info_by_RE(texts_list,serchList):
    pattern = "("
    for i in serchList:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

def get_info_by_keyWord(texts_list,keyWords):
    result = "不分"
    for text_list in texts_list:
        for text in text_list:
            for keyWord in keyWords:
                if keyWord in text:
                    return text
    return result

def get_info_by_texts_list(texts_list,keyWords):
    for text_list in texts_list:
        for keyWord in keyWords:
            if keyWord in text_list:
                return keyWord
    return "不分"

def get_info_item_by_list(texts_list,serchList):
    result = "不分"
    for texts in texts_list:
        for text in texts:
            for t in serchList:
                if t in text:
                    return t
    return "不分"

def mySorted(sort_list,text_str):
    info_index = {}
    info_index_sorted = {}
    tmp_index = []
    tmp_list = []
    for index,info in enumerate(sort_list):
        info_index[info] = index
        if info in text_str:
            tmp_list.append(info)
            tmp_index.append(index)

    tmp_list = sorted(tmp_list,key=text_str.index)
    for info in sort_list:
        if info not in tmp_list:
            info_index_sorted[info] = info_index[info]
        else:
            info_index_sorted[info] = tmp_index[tmp_list.index(info)]

    return sorted(sort_list,key=lambda x: info_index_sorted[x])


def get_info_list_by_list(texts_list,serchList):
    result = []
    for texts in texts_list:
        for text in texts:
            index = 0
            for t in serchList:
                if t in text:
                    if t not in result:
                        result.append(t)
                    index += 1
            if index > 1:
                result = mySorted(result,text)
    result_sorted = sorted(result, key=len)
    res = []
    if len(result_sorted) > 0:
        for index, i in enumerate(result_sorted):
            flag = True
            for j in result_sorted[index + 1:]:
                if i in j:
                    flag = False
            if flag:
                res.append(i)
    res = sorted(res,key=result.index)
    return res

def get_info_list_by_list_taste(texts_list,serchList):
    result = []
    for texts in texts_list:
        for text in texts:
            index = 0
            if "," in text or "、" in text or "配料" in text or "入" in text or "或" in text or "柠檬酸" in text or "葡萄糖" in text or "制品" in text:
                continue
            for t in serchList:
                if t in text:
                    if t not in result:
                        result.append(t)
                    index += 1
            if index > 1:
                result = mySorted(result,text)

    result_sorted = sorted(result,key=len)
    res = []
    if len(result_sorted) >0:
        for index,i in enumerate(result_sorted):
            flag = True
            for j in result_sorted[index+1:]:
                tmp_i = re.sub("味$","",i)
                if tmp_i in j:
                    flag = False
            if flag:
                res.append(i)
    res = sorted(res, key=result.index)
    return res

def isTaste(tmp_taste,text):
    for i in Taste_Abort_List:
        if i in tmp_taste:
            return False
    for i in Taste_Abort_List_Text:
        if i in text:
            return False
    if tmp_taste in ["新口味",]:
        return False

    ttaste = re.sub("[口风]味","",tmp_taste)
    if len(ttaste) <= 1:
        return False

    if len(tmp_taste) == 2:
        if tmp_taste == "原味" or tmp_taste == "橙味" or tmp_taste == "橘味" or tmp_taste == "奶味" or tmp_taste == "咸味" or tmp_taste == "果味":
            return True
    elif len(tmp_taste) < 11:
        return True

    return False

def TasteFilter(text):
    if "," in text or "、" in text or "配料" in text or "柠檬酸" in text or "山梨酸" in text or "葡萄糖" in text or "食用盐" in text or "小麦粉" in text or "玉米粉" in text or "酿造黄油" in text:
        return True
    return False

def get_taste_normal(texts_list,Taste_list):
    result_list = []
    pattern_0 = "("
    pattern_1 = "([\u4e00-\u9fa5]+味)\)"
    pattern_2 = "([\u4e00-\u9fa5]+味)$"
    pattern_3 = ""
    pattern_4 = "("
    pattern_5 = ""
    pattern_6 = "[\u4e00-\u9fa5]+味"
    for t in Taste_list:
        if "味" not in t:
            pattern_0 += "\w*" + t + "[口风]?味" + "|"
        else:
            pattern_0 += "\w*" + t + "|"

        if "味" not in t:
            pattern_3 += t + "[口风]?味" + "|"
        else:
            pattern_3 += t + "|"
        pattern_4 += "\w*" + t + "|"
        pattern_5 += "^" + t + "$" + "|"
    pattern_0 = pattern_0[:-1] + ")(\)|$)"
    pattern_3 = pattern_3[:-1]
    pattern_4 = pattern_4[:-1] + ")\)"
    pattern_5 = pattern_5[:-1]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_0)
            if len(p_res) > 0:
                p_res = p_res[0]
                if isTaste(p_res[0], text):
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            if TasteFilter(text):
                break
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                if isTaste(p_res[0], text):
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            if TasteFilter(text):
                break
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if isTaste(p_res[0], text):
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if isTaste(p_res[0], text):
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            if TasteFilter(text):
                continue
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            if TasteFilter(text) or "入" in text or "或" in text:
                continue
            p_res = get_info_by_pattern(text, pattern_5)
            if len(p_res) > 0:
                result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    # for texts in texts_list:
    #     for text in texts:
    #         if TasteFilter(text):
    #             break
    #         p_res = get_info_by_pattern(text, pattern_6)
    #         if len(p_res) > 0:
    #             if isTaste(p_res[0],text) and "市" not in text and "区" not in text and "公司" not in text and "集团" not in text:
    #                 result_list.append(p_res[0])
    #
    # if len(result_list) > 0:
    #     count = Counter(result_list).most_common(2)
    #     return count[0][0]

    result = get_info_list_by_list_taste(texts_list, Taste_list)
    if len(result) > 0:
        result = list(set(result))
        return "".join(result)

    return "不分"

def isIngredient(text):
    Ingredient_Abort_List_in = ["省","市","地址","包装","背面","年","月","公司","避免","企业","本品","产地","产国","表","信息","阴凉","光线","生产","号"]
    Ingredient_Abort_List_re = "^[日\d]+$|^[a-zA-Z\d\W]+$"
    if len(text) <= 1:
        return False
    for i in Ingredient_Abort_List_in:
        if i in text:
            return False
    if len(re.compile(Ingredient_Abort_List_re).findall(text)) > 0:
        return False

    return True

def get_keyValue_equal(kvs_list,keys):
    for kvs in kvs_list:
        for kv in kvs:
            for key in keys:
                if key in kv.keys() :
                    return kv[key]
    return "不分"

def get_keyValue_list(kvs_list,keys):
    result_list = []
    for kvs in kvs_list:
        for kv in kvs:
            for key in keys:
                for k in kv.keys():
                    if len(key) == 1:
                        if key == k:
                            result_list.append(kv[k])
                    else:
                        if key in k and len(k) < 6 and len(kv[k]) > 1:
                            result_list.append(kv[k])
    return result_list

def get_info_by_pattern(text,pattern):
    p = re.compile(pattern)
    p_res = p.findall(text)
    return p_res

def get_info_by_UIE(text,uie):
    result = uie(text)

    return result

def get_url_result(base64strs,url,category_id="101"):
    package_list = []
    package_list_plus = []
    for base64_data in base64strs:
        payload = {
            "model_id": category_id,
            "data": base64_data
        }
        try:
            merge = requests.post(url='%s' % (url), data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            json_dict = json.loads(merge.text)
            if json_dict["result"] == 0:
                label = json_dict["label"]
                score = json_dict["score"]
            if label != "其他" and "电商" not in label and label != "不分":
                package_list.append((label,score))
                if float(score) > 0.7:
                    package_list_plus.append((label,score))
        except:
            pass
    if len(package_list_plus) > 0:
        package_list = package_list_plus

    package_list = sorted(package_list,key=lambda x:x[1],reverse=True)
    package_list = [i[0] for i in package_list]
    return package_list

def package_filter(package_classify_list , filter_list):
    res = []
    for pc in package_classify_list:
        if pc not in filter_list:
            res.append(pc)
    return res

def get_package(base64strs,category_id = None):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material, category_id,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape, category_id,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if shape == "网兜":
        return "网兜"

    if material == "塑料膜" and shape != "包裹":
        material = "塑料"

    if shape == "冰淇淋甜筒":
        return "不分"

    if shape == "无包装" or material == "无包装":
        return "无包装"

    return material + shape

def get_package_104(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    if "真空袋" in result_shape:
        return "真空塑料袋"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if shape == "礼包":
        return shape

    if material == "塑料底" or "塑料" in material:
        material = "塑料"
    elif material == "玻璃底":
        material = "玻璃"

    if shape == "格":
        shape = "盒"

    if "袋" in shape:
        shape = "袋"
    elif "瓶" in shape:
        shape = "瓶"
    elif "桶" in shape:
        shape = "桶"

    return material + shape


def get_package_112(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    # 获取执行结果
    result_material = task_material.get_result()

    if len(result_material) == 0:
        return "不分"

    if "塑料底" in result_material:
        return "塑料包装"
    if "玻璃底" in result_material:
        return "玻璃包装"

    material = Counter(result_material).most_common(1)[0][0]

    return material + "包装"

def get_package_125(base64strs):
    url_shape = url_classify + ':5029/yourget_opn_classify'
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    result_shape = task_shape.get_result()

    if len(result_shape) > 0:
        shape = Counter(result_shape).most_common(1)[0][0]
        if "袋" in shape:
            shape = "袋"
        elif "瓶" in shape or shape in ["杯"]:
            shape = "瓶"
        elif "桶" in shape:
            shape = "桶"
        elif shape in ["托盘","格","碗"]:
            shape = "盒"
        elif "罐" in shape:
            shape = "罐"
        else:
            shape = "袋"
        return shape
    else:
        return "袋"

def get_package_126(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if material == "金属":
        return "铁罐（盒）（桶）"
    if shape == "礼包":
        return shape
    if material == "塑料底" or "塑料" in material:
        material = "塑料"
    elif material == "玻璃底":
        material = "玻璃"

    if "袋" in shape:
        shape = "袋"
    elif "瓶" in shape:
        shape = "瓶"
    elif "桶" in shape:
        shape = "桶"
    elif "罐" in shape:
        shape = "罐"

    if shape in ["格","盒","桶","罐","杯","筒","托盘","碗"]:
        shape = "盒（桶）"

    return material + shape

def get_package_128(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if shape == "礼包":
        return shape
    elif "袋" in shape:
        return "塑料袋"
    if "玻璃底" in result_material:
        material = "玻璃"
    elif "塑料底" in result_material:
        if "半透明塑料" in result_material:
            return "半透明塑料瓶(桶)"
        elif "非透明塑料" in result_material:
            return "非透明塑料瓶(桶)"
        else:
            return "全透明塑料瓶(桶)"

    if material == "玻璃":
        return "玻璃瓶"

    if material == "半透明塑料":
        return "半透明塑料瓶(桶)"
    elif material == "非透明塑料":
        return "非透明塑料瓶(桶)"
    else:
        return "全透明塑料瓶(桶)"

def get_package_130(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if shape == "礼包":
        return shape
    elif "袋" in shape:
        return "袋装"

    if "塑料底" in result_material or "塑料" in material:
        material = "塑料"
    if "玻璃底" in result_material:
        material = "玻璃"

    if "瓶" in shape or "桶" in shape or shape in ["杯","罐","筒"]:
        shape = "瓶"

    if shape in ["托盘","格","碗"]:
        shape = "盒"

    if material + shape == "塑料瓶":
        return "塑料瓶(桶)"
    else:
        return material + shape

def get_package_131(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if material == "金属":
        return "金属罐，听"
    elif shape == "礼包":
        return "礼盒"
    elif shape == "吸嘴袋":
        return "吸嘴塑料袋"
    elif shape == "挤压瓶":
        return "挤压塑料瓶"

    if "塑料底" in result_material or "塑料" in material:
        material = "塑料"
    if "玻璃底" in result_material:
        material = "玻璃"

    if "瓶" in shape or "桶" in shape or shape in ["罐", "筒"]:
        shape = "瓶，桶"
    if shape in ["杯", "碗"]:
        shape = "杯，碗"
    if shape in ["托盘", "格"]:
        shape = "盒"
    if "袋" in shape:
        shape = "袋"

    if material + shape in ["纸瓶，桶", "纸杯，碗" ]:
        return "纸桶装"
    else:
        return material + shape

def get_package_138(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if material == "金属":
        return "金属盒，桶"
    elif shape == "礼包":
        return "礼盒，礼袋"
    elif shape == "真空袋":
        return "真空袋"

    if "塑料底" in result_material or "塑料" in material:
        material = "塑料"
    if "玻璃底" in result_material:
        material = "玻璃"

    if "瓶" in shape or "桶" in shape or shape in ["罐","筒","杯"]:
        shape = "瓶，桶"
    if shape in ["托盘", "格", "碗"]:
        shape = "盒"
    if shape in ["立式袋", "吸嘴袋"]:
        shape = "袋"

    if material + shape in ["纸盒"]:
        return "纸盒，箱"
    elif material + shape in ["纸袋"]:
        return "纸袋，桶"
    else:
        return material + shape

def get_package_189(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if material == "金属":
        return "金属罐,桶"
    elif shape == "把手桶":
        return "把手塑料桶,瓶"
    elif shape == "喷雾瓶":
        return "喷雾瓶"
    elif shape == "滴管瓶":
        return "滴管瓶"

    if "塑料底" in result_material or "塑料" in material:
        material = "塑料"

    if "玻璃底" in result_material or material == "玻璃":
        return "玻璃瓶"
    if material == "纸":
        return "纸盒,礼盒"
    if material == "木":
        return "木盒,木盒"

    if "瓶" in shape or shape in ["筒", "杯"]:
        shape = "瓶"
    if shape in ["托盘", "格"]:
        shape = "盒"
    if "袋" in shape:
        shape = "袋"

    return material + shape

def get_package_510(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if shape == "立式袋":
        return "立式塑料袋"
    if "玻璃底" in result_material or material == "玻璃":
        return "玻璃罐(瓶)"
    if material == "金属":
        return "金属罐"
    if "塑料底" in result_material or "塑料" in material:
        material = "塑料"

    if material == "纸":
        return "纸盒"
    if material == "木":
        return "木盒"

    if "瓶" in shape or "桶" in shape or shape in ["罐","筒", "杯"]:
        shape = "罐(瓶)"
    if shape in ["托盘", "格"]:
        shape = "盒"
    if "袋" in shape:
        shape = "袋"

    if material + shape in ["塑料袋"]:
        return "普通塑料袋"
    else:
        return material + shape

def get_package_egg(base64strs,category_id = "103"):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs,url_material,category_id,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape, category_id,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if "格" in result_shape:
        result_shape_numpy = np.asarray(result_shape)
        index = np.where(result_shape_numpy == "格")[0]
        result_material = [result_material[i] for i in index]
        result_shape = [result_shape[i] for i in index]

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if shape == "网兜":
        return "网兜"

    if material == "塑料膜" and shape != "包裹":
        material = "塑料"

    if shape == "冰淇淋甜筒":
        return "不分"

    if shape == "无包装" or material == "无包装":
        return "无包装"

    return material + shape

def get_package_honey(base64strs,category_id = None):
    url_material = url_classify + ':5028/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material, category_id,))
    task_material.start()
    # 获取执行结果
    result_material = task_material.get_result()

    if len(result_material) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]

    if material == "塑料膜":
        material = "塑料"

    return material + "包装"


def get_package_suger(base64strs,category_id = None):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material, category_id,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape, category_id,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if "自封袋" in result_shape:
        return "自封袋装"

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if shape == "网兜":
        return "网兜"

    if material == "塑料膜" and shape != "包裹":
        material = "塑料"

    if shape == "冰淇淋甜筒":
        return "不分"

    if shape == "无包装" or material == "无包装":
        return "无包装"

    return material + shape

def get_suger_shape(base64strs,category_id = None):
    url_suger_shape = url_classify + ':5022/yourget_opn_classify'
    task_suger_shape = MyThread(get_url_result, args=(base64strs, url_suger_shape, category_id,))
    task_suger_shape.start()
    result_suger_shape = task_suger_shape.get_result()

    if len(result_suger_shape) > 0:
        return Counter(result_suger_shape).most_common(1)[0][0]
    else:
        return "粒状"

def get_package_penghua(base64strs,category_id = None):
    url_shape = url_classify + ':5029/yourget_opn_classify'
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape, category_id,))
    task_shape.start()
    result_shape = task_shape.get_result()

    if len(result_shape) > 0:
        return Counter(result_shape).most_common(1)[0][0]
    else:
        return "袋"

def get_package_icecream(base64strs, category_id=None):
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_shape = MyThread(get_url_result, args=(base64strs, url_shape, category_id,))
    task_shape.start()
    # 获取执行结果
    result_shape = task_shape.get_result()

    package_list_0 = []
    package_list_1 = result_shape
    for label in result_shape:
        if "盒" not in result_shape:
            package_list_0.append(label)

    if len(package_list_0) > 0:
        return Counter(package_list_0).most_common(1)[0][0]

    if len(package_list_1) > 0:
        return Counter(package_list_1).most_common(1)[0][0]
    else:
        return "不分"

def get_chocolate(base64strs, category_id=None):
    url_chocolate = url_classify + ':5027/yourget_opn_classify'
    task_suger_shape = MyThread(get_url_result, args=(base64strs, url_chocolate, category_id,))
    task_suger_shape.start()
    result_chocolate = task_suger_shape.get_result()

    if "有巧克力包裹" in result_chocolate:
        return "有巧克力包裹"

    if len(result_chocolate) > 0:
        return Counter(result_chocolate).most_common(1)[0][0]
    else:
        return "无巧克力包裹"

def get_package_tea(base64strs, category_id=None):
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_shape = MyThread(get_url_result, args=(base64strs, url_shape, category_id,))
    task_shape.start()
    # 获取执行结果
    result_shape = task_shape.get_result()

    package_list = result_shape

    if len(package_list) > 0:
        return Counter(package_list).most_common(1)[0][0]
    else:
        return "不分"

def get_package_box_unpriority(base64strs, category_id=None):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material, category_id,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape, category_id,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    result_shape_list = []
    result_shape_list_no_box = []
    result_material_list = []
    result_material_list_no_box = []

    for m,s in zip(result_material,result_shape):
        if "盒" not in s and "其他" not in s:
            result_shape_list_no_box.append(s)
            result_material_list_no_box.append(m)

        if "其他" not in s:
            result_shape_list.append(s)
            result_material_list.append(m)


    if len(result_shape_list_no_box) > 0:
        material = Counter(result_material_list_no_box).most_common(1)[0][0]
        shape = Counter(result_shape_list_no_box).most_common(1)[0][0]
    elif len(result_shape_list) > 0:
        material = Counter(result_material_list).most_common(1)[0][0]
        shape = Counter(result_shape_list).most_common(1)[0][0]
    else:
        return "不分"

    if shape == "网兜":
        return "网兜"

    if material == "塑料膜" and shape != "包裹":
        material = "塑料"

    if shape == "冰淇淋甜筒":
        return "不分"

    if shape == "无包装" or material == "无包装":
        return "无包装"

    return material + shape


if __name__ == '__main__':
    text ="我喜欢苹果和苹果汁！"

    index = text.find("苹果")
    pass



