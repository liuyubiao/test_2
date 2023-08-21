import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

PEOPLE_RULE = ['婴幼?儿',"宝宝","童趣","卡通","儿童"]

LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/149_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/149_brand_list_2",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/149_taste_list",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/149_type_list",encoding="utf-8").readlines())]

Brand_list_1 = sorted(list(set(Brand_list_1)), key=len)

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")

absor_productname = ["大娘水饺",]

def get_store(texts_list):
    key_1 = ["零下"]
    key_2 = ["冷藏"]

    for texts in texts_list:
        for text in texts:
            for k in key_1:
                if k in text:
                    return "零下18度"

    for texts in texts_list:
        for text in texts:
            for k in key_2:
                if k in text:
                    return "冷藏"

    return "零下18度"

def get_method(texts_list):
    key = "手工"
    for texts in texts_list:
        for text in texts:
            if key in text:
                if "非" not in text:
                    return "手工"
                else:
                    return "非手工"
    return "不分"

def get_taste(texts_list,product_name):
    pattern = "(\w+[味馅])"
    result = get_info_list_by_list_taste([[product_name,],], Taste_list)
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
        pattern = "(\w+[味馅])\)?$"
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
                    if tmp_taste == "新口味" or tmp_taste == "口味": tmp_flag = False
                    if tmp_flag:
                        if len(tmp_taste) == 2:
                            if tmp_taste == "原味" or tmp_taste == "橙味" or tmp_taste == "橘味" or tmp_taste == "奶味" or tmp_taste == "咸味":
                                return tmp_taste
                        elif len(tmp_taste) < 7:
                            return tmp_taste
                else:
                    for i in ["香辣","辛香","葱香","麻辣","五香","奶香","酱香"]:
                        if i in text:
                            return i

    if len(result) == 0:
        result = get_info_list_by_list_taste(texts_list, Taste_list)
    if len(result) > 0:
        # result = list(set(result))
        return "".join(result)
    return "不分"

def get_ingredients(texts_list,product_name):
    pattern = "(\w+馅)"
    result = get_info_list_by_list([[product_name,],], Taste_list)
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

    if len(result) > 0:
        ingredients_list = []
        for i in result:
            i = re.sub("[馅]","",i)
            if i not in ["香辣","酱香","辛香","奶香"]:
                ingredients_list.append(i)
        ingredients_list = list(set(ingredients_list))
        if len(ingredients_list) > 0:
            return "".join(ingredients_list)
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
                return p_res[-1]
    return "不分"

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

    pattern = "("
    for i in Type_list:
        pattern += "\w*" + i + "|"
    pattern = pattern[:-1] + ")[^\u4e00-\u9fa5]+"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "\w+[包粽饺糕饼面]$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

def get_productName_voting(kvs_list,texts_list):
    pattern_text = "公司|温度|适[中量]"
    pattern_pres = "[的是将使用放入搅匀每出做勿或市区变]|[撒淋]上|小火|^大娘水饺$|[炭碳]火烧$|图片|每一|其他|锅内|专注|没过"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w{2,}双拼|\w+鲜切面|\w*竹升面|\w+小笼包?|\w+拌面|\w+福袋|\w*猪肚鸡锅|\w+肉包|\w+刀削面|\w+礼盒|"
    for i in Type_list:
        pattern_1 += "\w{2,}" + i + "|"
    pattern_1 = pattern_1[:-1] + ")($|\()"
    pattern_2 = "(\w*鲜切面|\w+粽子?|\w*拌面|\w*刀削面|"
    for i in Type_list:
        pattern_2 += "\w*" + i + "|"
    pattern_2 = pattern_2[:-1] + ")$"
    pattern_3 = pattern_2[:-1]
    pattern_4 = "(\w+[粽饺糕饼馍]|\w+[^背正和煮全\W]面|\w+[^手\W]包|\w+[米面]+食品)($|\(|\d+[k千]?[g克])"

    pattern_tmp = pattern_1 + "|" + pattern_2 + "|" + pattern_3 + "|" + pattern_4
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称", "名"]) and len(k) < 6:
                    if len(kv[k]) <= 1:
                        continue
                    if len(re.compile(pattern_tmp).findall(kv[k])) == 0 and "#" not in kv[k]:
                        result_list_tmp.append(kv[k])
                    else:
                        result_list.append(kv[k])
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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
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
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) == 2 and count[0][1] == count[1][1] and len(count[1][0]) > len(count[0][0]) and len(re.compile("\W").findall(count[1][0])) == 0:
        return count[1][0]
    return count[0][0]

