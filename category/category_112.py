import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity
'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,包装形式,类型,包装类型,配料
'''

Brand_list_1 = [i.strip() for i in set(open("Labels/112_brand_list_1",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/112_type_list",encoding="utf-8").readlines())]
Type_list.sort(key=len,reverse=True)
Taste_list = [i.strip() for i in set(open("Labels/112_taste_list",encoding="utf-8").readlines())]

Brand_list_1 = sorted(list(set(Brand_list_1)), key=len)

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    result = get_info_list_by_list([[product_name,],], Taste_list)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0 and p_res[0] not in ["口味","新口味","风味"]:
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

def get_info_by_RE(texts_list,serchList):
    pattern = "("
    for i in serchList:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[-1]
    return "不分"

def get_info_by_list(texts_list,serchList):
    result = []
    for texts in texts_list:
        for text in texts:
            for t in serchList:
                if t in text:
                    result.append(t)
    if len(result) > 0:
        result = list(set(result))
        return "".join(result)
    return "不分"

def get_brand(kvs_list):
    pattern = r'(委托[方商]$|生产商$|制造商$)'
    brand = "不分"
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0 and len(re.compile("集团|有限|责任|公司|实业").findall(kv[k])) > 0:
                    brand = kv[k]
    # brand.replace("集团", "").replace("有限", "").replace("责任", "").replace("公司", "").replace("实业", "")
    return brand

def get_productName(texts_list):
    pattern = "(\w*调味酱|\w*沙司"
    for i in Type_list:
        pattern += "\w*" + i + "|"
    pattern = pattern[:-1] + ")$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = pattern[:-1]
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "\w+[酱|蜜]"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]
    return "不分"

def get_productName_voting(kvs_list,texts_list):
    pattern_res = "[的是用不]|本品|了解|如果|饮茶|一勺"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+调味酱|\w+沙司|\w+淡奶|\w+柠檬茶|\w+青梅茶|\w+树蜜|\w+雪梨膏|\w+芝士片|"
    for i in Type_list:
        pattern_1 += "\w+" + i + "|"
    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1[:-1].replace("+","*")
    pattern_3 = "[\\\/\w]+[酱蜜膏茶]"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]) and len(k) < 6:
                    if len(re.compile("[蜜酱料乳奶茶汁油膏]|芝士片").findall(kv[k])) == 0 and "沙司" not in kv[k]:
                        result_list_tmp.append(kv[k])
                    else:
                        result_list.append(kv[k])
    if len(result_list_tmp) == 0:
        product_name_tmp = "不分"
    else:
        count = Counter(result_list_tmp).most_common(2)
        product_name_tmp =  count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                if len(re.compile(pattern_res).findall(p_res[0])) == 0 :
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if len(re.compile(pattern_res).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 2 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    if product_name_tmp != "不分":
        return product_name_tmp
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if len(re.compile(pattern_res).findall(p_res[0])) == 0 and "甜蜜" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) == 2 and count[0][0] in count[1][0]:
        return count[1][0]
    return count[0][0]

def get_type(texts_list):
    result_list = []
    pattern_0 = "柚子蜜|柚子茶|柠檬茶|青梅茶"
    pattern_1 = "(淡奶$|"
    for i in Type_list:
        pattern_1 += i + "|"
    pattern_1 = pattern_1[:-1] + ")"
    pattern_2 = "番茄|黑椒|麻汁"
    pattern_3 = "(果味?酱|"
    for i in FRUIT_LIST:
        pattern_3 += i + "[酱膏]|"
    pattern_3 = pattern_3[:-1] + ")"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_0)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "是" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                if "的" not in p_res[-1] and "是" not in p_res[-1]:
                    result_list.append(p_res[-1])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if "的" not in p_res[-1] and "是" not in p_res[-1]:
                    result_list.append(p_res[-1] + "酱")
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "是" not in p_res[0]:
                    result_list.append("果酱")
                    continue

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    return count[0][0]

def get_Capacity(kvs_list,texts_list):
    kvs_list.sort(key=len, reverse=False)
    pattern = r'(净含量?|净重|[Nn][Ee][Tt][Ww]|重量)'
    result_list = []
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\s?(G|g|克|[千干]克|kg|KG|斤|公斤|升|毫升|ML|ml|mL|L)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克","kg","KG","斤","公斤","升","L","干克"]:
                                if float(p_res[0]) <= 5:
                                    if p_res[1] == "干克":
                                        result_list.append(p_res[0] + "千克")
                                    else:
                                        result_list.append(p_res[0] + p_res[1])
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= 1:
                                    result_list.append(p_res[0] + p_res[1])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    pattern = r'(规格)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\s?(G|g|克|千克|kg|KG|斤|公斤|升|毫升|ML|ml|mL|L)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克", "kg", "KG", "斤", "公斤", "升", "L"]:
                                if float(p_res[0]) <= 5:
                                    return p_res[0] + p_res[1]
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= 1:
                                    return p_res[0] + p_res[1]

    return "不分"

def get_Capacity_bak(texts_list):
    p = re.compile(r'(\d+\.?\d*)\s?(G|Kg|g|kg|KG|克|千克|ml|ML|mL|毫升|升)')
    for texts in texts_list:
        tmp_list = []
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0 and float(p_res[0][0]) < 10000:
                if not isNutritionalTable(text, texts, index):
                    continue
                tmp_list.append(p_res[0][0] + p_res[0][1])

        if len(tmp_list) == 1:
            return tmp_list[0]

    result_list = []
    p = re.compile(r'(\d+\.?\d*)\s?(G|Kg|g|kg|KG|克|千克|ml|ML|mL|毫升|升)')
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                if not isNutritionalTable(text, texts, index):
                    continue
                p_res = p_res[0]
                if p_res[1] in ["Kg","kg","KG","千克","升","L"]:
                    if float(p_res[0]) <= 30:
                        result_list.append(p_res[0] + p_res[1])
                else:
                    if float(p_res[0]) < 5000 and "." not in p_res[0]:
                        result_list.append(p_res[0] + p_res[1])

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    return count[0][0]

def get_Capacity_bak_2(kvs_list):
    pattern = r'(净含量?|净重|[Nn][Ee][Tt][Ww]|重量)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)($|[k千]\w?$)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if "k" in p_res[1] or "千" in p_res[1]:
                                if float(p_res[0]) <= 5:
                                    return p_res[0] + "kg"
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= 10:
                                    return p_res[0] + "克"
    return "不分"

def get_Capacity_2(kvs_list,texts_list):
    pattern = r'(净含量?|净重|[Nn][Ee][Tt][Ww]|重量|规格)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    if len(re.compile("\d+[克gG]\d+[克gG]").findall(kv[k])) > 0 or "装" in kv[k]:
                        continue
                    pattern = r'(\d+\.?\d*)\s?(G|g|克|千克|kg|KG|斤|公斤|升|毫升|ML|ml|mL|L)(\d+)[\u4e00-\u9fa5]{0,2}\)?$'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0" and p_res[2][0] != "0":
                            if p_res[1] in ["千克", "kg", "KG", "斤", "公斤", "升", "L"]:
                                if float(p_res[0]) <= 30 and float(p_res[2]) <= 30:
                                    return str(int(float(p_res[0]) * int(p_res[2]))) + p_res[1], p_res[0] + p_res[1] + "*" + p_res[2]
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= 1 and float(p_res[2]) <= 50:
                                    return str(int(float(p_res[0]) * int(p_res[2]))) + p_res[1], p_res[0] + p_res[1] + "*" + p_res[2]

    pattern = r'^(净含量?|净重|^[\u4e00-\u9fa5]?含量$|[Nn][Ee][Tt][Ww]|重量):?$'
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res_1 = get_info_by_pattern(text, pattern)
            total_len = len(texts)
            if len(p_res_1) > 0:
                for i in [-3, -2, -1, 1, 2, 3]:
                    if index + i >= 0 and index + i < total_len:
                        pattern_tmp = r'(\d+\.?\d*)\s?(G|g|克|千克|kg|KG|斤|公斤|升|毫升|ML|ml|mL|L)(\d+)[\u4e00-\u9fa5]{0,2}\)?$'
                        p_res_tmp = re.compile(pattern_tmp).findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            if len(re.compile("\d+[克gG]\d+[克gG]").findall(texts[index + i])) > 0 or "装" in texts[index + i]:
                                continue
                            p_res_tmp = p_res_tmp[0]
                            if p_res_tmp[0][0] != "0" and p_res_tmp[2][0] != "0":
                                if p_res_tmp[1] in ["千克", "kg", "KG", "斤", "公斤", "升", "L"]:
                                    if float(p_res_tmp[0]) <= 30 and float(p_res_tmp[2]) <= 30:
                                        return str(int(float(p_res_tmp[0]) * int(p_res_tmp[2]))) + p_res_tmp[1], p_res_tmp[0] + p_res_tmp[1] + "*" + p_res_tmp[2]
                                else:
                                    if float(p_res_tmp[0]) < 5000 and float(p_res_tmp[0]) >= 1 and float(p_res_tmp[2]) <= 50:
                                        return str(int(float(p_res_tmp[0]) * int(p_res_tmp[2]))) + p_res_tmp[1], p_res_tmp[0] + p_res_tmp[1] + "*" + p_res_tmp[2]

    pattern = r'\d+\.?\d*\D*[g克斤lL升]\D{0,3}\d+\D?[包袋盒罐支杯粒]装?\)?'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克|千克|kg|斤|公斤|ml|ML|mL|毫升|升)\D{0,3}(\d+)\D?[包袋盒罐支杯粒]装?\)?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            if len(re.split("[*xX]\d",text)) > 2:
                continue
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    unit = p_res_2[1]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if unit in ["Kg","kg","KG","千克","升","L"] and float(p_res_2[0]) <= 30:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0] or len(re.compile("/[包袋盒罐支杯粒]").findall(p_res[0])) > 0:
                                    return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "", p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                            elif float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000 :
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0] or len(re.compile("/[包袋盒罐支杯粒]").findall(p_res[0])) > 0:
                                    return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "", p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[g克斤lL升][*xX]\d+[包袋盒罐支杯粒\)]?'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克|千克|kg|斤|公斤|ml|ML|mL|毫升|升)[*xX](\d+)[包袋盒罐支杯粒\)]?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            if len(re.split("[*xX]\d",text)) > 2:
                continue
            p_res = p.findall(text)
            if len(p_res) > 0:
                if len(re.compile("\d+\.\d+克\([\dg]\)").findall(text)) > 0:
                    continue
                if "(9)" in text:
                    continue
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    unit = p_res_2[1]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if unit in ["Kg","kg","KG","千克","升","L"] and float(
                                    p_res_2[0]) <= 30:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                            elif float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    return "不分","不分"

def get_Capacity_2_bak(texts_list):
    p_bak = re.compile(r'(\d+)(\s?[包袋罐]装)')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1]

    p_bak = re.compile(r'(\d+)([包袋罐])\w*(装)$')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1] + p_res[2]

    p_bak = re.compile(r'内[装含](\d+)(小?[包袋罐])')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return "内装"+ p_res[0] + p_res[1]
    return "不分"

def category_rule_112(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    taste = "不分"
    type = "不分"
    package = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    peanutType = "不分"
    energy = "不分"

    brand_tmp = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed,["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,[],["太行山","屯河","MEA","自然流露","清美","农垦","口味全","好熟悉"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    # product_name = get_keyValue(dataprocessed, ["品名"])
    # if "蜜" not in product_name and "酱" not in product_name and "料" not in product_name and "乳" not in product_name and "奶" not in product_name and "沙司" not in product_name:
    #     product_name = "不分"
    if product_name == "不分":
        product_name = get_productName_voting(dataprocessed,datasorted)

    # if (brand_1 == "不分" or product_name == "不分") and uie_obj is not None:
    #     uie_brand,uie_productname = uie_obj.get_info_UIE(datasorted)
    #     brand_1 = brand_1 if brand_1 != "不分" else uie_brand
    #     product_name = product_name if product_name != "不分" else uie_productname

    product_name = re.sub("艺麻", "芝麻", product_name)
    product_name = re.sub("[蜂峰精][密蜜]", "蜂蜜", product_name)
    product_name = re.sub("[极搬]树", "椴树", product_name)
    product_name = re.sub("抽子", "柚子", product_name)
    product_name = re.sub("楼子", "榛子", product_name)

    product_name = re.sub("^[树花]蜂蜜", "蜂蜜", product_name)
    product_name = re.sub("^品?名1?", "", product_name)

    product_name = re.sub("^\w?\W+", "", product_name)

    capcity_1 ,capcity_2= get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤|升|毫[开元升]|ML|ml|mL|L", "瓶包袋罐", 2)

    # capcity_1 = get_Capacity(dataprocessed, datasorted)
    # capcity_1_bak, capcity_2 = get_Capacity_2(dataprocessed,datasorted)
    # if capcity_1_bak != "不分" and capcity_1_bak[0] != "0":
    #     capcity_1 = capcity_1_bak
    # if capcity_1 == "不分":
    #     capcity_1 = get_Capacity_bak(datasorted)
    # if capcity_1 == "不分":
    #     capcity_1 = get_Capacity_bak_2(dataprocessed)
    # if capcity_2 == "不分":
    #     capcity_2 = get_Capacity_2_bak(datasorted)

    capcity_2 = re.sub("面包", "", capcity_2)
    capcity_2 = re.sub("毫[开元]", "毫升", capcity_2)
    capcity_1 = re.sub("毫[开元]", "毫升", capcity_1)

    if taste == "不分":
        taste = get_taste(datasorted, product_name)

    #type = get_keyValue(dataprocessed, ["品类"])
    type = get_type([[product_name, ], ])
    if type == "不分":
        type = get_type(datasorted)
    if type == "不分":
        if "意大利面" in product_name or "意面" in product_name:
            type = "意面酱"

    type = type if type != "意大利面酱" else "意面酱"
    type = type if type != "麻汁" else "芝麻酱"
    type = type if type != "黑椒汁" else "黑椒酱"
    type = type if type != "沙拉汁" else "沙拉酱"
    if "茶" in type or "柚子" in type:
        type = "蜜茶"
    elif "蜜" in type:
        type = "蜂蜜"

    if type == "不分" and "蜜" in product_name:
        type = "蜂蜜"
    if type == "不分" and "芝麻" in product_name:
        type = "芝麻酱"

    if type == "花生酱":
        peanutType = get_info_by_list(datasorted, ["幼滑", "颗粒", "柔滑", "顺滑"])
        peanutType = peanutType if peanutType != "顺滑" else "柔滑"

    if "配料" in product_name:
        product_name = product_name.split("配料")[0] if product_name.split("配料")[0] != "" else product_name

    # package = get_package_honey(base64strs, category_id="112")
    package = get_package_112(base64strs)

    result_dict['info1'] = taste
    result_dict['info2'] = package
    result_dict['info3'] = energy
    result_dict['info4'] = type
    result_dict['info5'] = peanutType
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
        result_dict[key_name] = ""

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_1\112-黄油蜂蜜酱'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3050371"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_112(image_list)
        with open(os.path.join(root_path, product) + r'\%s_new.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)