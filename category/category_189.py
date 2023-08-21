import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/189_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/189_brand_list_2",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/189_type_list",encoding="utf-8").readlines())]

Brand_list_1 = sorted(list(set(Brand_list_1)), key=len)

def get_level(texts_list):
    pattern = "[一二三四特]级"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]
    return "不分"

def get_gene(texts_list):
    key = "转基因"
    flag = -1
    for texts in texts_list:
        text = "".join(texts)
        if key in text:
            if "非" not in text and "丰转" not in text :
                flag = "1"
            else:
                return "非转基因"
    if flag == "1":
        return "转基因"

    return "不分"

def get_method(texts_list):
    key_list = ["浸出","压榨","水代","冷榨"]
    result = get_info_list_by_list(texts_list,key_list)

    if len(result) > 1:
        return ",".join(result)
    elif len(result) == 1:
        return result[0]
    else:
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

def get_productName(texts_list):
    pattern = "(\w*麻椒油|\w*花椒油|\w*姜油|\w*香辣红油|"
    for i in Type_list:
        pattern += "\w*" + i + "|"
    pattern = pattern[:-1] + ")$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "配料" not in p_res[0]:
                return p_res[0]

    pattern = "(\w*麻椒油|\w*花椒油|\w*姜油|\w*香辣红油|"
    for i in Type_list:
        pattern += "\w*" + i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "配料" not in p_res[0]:
                return p_res[0]

    pattern = "\w+油$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "\w+油"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]
    return "不分"

def get_productName_voting(kvs_list,texts_list):
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+麻椒油|\w+花椒油|\w+姜油|\w+红油|\w+香油|"
    for i in Type_list:
        if len(i) > 3:
            pattern_1 += "\w*" + i + "|"
        else:
            pattern_1 += "\w+" + i + "|"
    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1.replace("+","*")[:-1]
    pattern_3 = "\w+油$"
    pattern_4 = "\w+油"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]) and len(k) < 6:
                    if "油" not in kv[k]:
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
                if "的" not in p_res[0] and "是" not in p_res[0] and "保留" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 2 and count[0][1] == count[1][1] and len(count[1][0]) > len(count[0][0]) and len(re.compile("\W").findall(count[1][0])) == 0:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "是" not in p_res[0] and "保留" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 2 and count[0][1] == count[1][1] and len(count[1][0]) > len(count[0][0]) and len(re.compile("\W").findall(count[1][0])) == 0:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "是" not in p_res[0] and "放心" not in p_res[0] and "保留" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 2 and count[0][1] == count[1][1] and len(count[1][0]) > len(count[0][0]) and len(re.compile("\W").findall(count[1][0])) == 0:
            return count[1][0]
        return count[0][0]

    if product_name_tmp != "不分":
        return product_name_tmp

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "是" not in p_res[0] and "放心" not in p_res[0] and "保留" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) == 2 and count[0][1] == count[1][1] and len(count[1][0]) > len(count[0][0]) and len(re.compile("\W").findall(count[1][0])) == 0:
        return count[1][0]
    return count[0][0]

def get_Capacity(kvs_list,texts_list):
    kvs_list.sort(key=len, reverse=False)
    pattern = r'(净含量?|净重|^[含容]量$|[Nn][Ee][Tt][Ww]|重量)'
    result_list = []
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\s?(g|[千干]?克|KG|kg|毫升?|斤|公斤|升|ml?|mL|L)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克", "kg", "KG", "升", "L", "干克","斤","公斤"]:
                                if float(p_res[0]) <= 30:
                                    if p_res[1] == "干克":
                                        result_list.append(p_res[0] + "千克")
                                    else:
                                        result_list.append(p_res[0] + p_res[1])
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= 1:
                                    if p_res[1] in ["毫","m"]:
                                        result_list.append(p_res[0] + "毫升")
                                    else:
                                        result_list.append(p_res[0] + p_res[1])

    result_list.sort(key=len,reverse=True)
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
                    pattern = r'(\d+\.?\d*)\s?(g|kg|毫升|升|ml|mL|L)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克", "kg", "KG", "升", "L"]:
                                if float(p_res[0]) <= 30:
                                    return p_res[0] + p_res[1]
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= 1:
                                    return p_res[0] + p_res[1]

    return "不分"