def get_productName_pre(texts_list):
    pattern = "产?品名称?\W*$"
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res_1 = get_info_by_pattern(text, pattern)
            total_len = len(texts)
            if len(p_res_1) > 0:
                for i in [1,-1]:
                    if index + i >= 0 and index + i < total_len:
                        p_res_tmp = re.compile("\w+[包粽饺糕饼面]$").findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            return p_res_tmp[0]
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
                    pattern = r'(\d+\.?\d*)\s?(G|g|克|[千干]克|kg|KG|斤|公斤)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克", "kg", "KG", "斤", "公斤","干克"]:
                                if float(p_res[0]) <= 10:
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
                    pattern = r'(\d+\.?\d*)\s?(G|g|克|千克|kg|KG|斤|公斤)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克", "kg", "KG", "斤", "公斤"]:
                                if float(p_res[0]) <= 10:
                                    return p_res[0] + p_res[1]
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= 1:
                                    return p_res[0] + p_res[1]

    return "不分"

def get_Capacity_bak(texts_list):
    p = re.compile(r'(\d+\.?\d*)\s?(G|g|克|千克|kg|KG)')
    for texts in texts_list:
        tmp_list = []
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0 and float(p_res[0][0]) < 10000 and float(p_res[0][0]) >= 10:
                if not isNutritionalTable(text, texts, index):
                    continue
                if "每份" in text:
                    continue
                tmp_list.append(p_res[0][0] + p_res[0][1])

        if len(tmp_list) == 1:
            return tmp_list[0]

    result_list = []
    p = re.compile(r'(\d+\.?\d*)\s?(G|g|克|千克|kg|KG)')
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                if not isNutritionalTable(text, texts, index):
                    continue
                if "每份" in text:
                    continue
                p_res = p_res[0]
                if p_res[1] in ["Kg","kg","KG","千克","升","L"]:
                    if float(p_res[0]) <= 30:
                        result_list.append(p_res[0] + p_res[1])
                else:
                    if float(p_res[0]) < 5000 and "." not in p_res[0] and float(p_res[0]) >= 10:
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

    pattern = r'\d+\.?\d*\D*[g克]\D{0,3}\d+\D?[包袋盒罐支片只个张]装?\)?'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克)\D{0,3}(\d+)\D?[包袋盒罐支片只个张]装?\)?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            if len(re.split("[*xX]\d",text)) > 2:
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
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0] :
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "", p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[g克][*xX]\d+[包袋盒罐支片只个张\)]?'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克)[*xX](\d+)[包袋盒罐支片只个张\)]?'
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
                            if float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+[包袋盒罐支片只个张][*xX]\d+\.?\d*\D*[g克]'
    pattern_2 = r'(\d+)[包袋盒罐支片只个张][*xX](\d+\.?\d*)\W*(g|克)'
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
                    unit = p_res_2[2]
                    if len(p_res_2) == 3:
                        if p_res_2[0] != "0" and p_res_2[0] != "":
                            if float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[1]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[g克l升]\D{0,3}\d+\D*\)$'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克|千克|kg)\D{0,3}(\d+)\D*'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                if len(re.compile("\d+\.\d+克\([\dg]\)").findall(text)) > 0:
                    continue
                if "(9)" in text:
                    continue
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    return "不分", re.sub(u"\)", "", p_res[0])

    return "不分","不分"

def get_Capacity_2_bak(texts_list):
    p_bak = re.compile(r'(\d+)(\s?[包袋盒罐支片只个张]装)')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1]

    p_bak = re.compile(r'(\d+)([包袋盒罐支片只个张])\w*(装)$')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1] + p_res[2]

    p_bak = re.compile(r'内[装含](\d+)(小?[包袋盒罐支片只个张])')
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
                        p_res_tmp = re.compile("^\d{1,3}[gG克]$").findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            return p_res_tmp[0]

                for i in [1,2,-1,-2]:
                    if index + i >=0 and index + i <total_len:
                        p_res_tmp = re.compile("^\d{1,3}$").findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            return p_res_tmp[0] + "克"
    return num

