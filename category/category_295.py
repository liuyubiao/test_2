import os
import re
import json

from collections import Counter
from util import *
from glob import glob
from category_101 import get_EXP
from utilCapacity import get_capacity

LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/295_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/295_brand_list_2",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/295_taste_list",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/295_type_list",encoding="utf-8").readlines())]

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")

Spacial_productname = []
Wort_concentration = ["6","7"]

def get_taste(texts_list,product_name):
    pattern = "([\u4e00-\u9fa5]+味)"
    result = []
    if len(product_name) > 4:
        result = get_info_list_by_list([[product_name,],], Taste_list)
        if len(result) == 0:
            p_res = re.compile(pattern).findall(product_name)
            if len(p_res) > 0 and p_res[0] not in ["风味","口味","新口味","山如雪般绵密泡味","原汁原味","俄罗斯风味","梅元味"]:
                Flag = True
                for i in Taste_Abort_List:
                    if i in p_res[0]:
                        Flag = False
                        break
                if Flag:
                    result.append(p_res[0])

    if len(result) == 0:
        return get_taste_normal(texts_list, Taste_list)
    else:
        # result = list(set(result))
        return "".join(result)
    # pattern = "("
    # for i in Taste_list:
    #     pattern += i + "|"
    # pattern = pattern[:-1] + ")"
    # for texts in texts_list:
    #     for text in texts:
    #         p_res = get_info_by_pattern(text, pattern)
    #         if len(p_res) > 0:
    #             return p_res[0]
    #
    # return "不分"

def get_type(texts_list):
    pattern = "("
    for i in Type_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 :
                if p_res[0] == "生啤" and ("纯生啤" in text or "蓝生啤" in text):
                    continue
                if p_res[0] == "酸啤" and ("玻尿酸啤" in text or "精酸啤" in text or "古师酸啤" in text):
                    continue
                if p_res[0] == "醇啤" and ("无醇啤" in text or "纸醇啤" in text):
                    continue
                return p_res[0]

    return "不分"

def get_maiyazhi(kvs_list,texts_list):
    pattern = "(\d+\.?\d*).?[Pp]$|(\d+\.?\d*).?[Pp][^a-zA-Z0-9]"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                p_res = p_res[0][0] if p_res[0][0] != "" else p_res[0][1]
                if float(p_res) > 20 and float(p_res) < 200:
                    return str(float(p_res) / 10.0)
                elif float(p_res) > 3 and float(p_res) < 20:
                    return p_res

    result = get_keyValue(kvs_list, ["汁浓度"])
    try:
        result = re.compile("(\d+\.?\d*)").findall(result)[0]
    except:
        result = "不分"

    if result != "不分":
        if float(result) > 20 and float(result) < 200:
            return str(float(result) / 10.0)
        elif float(result) > 3 and float(result) < 20:
            return result

    return "不分"

def get_productName_voting(texts_list):
    result_list = []

    # pattern_absort = "^中山|^[水高本收空请进浙点及门生时工美优赣安志农上]|^德[恩图]|^特种|孕妇|工业|[饮喝]|德姆"
    pattern_absort = "^中山|^[请将用把优水]|^特种|孕妇|工业|[饮喝的]"
    pattern_text = "[、，,]|公司"
    pattern_0 = "(\w*纯生态|\w*新动8°|\w*蔓越莓味|\w*好兄弟|\w*雪花|\w*黄河之水|\w*龙井小麦|\w*国纯·金冠|\w*金麦|\w*原汁麦|\w*鲜啤2022)"
    pattern_1 = "(\w+啤酒|\w+原浆|\w+纯生)$"
    pattern_2 = "(\w+啤酒|\w+原浆|\w+纯生)"
    pattern_3 = "\w+[酒啤]$"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_0)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if "啤" not in count[0][0] and "酒" not in count[0][0]:
            return count[0][0] + "啤酒"
        else:
            return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if "啤" not in count[0][0] and "酒" not in count[0][0]:
            return count[0][0] + "啤酒"
        else:
            return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if "啤" not in count[0][0] and "酒" not in count[0][0]:
            return count[0][0] + "啤酒"
        else:
            return count[0][0]

    return "不分"

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

def get_package_295(base64strs):
    '''
    1.塑料瓶：塑料包装材质的口小腹大的器皿
    2.玻璃瓶：玻璃包装材质的口小腹大的器皿
    3.听：马口铁密封成筒状的器皿，如罐装、易拉罐
    4.塑料袋：外包装为塑料袋、纸袋等袋形式的包装
    5.铁桶：用金属材料制成的盛东西的器具，有提梁
    6.塑料桶：用塑料材料制成的盛东西的器具，有提梁
    7.铝瓶：铝包装材质的口小腹大的器皿
    8.不锈钢罐：不锈钢包装材质的口小腹大的器皿
    9.细长听：小于等于350毫升，且人工判断为细长型的听装产品归为细长听
    :param base64strs:
    :return:
    '''
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    result_material = package_filter(result_material,["纸"])
    result_shape = package_filter(result_shape,["盒","格"])

    if len(result_material) == 0 or len(result_shape) == 0:
        return "听"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if "玻璃底" in result_material:
        return "玻璃瓶"
    elif "塑料底" in result_material:
        material ="塑料"

    if material == "玻璃":
        return "玻璃瓶"
    elif "塑料" in material:
        if "瓶" in shape:
            return "塑料瓶"
        else:
            return "塑料桶"
    elif material == "金属":
        if shape == "瓶":
            return "铝瓶"
        elif "桶" in shape:
            return "铁桶"
        elif shape == "细长罐":
            return "细长听"
        return "听"

    return "听"