def get_Capacity_bak(texts_list):
    p = re.compile(r'^(\d+\.?\d*)\s?(毫升|升|ml|L)$')
    for texts in texts_list:
        tmp_list = []
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0 and float(p_res[0][0]) < 10000:
                # if not isNutritionalTable(text, texts, index):
                #     continue
                if "每份" in text:
                    continue
                tmp_list.append(p_res[0][0] + p_res[0][1])

        if len(tmp_list) == 1:
            return tmp_list[0]

    p = re.compile(r'(\d+\.?\d*)\s?(毫升|升|ml|L)$')
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
    p = re.compile(r'(\d+\.?\d*)\s?(毫升|升|ml|L)')
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

    pattern = r'\d+\.?\d*\D*[lL升]\D{0,3}\d+\D?[包袋盒瓶桶]装?\)?'
    pattern_2 = r'(\d+\.?\d*)\W*(升|毫升|ml|L|ML|mL)\D{0,3}(\d+)\D?[包袋盒瓶桶]装?\)?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            if len(re.split("[*xX]\d", text)) > 2:
                continue
            if "每份" in text:
                continue
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    unit = p_res_2[1]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000 and float(p_res_2[2]) < 201:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), p_res[0]
                                else:
                                    return "不分", p_res[0]
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[lL升][*xX]\d+[包袋盒瓶桶\)]?'
    pattern_2 = r'(\d+\.?\d*)\W*(升|毫升|ml|L|ML|mL)[*xX](\d+)[包袋盒瓶桶\)]?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            if len(re.split("[*xX]\d", text)) > 2:
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
                            if float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[m毫][*xX]\d+[包袋盒瓶桶\)]?'
    pattern_2 = r'(\d+\.?\d*)\W*(毫|m)[*xX](\d+)[包袋盒瓶桶\)]?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            if len(re.split("[*xX]\d", text)) > 2:
                continue
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    unit = p_res_2[1] + "升" if p_res_2[1] == "毫" else p_res_2[1] + "l"
                    if p_res_2[2] != "0" and p_res_2[2] != "":
                        if float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000:
                            return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "",p_res[0])

    return "不分","不分"

def get_Capacity_2_bak(texts_list):
    p_bak = re.compile(r'(\d+)(\s?[袋盒罐瓶]装)')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1]

    p_bak = re.compile(r'(\d+)([袋盒罐瓶])\w*(装)$')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1] + p_res[2]

    p_bak = re.compile(r'内[装含](\d+)(小?[袋盒罐瓶])')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return "内装"+ p_res[0] + p_res[1]
    return "不分"

def get_Capacity_bak_2(texts_list):
    pattern = r'(净含量?|净重|^含量$|[Nn][Ee][Tt][Ww]|重量)'
    num = "不分"
    for texts in texts_list:
        for index,text in enumerate(texts):
            p_res_1 = get_info_by_pattern(text, pattern)
            total_len = len(texts)
            if len(p_res_1) > 0:
                for i in [1,2,-1,-2]:
                    if index + i >=0 and index + i <total_len:
                        p_res_tmp = re.compile("^\d{1,4}[mM]?[lL]$").findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            return p_res_tmp[0]
    return num

