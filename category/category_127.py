import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity


'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,包装形式,类型,包装类型,配料
'''

Brand_list_1 = [i.strip() for i in set(open("Labels/127_brand_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/127_taste_list",encoding="utf-8").readlines())]

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

def get_taste(texts_list,product_name):
    pattern = "(\w+口?味)"
    result = []
    if len(product_name) > 4:
        result = get_info_list_by_list([[product_name,],], Taste_list)
        if len(result) == 0:
            p_res = re.compile(pattern).findall(product_name)
            if len(p_res) > 0 and p_res[0] not in ["口味","新口味"]:
                Flag = True
                for i in Taste_Abort_List:
                    if i in p_res[0]:
                        Flag = False
                        break
                if Flag:
                    result.append(p_res[0])

    if len(result) == 0:
        result = get_taste_normal(texts_list, Taste_list)
        if result != "不分":
            return result
        else:
            result = get_info_list_by_list_taste(texts_list,Taste_list)

    if len(result) == 0:
        return "不分"
    else:
        return "".join(result)

def get_type(texts_list):
    pattern_1 = "奶[芙酥盖]|雪花酥|酪酪|芙条"

    for texts in texts_list:
        for text in texts:
            if "琪玛" in text:
                return "沙琪玛"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                return "烤芙条"

    return "沙琪玛"

def get_brand(kvs_list):
    pattern = r'(生产商)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    return kv[k].replace("有限公司","").replace("有限责任公司","").replace("实业","")
    return "不分"

def get_productName_voting(kvs_list,texts_list):
    pattern_text = "[、，,]|干燥|产品类型|工艺|加工|常识|油炸型|工糕"
    pattern_pres = "的"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+沙琪玛|\w*琪玛酥)($|\()"
    pattern_2 = "(^\w*沙琪玛\w{0,6}|\w*雪花酥|\w*奶[芙酥盖]|\w*糖果|\w*奶芙[棒糕]|\w*团子|\w*酪酪|\w*奶酥|\w+芙条)($|\()"
    pattern_3 = "^沙琪玛$|\w+沙琪玛|\w{2,}\(\w*沙琪玛\)"
    pattern_4 = "[^香\W]{2,}酥|\w{2,}糕点$"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(k) < 5 and len(re.compile("[酥玛芙奶酪糖糕]").findall(kv[k])) > 0:
                        kv[k] = re.sub("^[种称]","",kv[k])
                        result_list.append(kv[k])
                    elif len(kv[k]) > 1:
                        result_list_tmp.append(kv[k])

    if len(result_list_tmp) == 0:
        product_name_tmp = "不分"
    else:
        count = Counter(result_list_tmp).most_common(2)
        product_name_tmp = count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0]:
        return count[1][0]
    return count[0][0]

def get_suger(texts_list):
    flag_1 = False
    flag_2 = False
    pattern = "[无0零]蔗糖|[未无]添加蔗糖"
    for texts in texts_list:
        for text in texts:
            if "木糖醇" in text:
                flag_1 = True
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                flag_2 = True

    result = []
    if flag_1:
        result.append("木糖醇")
    if flag_2:
        result.append("无糖")

    if len(result) == 0:
        return "不分"
    else:
        return "，".join(result)

def get_package_127(base64strs):
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
        return "铁盒"

    if material == "塑料底" or "塑料" in material:
        material = "塑料"
    elif material == "玻璃底":
        material = "玻璃"

    if shape in ["格","托盘"]:
        shape = "盒"

    if "袋" in shape:
        shape = "袋"
    elif "桶" in shape:
        shape = "桶"

    return material + shape

def category_rule_127(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    series = "不分"
    type = "不分"
    taste = "不分"
    package = "不分"
    suger = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,[],["金山","乐滋","随便","东东"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("阿萨效", "阿萨郊", brand_1)
    brand_1 = re.sub("随便沙琪玛", "随便", brand_1)


    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐", 0)

    # datasorted = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed,datasorted)

    product_name = re.sub("苦养", "苦荞", product_name)
    product_name = re.sub("鲜如", "鲜奶", product_name)
    product_name = re.sub("奶美", "奶芙", product_name)

    product_name = re.sub("^\w沙琪玛$", "沙琪玛", product_name)
    product_name = re.sub("^\w*品名称?", "", product_name)

    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    type = get_type([[product_name]])
    taste = get_taste(datasorted,product_name)
    suger = get_suger(datasorted)

    package = get_package_127(base64strs)

    result_dict['info1'] = series
    result_dict['info2'] = type
    result_dict['info3'] = taste
    result_dict['info4'] = package
    result_dict['info5'] = suger
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 5
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Tools\KWPOTools\KWPO数据获取\格式化数据-43\127'
    # root_path = r'C:\Users\zhangxuan\Desktop\00001'
    for product in os.listdir(root_path):
        image_list = []
        product = "4377420"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_127(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)