def category_rule_149(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    type = "不分"
    taste = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    people = "不分"
    store = "不分"
    method = "不分"
    ingredients = "不分"

    brand_tmp = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,Brand_list_2,["家乡味","光明","遇见","奥秘","伯爵","吉祥","粤冷","优食","金家","扬子江","意美","润味","包文化","鲜道","日日鲜","优鲜"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("TAOCHU", "饕厨", brand_1)
    brand_1 = re.sub("柯众吖", "柯尒吖", brand_1)
    brand_1 = re.sub("生张力", "张力生", brand_1)

    if product_name == "不分":
        product_name = get_productName_pre(datasorted)
    if product_name == "不分":
        product_name = get_productName_voting(dataprocessed,datasorted)

    product_name = re.sub("粹", "粽", product_name)
    product_name = re.sub("香苹", "香芋", product_name)
    product_name = re.sub("七豆", "土豆", product_name)
    product_name = re.sub("八宝板", "八宝饭", product_name)
    product_name = re.sub("非菜", "韭菜", product_name)
    product_name = re.sub("鲮鱼", "鲅鱼", product_name)
    product_name = re.sub("尔薯", "紫薯", product_name)
    product_name = re.sub("白颗", "白粿", product_name)
    product_name = re.sub("特包子", "烤包子", product_name)

    product_name = re.sub("^\w?\W+", "", product_name)

    # if (brand_1 == "不分" or product_name == "不分") and uie_obj is not None:
    #     uie_brand,uie_productname = uie_obj.get_info_UIE(datasorted)
    #     brand_1 = brand_1 if brand_1 != "不分" else uie_brand
    #     product_name = product_name if product_name != "不分" else uie_productname

    capcity_1 ,capcity_2= get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤|升|毫升|ML|ml|mL|L", "包袋盒罐支片只个张", 2)

    # capcity_1 = get_Capacity(dataprocessed, datasorted)
    # capcity_1_bak, capcity_2 = get_Capacity_2(dataprocessed,datasorted)
    # if capcity_1_bak != "不分":
    #     if capcity_1 == "不分":
    #         capcity_1 = capcity_1_bak
    #     elif re.compile("\d+\.?\d*").findall(capcity_1)[0] in capcity_2:
    #         capcity_1 = capcity_1_bak
    # if capcity_1 == "不分":
    #     capcity_1 = get_Capacity_bak(datasorted)
    # if capcity_1 == "不分":
    #     capcity_1 = get_Capacity_bak_2(datasorted)
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

    if taste == "不分":
        taste = get_taste(datasorted,product_name)

    if store == "不分":
        store = get_store(datasorted)

    # if method == "不分":
    #     method = get_method(datasorted)

    if people == "不分":
        people = get_info_by_RE(datasorted, PEOPLE_RULE)
        people = people if people == "不分" else "儿童"


    type_tmp_list = ["粽","饺","包","面"]
    for index,i in enumerate(reversed(product_name.split("(")[0])):
        if index > 2:
            break
        if i in type_tmp_list:
            if "粽" == i:
                type = "粽子"
                break
            elif "饺" == i and "煎饺" not in product_name and "水饺" not in product_name:
                type = "饺子"
                break
            elif "包" == i and "包饭" not in product_name:
                type = "包子"
                break
            elif "面" == i :
                type = "面条"
                break
    if "小笼" in product_name:
        type = "小笼包"
    if "烤冷面" in product_name:
        type = "烤冷面"

    if type == "不分":
        type = get_type([[product_name,],])
    if type == "不分":
        if "海鲜" in product_name:
            type = "海鲜"

    if product_name.endswith("肉馅"):
        type = "肉馅"
    if type == "不分":
        type= get_type(datasorted)

    if type == "牛肉芝士卷":
        type = "牛肉卷"

    if len(re.sub(type + "$","",product_name)) == 1:
        product_name = type

    ingredients_list = ["紫糯米","黑糯米","老面","紫米","大黄米","芋头","糯米","高梁","白面","糯玉米","玉米","荞麦","玉米"]
    for i in ingredients_list:
        if i in product_name:
            ingredients = i
    # if ingredients == "不分":
    #     ingredients = get_ingredients(datasorted,product_name)

    result_dict['info1'] = taste
    result_dict['info2'] = method
    result_dict['info3'] = type
    result_dict['info4'] = ingredients
    result_dict['info5'] = store
    result_dict['info6'] = people
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    for k in result_dict.keys():
        result_dict[k] = re.sub("[,，：:]", "", result_dict[k])

    real_use_num = 6
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_2\149-速冻食品'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3039104"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_149(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)