def category_rule_189(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    type = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    level = "不分"
    gene = "不分"
    method = "不分"
    package = "不分"

    brand_tmp = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,Brand_list_2,["花蕊","天香","四海","朱家","飞越","福顺"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    # product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(dataprocessed,datasorted)
    product_name = product_name.replace("配料","")

    product_name = re.sub("亚麻好油", "亚麻籽油", product_name)
    product_name = re.sub("南瓜好油", "南瓜籽油", product_name)
    product_name = re.sub("葵花好油", "葵花籽油", product_name)
    product_name = re.sub("亚欧籽", "亚麻籽", product_name)
    product_name = re.sub("花根", "花椒", product_name)


    product_name = re.sub("^榨", "", product_name)
    product_name = re.sub("^级", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)

    # if (brand_1 == "不分" or product_name == "不分") and uie_obj is not None:
    #     uie_brand,uie_productname = uie_obj.get_info_UIE(datasorted)
    #     brand_1 = brand_1 if brand_1 != "不分" else uie_brand
    #     product_name = product_name if product_name != "不分" else uie_productname

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "ml|毫[升元开]|mL|L|[升元开]|ML", "袋盒桶罐瓶", 1)

    capcity_2 = re.sub("[元开]", "升", capcity_2)
    capcity_1 = re.sub("[元开]", "升", capcity_1)

    # capcity_1 = get_Capacity(dataprocessed, datasorted)
    # capcity_1_bak, capcity_2 = get_Capacity_2(dataprocessed,datasorted)
    # if capcity_1_bak != "不分":
    #     if capcity_1 == "不分":
    #         capcity_1 = capcity_1_bak
    #     elif re.compile("\d+\.?\d*").findall(capcity_1)[0] in capcity_2:
    #         capcity_1 = capcity_1_bak
    # if capcity_1 == "不分":
    #     capcity_1 = get_Capacity_bak_2(datasorted)
    # if capcity_1 == "不分":
    #     capcity_1 = get_Capacity_bak(datasorted)
    # if capcity_2 != "不分":
    #     try:
    #         num_0 = float(re.compile("\d+\.?\d*").findall(capcity_1)[0])
    #         num_1, num_2 = re.compile("\d+\.?\d*").findall(capcity_2)
    #         if float(num_1) * float(num_2) != num_0 and num_0 != float(num_1) and num_0 != float(num_2):
    #             capcity_2 = "不分"
    #     except:
    #         pass
    # if capcity_2 == "不分":
    #     capcity_2 = get_Capacity_2_bak(datasorted)

    if "调和" in product_name:
        type = "调和油"
    if type == "不分":
        type = get_type([[product_name, ], ])
    if type == "不分":
        if "花椒" in product_name or "胡麻" in product_name or "蒜油" in product_name or "红油" in product_name or "藤椒" in product_name:
            type = "调味油"
        elif "香油" in product_name:
            type = "芝麻油"
    if type == "不分":
        type = get_type(datasorted)
    if "辣" in type :
        type = "调味油"
    if type == "不分":
        if "麻油" in product_name:
            type = "麻油"

    if method == "不分":
        method = get_method(datasorted)
    if method == "不分":
        if "榨" in product_name:
            method = "压榨"

    # if "调" in type or "玉米" in type or "大豆" in type :
    gene = get_gene(datasorted)

    # if "大豆" in type or "菜籽" in type:
    level = get_level(datasorted)

    if type in ["大豆油","菜籽油"]:
        pattern = "维A|维生素A|营养强化|^AE$"
        for texts in datasorted:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern)
                if len(p_res) > 0:
                    type = "营养强化油"

    if type == "芝麻油" and "石磨" not in product_name and "小磨" not in product_name:
        pattern = "石磨|小磨|机制压榨"
        for texts in datasorted:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern)
                if len(p_res) > 0:
                    product_name = product_name if p_res[0] in product_name else p_res[0] + product_name

    package = get_package_189(base64strs)

    if package == "塑料瓶" and capcity_2 == "不分":
        try:
            num_0 = float(re.compile("\d+\.?\d*").findall(capcity_1)[0])
            if num_0 > 1500 or num_0 < 6:
                package = "塑料桶"
        except:
            pass

    result_dict['info1'] = type
    result_dict['info2'] = level
    result_dict['info3'] = gene
    result_dict['info4'] = method
    result_dict['info5'] = package
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
    root_path = r'D:\Data\商品识别\stage_2\189-食用植物油（含调味油）'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        product = "3042691"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_189(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)