def category_rule_295(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    taste = "不分"
    package = "不分"
    type = "不分"
    maiyazhi = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # 品牌
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1,
                                          [],["HITE","英皇","DALI","1551","1916","1595","1513","ABC",
                                              "杠","RIO","麒麟一番","一番榨","金星啤酒","科罗拉","金星","欧加","吉安","SPP","星威","国科",
                                              "BLUERIBBON","锦博士"], [])

    brand_1 = re.sub("喜芝博","嘉芝博",brand_1)
    brand_1 = re.sub("ZENST","ZENZT",brand_1)
    brand_1 = re.sub("茅汨","芽汨",brand_1)
    brand_1 = re.sub("WEUJIXIONG","WEIJIXIONG",brand_1)
    brand_1 = re.sub("芳德巴林","劳德巴赫",brand_1)
    brand_1 = re.sub("头道美","头道麦",brand_1)
    brand_1 = re.sub("有它必胜", "有TA必胜", brand_1)
    brand_1 = re.sub("勇闯天涯", "雪花", brand_1)
    brand_1 = re.sub("BAIRENBAHE", "拜仁巴赫", brand_1,re.IGNORECASE)
    brand_1 = re.sub("BLACKBEAUTY", "黑美人BLACK BEAUTY", brand_1, re.IGNORECASE)

    product_name = get_keyValue(dataprocessed, ["品名"])
    if "酒" not in product_name and "啤" not in product_name and "纯生" not in product_name :
        product_name = "不分"
    if "饮" in product_name or "喝" in product_name or "m1" in product_name or "制品" in product_name or "原料" in product_name or "ProductName" in product_name or "浓度" in product_name:
        product_name = "不分"
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)


    product_name = re.sub("霞津","雪津",product_name)
    product_name = re.sub("[自日]啤酒","白啤酒",product_name)
    product_name = re.sub("膏大师","青大师",product_name)
    product_name = re.sub("头道美","头道麦",product_name)
    product_name = re.sub("德國保拉纳柏能啤酒","德國保拉纳柏龍啤酒",product_name)
    product_name = re.sub("构龙果","柏龙果",product_name)
    product_name = re.sub("浪溪","浪漫",product_name)
    product_name = re.sub("国纯·金冠","超纯·金冠",product_name)
    product_name = re.sub("丁妈","丁姆",product_name)
    product_name = re.sub("香石榨","番石榴",product_name)

    # 重容量
    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "ml|毫[升元开]|mL|L|[升元开]|ML", "袋盒桶罐瓶", 1)
    capcity_2 = re.sub("[元开]", "升", capcity_2)
    capcity_1 = re.sub("[元开]", "升", capcity_1)

    # 口味
    taste = get_taste(datasorted, product_name)

    #类型
    type = get_type([[product_name,],])
    if type == "不分" :
        type = get_type(datasorted)
    if taste in FRUIT_LIST:
        type = "果啤"

    #麦芽浓度
    maiyazhi = get_maiyazhi(dataprocessed,datasorted)

    #包装-测试
    image_list = ["/data/zhangxuan/images/43-product-images" + i.split("ShangPin")[-1].replace("\\", "/") for i in base64strs]
    package = get_package_295(image_list)
    #包装-正式
    # package = get_package_295(base64strs)
    if package == "细长听":
        if str(capcity_1) > "350ml" or str(capcity_1) == "1L" or str(capcity_1) == "12L" or str(capcity_1) == "1500.0ml" or str(capcity_1) == "12000.0ML":
            package = "听"

    if product_name == "不分":
        if brand_1 != "不分":
            product_name = brand_1 + "啤酒"
        else:
            product_name = "啤酒"

    product_name = re.sub("白威", "百威", product_name)
    product_name = re.sub("味酒", "啤酒", product_name)
    product_name = re.sub("^\w啤酒", "啤酒", product_name)
    product_name = re.sub("^\w扎啤", "扎啤", product_name)
    product_name = re.sub("^\w原浆", "原浆", product_name)
    product_name = re.sub("^\w纯生", "纯生", product_name)
    product_name = re.sub("啤酒\w$", "啤酒", product_name)

    result_dict['info1'] = type
    result_dict['info2'] = package
    result_dict['info3'] = taste
    result_dict['info4'] = maiyazhi
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\295-啤酒'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3056263"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_295(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)