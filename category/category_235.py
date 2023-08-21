import os
import re

from util import *
from glob import glob
# from utilCapacity import get_capacity

LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/235_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/235_brand_list_2",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/235_type_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/235_taste_list",encoding="utf-8").readlines())]
suffix_name_list = [i.strip() for i in open("Labels/235_suffix_name_list",encoding="utf-8").readlines()]
absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")

Spacial_productname = []

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    result = get_info_list_by_list_taste([[product_name,],], Taste_list)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0:
            Flag = True
            for i in Taste_Abort_List:
                if i in p_res[0]:
                    Flag = False
                    break
            if Flag:
                result.append(p_res[0])

    if len(result) == 0:
        pattern = "(\w+味)\)?$"
        for texts in texts_list:
            for text in texts:
                Flag = False
                for absort in absor_taste:
                    if absort in text:
                        Flag = True
                        break
                if Flag:
                    continue
                p_res = get_info_by_pattern(text, pattern)
                if len(p_res) > 0:
                    tmp_taste = p_res[-1]
                    if len(re.compile("\d").findall(tmp_taste)) > 0:
                        continue

                    tmp_flag = True
                    for i in Taste_Abort_List:
                        if i in tmp_taste:
                            tmp_flag = False
                    if tmp_taste == "新口味": tmp_flag = False
                    if tmp_flag:
                        if len(tmp_taste) == 2:
                            if tmp_taste == "原味" or tmp_taste == "橙味" or tmp_taste == "橘味" or tmp_taste == "奶味" or tmp_taste == "咸味":
                                return tmp_taste
                        elif len(tmp_taste) < 7:
                            return tmp_taste

    if len(result) == 0:
        result = get_info_list_by_list_taste(texts_list, Taste_list)
    if len(result) > 0:
        result = list(set(result))
        return "".join(result)
    return "不分"

# 提取添加成分
def get_inside(texts_list):
    '''
    提取添加成分
    提取依据：235定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路： 偏硅酸、高锶、低纳、锌、硒
               高偏硅酸，富锶，弱碱性
    :param texts_list: 有序文本列表
    :return:
    '''
    key_1 = ['锶','硒','弱碱']
    # key_1 = ["矿物质", "高锶", '低纳','锌','硒','偏硅酸','富锶','弱碱','含氢','高硅']
    # key_1 = [ '低纳','锌','硒','偏硅酸','锶','弱碱','含氢','高硅','镁','钙','钾','纳']
    result = get_info_list_by_list(texts_list,key_1)

    if len(result) > 0:
        return "，".join(result)
    return "不分"

def get_carbon(kvs_list):
    protein_key = "营养成分表-碳水化合物"
    p = re.compile(r'(\d+\.?\d*)\s?(G|g|克)')
    for kvs in kvs_list:
        for kv in kvs:
            if protein_key in kv.keys():
                if len(p.findall(kv[protein_key])) > 0:
                    if float(p.findall(kv[protein_key])[0][0]) == 0:
                        return "无"
                    else:
                        return "有"
    return "不分"

# 提取是否有气
def get_air(texts_list):
    '''
    提取是否有气
    提取依据：235定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路： 有气/气泡，充气、含气、不分
    :param texts_list: 有序文本列表
    :param texts_list:
    :return:
    '''
    key_1 = ["含气", "充气","有气","气泡"]
    for texts in texts_list:
        for text in texts:
            for k in key_1:
                if k in text:
                    return '有汽'
    return "不分"

# 提取是否磁化
def get_cihua(texts_list):
    '''
    提取是否磁化
    提取依据：235定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路： 磁化、不分
    :param texts_list: 有序文本列表
    :return:
    '''
    key_1 = ["磁化"]
    for texts in texts_list:
        for text in texts:
            for k in key_1:
                if k in text:
                    return "磁化"
    return "不分"

