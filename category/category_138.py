#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/30 10:23
# @Author  : liuyb
# @Site    :
# @File    : 139.py.py
# @Software: PyCharm
# @Description: 139-饼干类别
import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,类型,包装类型,代餐功能,食用方法用量,适宜/不适宜人群
'''
# 目前已知的属性列表, 可以进行扩展
Brand_list_1 = [i.strip() for i in set(open("Labels/138_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/138_brand_list_2",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/138_taste_list",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/138_type_list",encoding="utf-8").readlines())]

Brand_list_1 = sorted(list(set(Brand_list_1)), key=len)

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")
# 通常来看需要20个非通用属性
LIMIT_NUM = 20

from category_101 import FRUIT_LIST


def get_taste(texts_list,product_name):
    result = get_info_list_by_list_taste([[product_name,],], FRUIT_LIST)
    if len(result) == 0:
        result = get_info_list_by_list_taste(texts_list, FRUIT_LIST)
    if len(result) > 0:
        # result = list(set(result))
        if len(result) > 1:
            return "混合"
        elif len(result) == 1:
            if result[0] in Taste_list:
                return result[0] + "味"
            else:
                return "其他水果味"
    return "其他"

def get_brand(kvs_list):
    pattern = r'(生产商|制造商)'
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

def get_type(texts_list,product_name):
    result = "其他酥"
    fruit_type = "不分"
    if "凤梨" in product_name:
        return "水果酥","凤梨酥"
    if "桃酥" in product_name:
        return result,fruit_type

    flag_fruit = False
    for f in FRUIT_LIST:
        if f in product_name:
            flag_fruit = True
            fruit_type = f
            break
    flag_inside = True if "芯" in product_name or "心" in product_name else False

    for texts in texts_list:
        for text in texts:
            # if not flag_fruit:
            #     for f in FRUIT_LIST:
            #         if f in text and f not in ["柠檬","梨"]:
            #             flag_fruit = True
            #             fruit_type = f
            #             break

            if "馅" in text or "酱" in text or "夹心" in text or "流心" in text or "果肉" in text or "果脯" in text:
                flag_inside = True

    for f in FRUIT_LIST:
        if f in product_name:
            flag_fruit = True
            fruit_type = f
            break

    if "礼盒" in product_name or "什锦" in product_name or "礼包" in product_name:
        fruit_type = "混合水果酥"

    if flag_fruit and flag_inside:
        result = "水果酥"
        if fruit_type in Taste_list:
            fruit_type = f + "酥"
        elif fruit_type != "混合水果酥":
            fruit_type = "其他水果酥"
    else:
        fruit_type = "不分"

    return result,fruit_type

def get_productName(texts_list):
    pattern = "("
    for i in Type_list:
        pattern += "\w*" + i + "|"
    pattern = pattern[:-1] + ")$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "(\w+酥|\w+饼|\w+米条|\w+糕|\w*猫耳朵)$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "("
    for i in Type_list:
        pattern += "\w*" + i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "(\w+酥|\w+饼|\w+米条)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

def get_productName_voting(kvs_list,texts_list):
    pattern_text = "[,，、]"
    pattern_pres = "[的是做]|^可"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+礼[盒包]|\w+什锦|\w+脆卷|\w+糍粑|\w+团子|\w+手信|\w+酥糖|\w+麻切|"
    for i in Type_list:
        pattern_1 += "\w*" + i + "|"
    pattern_1 = pattern_1[:-1] + ")($|\(|\d+[k千]?[g克])"
    pattern_2 = "(\w+酥|\w+饼干?|\w+[酥饼]+王|\w+华夫饼?|\w+[米酥]条|\w+小脆|\w+[^岩]烧|\w*牛奶囊|\w+糕|\w*猫耳朵|\w+卷|\w+乳酪|\w+[^真好太]棒|\w+麻花)($|\(|\d+[k千]?[g克])"
    pattern_3 = "(\w+礼[盒包]|\w+什锦|"
    for i in Type_list:
        pattern_3 += "\w*" + i + "|"
    pattern_3 = pattern_3[:-1] + ")"
    # pattern_4 = "(\w+酥|\w+饼|\w+[米酥]条)"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名"]) and len(k) < 6 and len(kv[k]) > 1:
                    if len(re.compile("[酥饼脆烧糕卷派棒炸包香]|团子|糕点|华夫").findall(kv[k])) ==0 and "礼盒" not in kv[k] and "礼包" not in kv[k] and "什锦" not in kv[k] :
                        result_list_tmp.append(kv[k])
                    else:
                        result_list.append(kv[k])
    if len(result_list_tmp) == 0:
        product_name_tmp = "不分"
    else:
        count = Counter(result_list_tmp).most_common(2)
        if len(count) > 1 and count[0][1] == count[1][1] and len(count[0][0]) < len(count[1][0]) and len(re.compile(pattern_text).findall(count[1][0])) == 0:
            product_name_tmp = count[1][0]
        else:
            product_name_tmp = count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    continue

    # if len(result_list) > 0:
    #     count = Counter(result_list).most_common(2)
    #     return count[0][0]
    #
    # for texts in texts_list:
    #     for text in texts:
    #         p_res = get_info_by_pattern(text, pattern_4)
    #         if len(p_res) > 0:
    #             if "的" not in p_res[0] and "是" not in p_res[0] and len(re.compile("[,，、]").findall(text)) == 0:
    #                 result_list.append(p_res[0])
    #                 continue

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    return count[0][0]

def get_productName_bak(texts_list):
    result_list = []
    pattern_1 = "("
    for i in Taste_list:
        pattern_1 += "\w*" +  i + "味?\w{2,}" + "|"
    pattern_1 = pattern_1 + "\w+\(\w+味\))"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "是" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return "不分"

def get_Capacity(kvs_list,texts_list):
    kvs_list.sort(key=len, reverse=False)
    pattern = r'(净含量?|净重|^含量$|[Nn][Ee][Tt][Ww]|重量)'
    result_list = []
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\W*(g|克|公克|千克|[kK][Gg]|斤|公斤)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        num = p_res[0]
                        if len(num) > 0:
                            if p_res[1] == "千克" or p_res[1] == "斤" or p_res[1] == "公斤" or p_res[1] == "kg" or p_res[1] == "KG":
                                if float(p_res[0]) <= 10:
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
                    pattern = r'(\d+\.?\d*)\W*(g|克|千克|[kK][Gg]|斤|公斤)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        num = p_res[0]
                        if len(num) > 0:
                            if p_res[1] == "千克" or p_res[1] == "斤" or p_res[1] == "公斤" or p_res[1] == "kg" or p_res[1] == "KG":
                                if float(p_res[0]) <= 10:
                                    return p_res[0] + p_res[1]
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= 1:
                                    return p_res[0] + p_res[1]

    return "不分"

def get_Capacity_bak(texts_list):
    p = re.compile(r'(\d+\.?\d*)\s?(G|g|克|千克|kg)')
    for texts in texts_list:
        tmp_list = []
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0 and float(p_res[0][0]) < 10000:
                if not isNutritionalTable(text, texts, index):
                    continue
                if "每份" in text:
                    continue
                tmp_list.append(p_res[0][0] + p_res[0][1])

        if len(tmp_list) == 1:
            return tmp_list[0]

    result_list = []
    p = re.compile(r'(\d+\.?\d*)\s?(G|g|克|千克|kg)')
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                if not isNutritionalTable(text, texts, index):
                    continue
                if "每份" in text:
                    continue
                p_res = p_res[0]
                if p_res[1] in ["Kg", "kg", "KG", "千克", "升", "L"]:
                    if float(p_res[0]) <= 30:
                        result_list.append(p_res[0] + p_res[1])
                else:
                    if float(p_res[0]) < 5000 and "." not in p_res[0]:
                        result_list.append(p_res[0] + p_res[1])

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    return count[0][0]

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

    pattern = r'\d+\.?\d*\D*[g克斤]\D{0,3}\d+\D*[包袋盒罐枚个]装?\)?'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克|千克|kg|斤|公斤)\D{0,3}(\d+)\D*[包袋盒罐枚个]装?\)?'
    p_unit = re.compile(r'(g|克|千克|kg|斤|公斤)')
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                unit = p_unit.findall(text)[0]
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if (unit == "千克" or unit == "斤" or unit == "公斤" or unit == "kg") and float(p_res_2[0]) <= 30:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "", p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                            if (unit == "克" or unit == "g" ) and float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "", p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[g克斤][*xX]\d+[包袋盒罐枚个\)]?$'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克|千克|kg|斤|公斤)[*xX](\d+)[包袋盒罐枚个\)]?'
    p_unit = re.compile(r'(g|克|千克|kg|斤|公斤)')
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                if len(re.compile("\d+\.\d+克\([\dg]\)").findall(text)) > 0:
                    continue
                if "(9)" in text:
                    continue
                unit = p_unit.findall(text)[0]
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if (unit == "千克" or unit == "斤" or unit == "公斤" or unit == "kg") and float(
                                    p_res_2[0]) <= 30:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                            if (unit == "克" or unit == "g") and float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*[*xX]\d+[包袋盒罐枚个]\)?$'
    pattern_2 = r'(\d+\.?\d*)[*xX](\d+)[包袋盒罐枚个]\)?'
    p_unit = re.compile(r'(g|克|千克|kg|斤|公斤)')
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                if len(re.compile("\d+\.\d+克\([\dg]\)").findall(text)) > 0:
                    continue
                if "(9)" in text:
                    continue
                if len(p_unit.findall(text)) > 0:
                    unit = p_unit.findall(text)[0]
                else:
                    unit = "g"
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if len(p_res_2) == 2:
                        if p_res_2[1] != "0" and p_res_2[1] != "":
                            if (unit == "千克" or unit == "斤" or unit == "公斤" or unit == "kg") and float(
                                    p_res_2[0]) <= 30:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[1]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                            if (unit == "克" or unit == "g") and float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[1]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+[包袋盒罐枚个]?[*xX]\d+\D*[克g]'
    pattern_2 = r'(\d+)[包袋盒罐枚个]?[*xX](\d+)\W*(g|克)'
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
                            if float(p_res_2[0]) in [4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 18.0, 24.0, 42.0, 48.0]:
                                if p_res_2[2] in ["g", "克"] and float(p_res_2[1]) > 1000:
                                    continue
                                return ("%s%s" % (str(float(p_res_2[0]) * float(p_res_2[1])), p_res_2[2])), re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[g克]\d+\D*\)'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克)(\d+)\D*\)'
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
                            if float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000:
                                return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    return "不分","不分"

def get_Capacity_2_bak(texts_list):
    p_bak = re.compile(r'(\d+)(\s?[包袋罐枚个]装)')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1]

    p_bak = re.compile(r'(\d+)([包袋罐枚个])\w*(装)$')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1] + p_res[2]

    p_bak = re.compile(r'内[装含](\d+)(小?[包袋罐枚个])')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return "内装"+ p_res[0] + p_res[1]
    return "不分"

def category_rule_138(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    taste = "不分"
    type_1 = "不分"
    type_2 = "不分"
    package = "不分"

    brand_tmp = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,Brand_list_2,["麦香","仁和","晶晶","龙凤","ABD","真老大","SKH"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    # product_name = get_keyValue(dataprocessed,["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(dataprocessed,datasorted)
    if product_name == "不分":
        product_name = get_productName_bak(datasorted)

    # if (brand_1 == "不分" or product_name == "不分") and uie_obj is not None:
    #     uie_brand,uie_productname = uie_obj.get_info_UIE(datasorted)
    #     brand_1 = brand_1 if brand_1 != "不分" else uie_brand
    #     product_name = product_name if product_name != "不分" else uie_productname

    product_name = re.sub("[蔓曼][越][莓每]", "蔓越莓", product_name)
    product_name = re.sub("紫馨", "紫薯", product_name)
    product_name = re.sub("风梨", "凤梨", product_name)
    product_name = re.sub("干层", "千层", product_name)
    product_name = re.sub("机酥", "桃酥", product_name)

    product_name = re.sub("^品[多名]", "", product_name)

    product_name = re.sub("^\w?\W+", "", product_name)

    # type_2 = get_keyValue(dataprocessed,["品类"])
    type_1, type_2 = get_type(datasorted, product_name)

    # 输出口味
    if type_1 == "其他酥":
        taste_list = get_info_list_by_list_taste(datasorted, ["肉松","咸绿豆","咸酥","黑松露","五香"])
        if len(taste_list) == 0:
            taste = "其他"
        else:
            taste = ",".join(taste_list)
    else:
        taste = get_taste(datasorted, product_name)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "g|克|公克|千克|[kK][Gg]|斤|公斤", "包袋罐枚个", 0)

    # capcity_1 = get_Capacity(dataprocessed, datasorted)
    # capcity_1_bak, capcity_2 = get_Capacity_2(dataprocessed,datasorted)
    # if capcity_1_bak != "不分" and capcity_1_bak[0] != "0":
    #     capcity_1 = capcity_1_bak
    # if capcity_1 == "不分":
    #     capcity_1 = get_Capacity_bak(datasorted)
    # if capcity_2 == "不分":
    #     capcity_2 = get_Capacity_2_bak(datasorted)

    # package = get_package(base64strs, category_id="138")
    package = get_package_138(base64strs)

    result_dict['info1'] = taste
    result_dict['info2'] = type_1
    result_dict['info3'] = type_2
    result_dict['info4'] = package
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\138-中式点心'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3995802"
        for image_path in glob(os.path.join(root_path,product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_138(image_list)
        with open(os.path.join(root_path,product) + r'\%s_ppocr.json'%(product),"w",encoding="utf-8") as f:
            json.dump(result_dict,f,ensure_ascii=False,indent=4)

