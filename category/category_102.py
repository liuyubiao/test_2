import os
import re

from util import *
from glob import glob
from category_101 import get_EXP,get_EXP_all,get_EXP_store
from utilCapacity import get_capacity

'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,包装形式,类型,包装类型,配料
'''

Brand_list_1 = [i.strip() for i in set(open("Labels/102_brand_list_1",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/102_type_list",encoding="utf-8").readlines())]
Type_list.sort(key=len,reverse=True)
# 通常来看需要20个非通用属性
LIMIT_NUM = 20

def get_type(texts_list):
    pattern = "("
    for i in Type_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

def get_productName_voting(texts_list):
    result_list = []
    pattern_1 = "("
    for i in Type_list:
        pattern_1 += "[\w\.]+" + i + "|"
    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1[:-1].replace("+","*")
    pattern_3 = "\w+菜心?"

    for texts in texts_list:
        # print(1)
        for text in texts:
            # print(1)
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                if "西兰" in p_res[0] and "新西兰" in text:
                    continue
                result_list.append(p_res[0])
                continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if "的" not in count[0][0]:
            return count[0][0]
        elif len(count) == 2:
            return count[1][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if "西兰" in p_res[0] and "新西兰" in text:
                    continue
                result_list.append(p_res[0])
                continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if "的" not in count[0][0]:
            return count[0][0]
        elif len(count) == 2:
            return count[1][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if "西兰" in p_res[0] and "新西兰" in text:
                    continue
                result_list.append(p_res[0])
                continue

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if "的" not in count[0][0] or len(count) == 1:
        return count[0][0]
    else:
        return count[1][0]

def get_EXP_last(store,EXP):
    store = re.sub("^-", "零下", store)
    store = re.sub("[度C]?以下", "度以下", store)
    store = re.sub("带温", "常温", store)
    store = re.sub("C", "度", store)
    store = re.sub("下", "度", store)
    EXP = re.sub("^-", "零下", EXP)
    EXP = re.sub("[度C]?以下", "度以下", EXP)
    EXP = re.sub("0[-至]4[度C]?", "0至4度", EXP)
    EXP = re.sub("0[-至]5[度C]?", "0至5度", EXP)
    EXP = re.sub("C度", "度", EXP)
    if len(re.compile("\d$").findall(store)) > 0:
        store += "度"

    store = "零下18度以下冷冻保存" if store == "冷冻" or store == "不分" else store
    if store != "不分":
        if EXP != "不分" and len(
                re.compile(r'(-?\d+[-至]\d+[度C]|零下\d+以?下?|-\d+[度C]?以?下?|冷藏|冷冻|常温)').findall(EXP)) == 0:
            EXP = store + EXP
    if EXP == '不分':
        EXP = store
    return EXP

def get_package_102(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    result_shape = package_filter(result_shape, ["瓶", "杯", "桶", "罐"])

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    if "真空袋" in result_shape:
        return "真空塑料袋"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if shape == "网兜":
        return "网兜"
    elif shape == "薄膜":
        return "塑料薄膜"

    if material == "塑料底" or "塑料" in material:
        material = "塑料"
    elif material == "玻璃底":
        material = "玻璃"

    if "袋" in shape:
        shape = "袋"
    elif "瓶" in shape:
        shape = "瓶"
    elif "桶" in shape or "罐" in shape:
        shape = "桶"
    elif shape in ["礼包","碗"]:
        shape = "盒"

    return material + shape

def category_rule_102(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    Brand_replace_dict_1={'赞汉':'赞叹','春冰源':'春沐源','義皇':'羲皇','小苏之选':'小荔之选','一粒考思':'一粒考恩','明剪':'明隽',"ALDI":"奥乐齐ALDI"}
    product_replace_dict = {'柔芽': '桑芽', '缘豆': '绿豆', '鲍茄': '鲍菇', '菁豆': '青豆', '蟹味菜': '蟹味菇','大红辣':'大红椒','楼桃':'樱桃',
                            '特机':'有机','香恋':'香葱','清能':'清脆','撬玉米':'糯玉米','蛋豆':'蚕豆',"食马":"盒马"}
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    EXP = "不分"
    type = "不分"
    package = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed,["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], [], [])

    #
    for key in Brand_replace_dict_1.keys():
        brand_1 = re.sub(key, Brand_replace_dict_1.get(key), brand_1)


    product_name = get_keyValue(dataprocessed, ["品名"])
    if len(product_name) <=1:
        product_name = "不分"
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)

    for key in product_replace_dict.keys():
        product_name = re.sub(key, product_replace_dict.get(key), product_name)

    product_name = re.sub("^[品晶]名称?","",product_name)

    if product_name != "不分":
        for i in Type_list:
            if i in product_name:
                type = i
                break
        if type == "不分":
            type = get_type(datasorted)

    # if EXP == "不分":
    #     EXP = get_EXP(dataprocessed,datasorted)
    EXP = get_EXP_all(datasorted)
    if EXP != "不分":
        EXP = re.sub("^-", "零下", EXP)
        EXP = re.sub("[度C]", "度", EXP)

    if EXP == "不分":
        store = get_EXP_store(dataprocessed, datasorted)
        EXP = get_EXP(dataprocessed, datasorted)
        EXP = get_EXP_last(store, EXP)

    capcity_1 ,capcity_2= get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐粒个", 0)

    type = type if type != "松花" else "花菜"

    try:
        product_name = re.compile("[\w\.]*[\u4e00-\u9fa5]").findall(product_name)[0]
    except:
        pass

    package = get_package_102(base64strs)

    result_dict['info1'] = package
    result_dict['info2'] = EXP
    result_dict['info3'] = type
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    real_use_num = 3
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = ""

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_1\102-蔬菜'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3110739"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_102(image_list)
        with open(os.path.join(root_path, product) + r'\%s_new.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)