#提取类型
def get_type(kvs_list,product_name,texts_list):
    '''
    提取类型
    提取依据：235定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路： 纯净水/矿泉水/山泉水等
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern = "("
    for i in Type_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"

    text = get_keyValue(kvs_list, ["配料","配料表","产品分类","原料",'配科'])
    p_res = get_info_by_pattern(text, pattern)
    if len(p_res) > 0:
        return p_res[0]

    p_res = get_info_by_pattern(product_name, pattern)
    if len(p_res) > 0:
        return p_res[0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"


def get_Capacity(kvs_list,texts_list):
    pattern = r'(净含量|净重|NETWT|重量)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\W*(ml|毫升|mL|L|kg|ML|升|g|克)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0 and p_res[0][0][0] != "0":
                        p_res = p_res[0]
                        if p_res[1] in ["ml","毫升","Ml","ML"] and float(p_res[0]) < 10:
                            continue
                        if p_res[1] in ["L","升"] and float(p_res[0]) > 25:
                            continue
                        return p_res[0] + p_res[1]

    pattern = r'(规格)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\W*(ml|毫升|mL|L|ML|升|g|克)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0 and p_res[0][0][0] != "0":
                        p_res = p_res[0]
                        if p_res[1] in ["ml", "毫升", "Ml", "ML"] and float(p_res[0]) < 10:
                            continue
                        if p_res[1] in ["L", "升"] and float(p_res[0]) > 25:
                            continue
                        return p_res[0] + p_res[1]

    pattern = r'(量$)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\W*(ml|毫升|mL|L|升|ML)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0 and p_res[0][0][0] != "0":
                        p_res = p_res[0]
                        if p_res[1] in ["ml", "毫升", "Ml", "ML"] and float(p_res[0]) < 10:
                            continue
                        if p_res[1] in ["L", "升"] and float(p_res[0]) > 25:
                            continue
                        return p_res[0] + p_res[1]

    return "不分"

def get_Capacity_bak(texts_list):
    p = re.compile(r'(\d+\.?\d*)\s?(ml|毫升|mL|ML|L$|升)')
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = p.findall(text)
            if len(p_res) > 0 and "每" not in text and p_res[0][0][0] != "0":
                p_res = p_res[0]
                tmp_list.append(p_res[0] + p_res[1])

        if len(set(tmp_list)) == 1:
            return tmp_list[0]

    p = re.compile(r'^(\d+\.?\d*)\s?(ml|毫升|mL|ML|L|升)$')
    for texts in texts_list:
        for text in texts:
            p_res = p.findall(text)
            if len(p_res) > 0 and "每" not in text and p_res[0][0][0] != "0":
                p_res = p_res[0]
                return p_res[0] + p_res[1]


    p = re.compile(r'(\d+\.?\d*)\s?(ml|毫升|mL|ML|L|升)$')
    for texts in texts_list:
        for text in texts:
            p_res = p.findall(text)
            if len(p_res) > 0 and "每" not in text and p_res[0][0][0] != "0":
                p_res = p_res[0]
                return p_res[0] + p_res[1]

    p = re.compile(r'(\d+)[mM]$')
    for texts in texts_list:
        for text in texts:
            p_res = p.findall(text)
            if len(p_res) > 0 and "每" not in text and p_res[0][0] != "0":
                return p_res[0] + "ml"

    p = re.compile(r'^(\d+)cle?$')
    for texts in texts_list:
        for text in texts:
            p_res = p.findall(text)
            if len(p_res) > 0 and "每" not in text and p_res[0][0] != "0":
                return str(float(p_res[0])*10) + "ml"

    return "不分"

def get_Capacity_2(texts_list):
    pattern = r'\d+\.?\d*\D*[l升L]\D{0,3}\d+\D*[包袋罐瓶听支]装?\)?'
    pattern_2 = r'(\d+\.?\d*)\W*(毫升|ml|mL|ML|L|升)\D{0,3}(\d+)\D*[包袋罐瓶听支]装?\)?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if p_res_2[1] in ["升", "L"] and float(p_res_2[0]) > 25:
                                continue
                            if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0] or float(p_res_2[2]) in [4.0,6.0,8.0,10.0,12.0,15.0,18.0,24.0,42.0,48.0]:
                                return ("%s%s" % (str(float(p_res_2[0]) * float(p_res_2[2])), p_res_2[1])), re.sub(u"\)", "",p_res[0])
                            else:
                                return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[l升L][*xX]\d+[包袋罐瓶听支\)]?$'
    pattern_2 = r'(\d+\.?\d*)\W*(毫升|ml|mL|ML|L|升)[*xX](\d+)[包袋罐瓶听支\)]?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if p_res_2[1] in ["升", "L"] and float(p_res_2[0]) > 25:
                                continue
                            if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                return ("%s%s" % (str(float(p_res_2[0]) * float(p_res_2[2])), p_res_2[1])), re.sub(u"\)", "",p_res[0])
                            else:
                                return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[l升L][*xX]\d+[包袋罐瓶听支\)]?'
    pattern_2 = r'(\d+\.?\d*)\W*(毫升|ml|mL|ML|L|升)[*xX](\d+)[包袋罐瓶听支\)]?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if p_res_2[1] in ["升", "L"] and float(p_res_2[0]) > 25:
                                continue
                            if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                return ("%s%s" % (str(float(p_res_2[0]) * float(p_res_2[2])), p_res_2[1])), re.sub(u"\)", "",p_res[0])
                            else:
                                return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[l升L]\d+[包袋罐瓶听支\)]?$'
    pattern_2 = r'(\d+\.?\d*)\W*(毫升|ml|mL|ML|L|升)(\d+)[包袋罐瓶听支\)]?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if float(p_res_2[2]) in [4.0,6.0,8.0,10.0,12.0,15.0,18.0,24.0,42.0,48.0]:
                                if  p_res_2[1] in ["升","L"] and float(p_res_2[0]) > 25:
                                    continue
                                return ("%s%s" % (str(float(p_res_2[0]) * float(p_res_2[2])), p_res_2[1])), re.sub(u"\)", "",p_res[0])

    pattern = r'\d+[包袋罐瓶听支]?[*xX]\d+\D*[l升L]'
    pattern_2 = r'(\d+)[包袋罐瓶听支]?[*xX](\d+)\W*(毫升|ml|mL|ML|L|升)'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if float(p_res_2[0]) in [4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 18.0, 24.0,42.0,48.0]:
                                if  p_res_2[2] in ["升","L"] and float(p_res_2[1]) > 25:
                                    continue
                                return ("%s%s" % (str(float(p_res_2[0]) * float(p_res_2[1])), p_res_2[2])), re.sub(u"\)", "",p_res[0])
    return "不分","不分"

def get_Capacity_2_bak(texts_list):
    p_bak = re.compile(r'(\d+)(\s?瓶装)')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 48:
                    return p_res[0] + p_res[1]
    return "不分"

#提取适用人群
def get_suitpeople(texts_list):
    '''
    提取适用人群
    提取依据：235定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：选项：儿童/婴儿/婴幼儿/孕妇/孕婴/其它（请注明）
    :param texts_list: 有序文本列表
    :return:
    '''
    # 适合婴幼儿和准妈妈
    pattern = "适合(婴幼儿和准妈妈|婴幼儿|准妈妈|孕婴|儿童|婴儿|孕妇|baby|BABY)"
    pattern1 = "婴幼儿和准妈妈|婴幼儿|准妈妈|孕婴|儿童|婴儿|孕妇|baby|BABY"
    for texts in texts_list:
        text_origi = ''.join(texts)
        if 'baby' in text_origi and 'Kiaora' in text_origi:
            return '宝宝'
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res)>0:
                if p_res[0]=='婴幼儿和准妈妈':
                    return '孕婴'
                return p_res[0]
            else:
                p_res = get_info_by_pattern(text, pattern1)
                if len(p_res) > 0:
                    if p_res[0] == '婴幼儿和准妈妈':
                        return '孕婴'
                    return p_res[0]


    return '不分'

#取出所有品牌，目的是为了刷选品牌用
def get_brand_list_test(texts_list):
    brand_1_list = []
    brand_2 = []
    for texts in texts_list:
        text_str = "".join(texts)
        text_str_ori = ",".join(texts)
        for bb in Brand_list_1:
            if bb in text_str :
                if len(bb) > 2 and len(re.compile("[\u4e00-\u9fa5]").findall(bb)) > 0:
                    brand_1_list.append(bb)
                elif len(re.compile("(,|^)%s($|,)"%(",".join(list(bb)))).findall(text_str_ori)) > 0:
                    brand_1_list.append(bb)

        for text in texts:
            for b1 in Brand_list_1:
                if b1.upper() in text.upper() or b1 in text:
                    brand_1_list.append(b1)

    if len(brand_2) > 0:
        brand_2 = ",".join(list(set(brand_2)))
    else:
        brand_2 = "不分"

    if len(brand_1_list) == 0:
        brand_1 = "不分"
    else:
        brand_1_list.sort(key=len,reverse=True)
        count = Counter(brand_1_list).most_common(6)
        brand_1 = ",".join([i[0] for i in count])
    return brand_1,brand_2

#提取商品全称
def get_productName_voting(texts_list):
    result_list = []
    abort_list = ['指定','市']
    pre_result_list = []
    pattern_1 = "("
    for i in suffix_name_list:
        pattern_1 += "\w+" + i + "|"

    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1.replace("+", "*")[:-1]


    for texts in texts_list:
        for text in texts:
            flag = True
            for it in abort_list:
                if it in text:
                    flag = False
                    break
            if flag:
                p_res = get_info_by_pattern(text, pattern_1)
                if len(p_res) > 0 and '的' not in p_res[0]:
                    result_list.append(p_res[0])
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        if len(pre_result_list) > 0:
            return pre_result_list[0]
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            flag = True
            for it in abort_list:
                if it in text:
                    flag = False
                    break

            if flag:
                p_res = get_info_by_pattern(text, pattern_2)
                if len(p_res) > 0 and '的' not in p_res[0]:
                    result_list.append(p_res[0])
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        if len(pre_result_list) > 0:
            return pre_result_list[0]
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return '不分'

def get_package_235(base64strs):
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

    if "玻璃底" in result_material:
        return "玻璃瓶"
    elif "塑料底" in result_material:
        return "塑料瓶"

    if material == "玻璃":
        return "玻璃瓶"
    if "桶" in shape:
        return "桶"

    return "塑料瓶"

def category_rule_235(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    taste = "不分"
    inside = "不分"
    package = "不分"
    store = "不分"
    type = "不分"
    air = "不分"
    cihua = "不分"
    yinshuiji = "非饮水机专用"
    #适用人群
    suitpeople = '不分'

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], [], [])
        brand_1 = re.sub('矿500', "矿享500", brand_1)

    # product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)
        product_name = re.sub('^\d+ml', "", product_name)
        product_name = re.sub('^\d+毫升', "", product_name)
        product_name = re.sub('^\d+L', "", product_name)
        product_name = re.sub('矿500', "矿享500", product_name)

    if product_name != '不分' and brand_1 != '不分' and brand_1.title() in product_name.title():
        product_name = product_name.title().replace(brand_1.title(), '')

    capcity_1 = get_Capacity(dataprocessed, datasorted)
    capcity_1_bak, capcity_2 = get_Capacity_2(datasorted)
    if capcity_1 != "不分":
        try:
            num = float(re.compile("\d+").findall(capcity_1)[0])
            if "毫升" in capcity_1 or "m" in capcity_1 or "M" in capcity_1:
                if num > 12000:
                    yinshuiji = "饮水机专用"
                    package = "桶"
            elif "升" in capcity_1 or "L" in capcity_1:
                if num > 12:
                    yinshuiji = "饮水机专用"
                    package = "桶"
        except:
            pass

    if capcity_1_bak != "不分" and capcity_1_bak[0] != "0":
        capcity_1 = capcity_1_bak
    if capcity_1 == "不分":
        capcity_1 = get_Capacity_bak(datasorted)
    if capcity_2 == "不分":
        capcity_2 = get_Capacity_2_bak(datasorted)
    #
    # capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "ml|毫升|mL|L|kg|ML|升|g|克", "包袋罐瓶听支", 0)
    # type = get_type([[product_name,],])
    # if type == "不分" :
    #     type = get_type(datasorted)
    type = get_type(dataprocessed, product_name, datasorted)
    # type = re.sub("饮用水", "纯净水", type)

    air = get_air(datasorted)
    cihua = get_cihua(datasorted)
    inside = get_inside(datasorted)
    taste = get_taste(datasorted,product_name)

    # # #正式用
    if package == "不分":
        package = get_package_235(base64strs)


    product_name = re.sub("大然", "天然", product_name)

    product_name = re.sub("^\w*类别", "", product_name)
    product_name = re.sub("配料\w*$", "", product_name)
    product_name = re.sub("\d+$", "", product_name)
    product_name = re.sub("^[喝吃用]", "", product_name)
    if len(product_name) == 0:
        product_name='饮用水'

    suitpeople = get_suitpeople(datasorted)
    # 包装形式
    result_dict['info1'] = package
    # 口味
    result_dict['info2'] = taste
    # 类型
    result_dict['info3'] = type
    # 添加成分
    result_dict['info4'] = inside
    # 是否有汽
    result_dict['info5'] = air
    # 是否磁化
    result_dict['info6'] = cihua
    # 是否饮水机专用
    result_dict['info7'] = yinshuiji
    # 适用人群
    result_dict['info8'] = suitpeople

    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])
    real_use_num = 8
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\235-包装饮用水'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3124131"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_235(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)