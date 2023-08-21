import os
import re

from util import *
from glob import glob


PEOPLE_RULE = ['中?老年', '婴幼?儿',"宝宝","宝贝"]
PEOPLE_RULE_NEG = ['[不非]\w*中?老年', '[非不]\w*婴幼?儿',"不适\w*人\w*","\w*慎用","\w*不宜食用"]
Brand_list_1 = [i.strip() for i in set(open("Labels/117_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/117_brand_list_2",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/117_taste_list",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/117_type_list",encoding="utf-8").readlines())]

Brand_list_1 = sorted(list(set(Brand_list_1)), key=len)

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")
# 通常来看需要20个非通用属性
LIMIT_NUM = 20

# def get_taste(texts_list,product_name):
#     pattern = "(\w+味)"
#     result = []
#     if len(product_name) > 3:
#         result = get_info_list_by_list_taste([[product_name,],], Taste_list)
#         if len(result) == 0:
#             p_res = re.compile(pattern).findall(product_name)
#             if len(p_res) > 0:
#                 Flag = True
#                 for i in Taste_Abort_List:
#                     if i in p_res[0]:
#                         Flag = False
#                         break
#                 if Flag:
#                     result.append(p_res[0])
#
#     if len(result) == 0:
#         pattern = "(\w+味)\)?$"
#         for texts in texts_list:
#             for text in texts:
#                 Flag = False
#                 for absort in absor_taste:
#                     if absort in text:
#                         Flag = True
#                         break
#                 if Flag:
#                     continue
#                 p_res = get_info_by_pattern(text, pattern)
#                 if len(p_res) > 0:
#                     tmp_taste = p_res[-1]
#                     if len(re.compile("\d").findall(tmp_taste)) > 0:
#                         continue
#
#                     tmp_flag = True
#                     for i in Taste_Abort_List:
#                         if i in tmp_taste:
#                             tmp_flag = False
#                     if tmp_taste == "新口味": tmp_flag = False
#                     if tmp_flag:
#                         if len(tmp_taste) == 2:
#                             if tmp_taste == "原味" or tmp_taste == "橙味" or tmp_taste == "橘味" or tmp_taste == "奶味" or tmp_taste == "咸味":
#                                 return tmp_taste
#                         elif len(tmp_taste) < 7:
#                             return tmp_taste
#
#     if len(result) == 0:
#         result = get_info_list_by_list_taste(texts_list, Taste_list)
#     if len(result) > 0:
#         # result = list(set(result))
#         return "".join(result)
#     return "不分"

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
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
        result = get_info_list_by_list_taste(texts_list, Taste_list)
    if len(result) > 0:
        # result = list(set(result))
        return "".join(result)
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
        if "芝麻" in result and "黑芝麻" in result:
            result.remove("芝麻")
        return "".join(result)
    return "不分"

def get_brand(kvs_list):
    pattern = r'(委托[方商]$|生产商$|经销商$)'
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
    pattern = "(\w+葡萄糖|"
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
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "\w+[粉|糊|粥|羹]$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "\w+[粉|糊|粥|羹]"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]
    return "不分"

def get_productName_voting(kvs_list,texts_list):
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+葡萄糖|\w+莲子粉|\w+葛根粉|\w+蛋白质?粉|\w+藕粉羹?|\w+豆粉|\w*豆腐脑粉|\w+营养粉|\w+芝麻糊|\w+五谷粉|\w+豆[浆奶]粉?|\w+核桃粉|\w+[^玉小]米粉|\w+米乳|\w+米粉?[稀粥羹糊]|\w+芡实粥|\w+油茶|\w+鸡内金|\w*匀浆膳|\w+燕麦片)($|\()"
    pattern_2 = "(\w+葡萄糖|\w*莲子粉|\w*葛根粉|\w*蛋白质?粉|\w*藕粉羹?|\w*豆粉|\w*豆腐脑粉?|\w*营养粉|\w*芝麻糊|\w*五谷粉|\w*豆[浆奶]粉?|\w*核桃粉|\w*[^玉小]米粉|\w+米乳|\w*米粉?[稀粥羹糊]|\w*芡实粥|\w*油茶|\w*燕麦片)"
    pattern_3 = "\w{2,}[糊粥羹汤粉]$|\w+固体饮料$|\w*银耳[美蒙望费葵堂菱业真]$|\w*粉[美蒙望费葵堂菱奠蟹]$|^葡萄糖$"
    pattern_4 = "[\\\/\w]{2,}[糊粥羹汤粉]"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]) and len(k) < 6 and len(kv[k]) > 1:
                    if ("粉" not in kv[k] and "葡萄糖" not in kv[k] and "汤" not in kv[k] and "羹" not in kv[k] and "粥" not in kv[k] and "油茶" not in kv[k] and "糊" not in kv[k] and "饮" not in kv[k] and "燕麦片" not in kv[k]) or len(kv[k]) <= 2:
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
                p_res = p_res[0]
                if len(re.compile("[的是请勺取入烤]").findall(p_res[0])) == 0 and "、" not in text and "," not in text and "本品" not in p_res[0] and "加入" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 2 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if len(re.compile("[的是请勺取入烤]").findall(p_res[0])) == 0 and "、" not in text and "," not in text and "本品" not in p_res[0] and "加入" not in p_res[0]:
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
                if len(re.compile("[的是请勺取入烤]").findall(p_res[0])) == 0 and "、" not in text and "," not in text and "本品" not in p_res[0] and "加入" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 2 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                if len(re.compile("[的是请勺取入烤]").findall(p_res[0])) == 0 and "、" not in text and "," not in text and "本品" not in p_res[0] and "加入" not in p_res[0] and "淀粉" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) == 2 and count[0][0] in count[1][0]:
        return count[1][0]
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
                    pattern = r'(\d+\.?\d*)\s?(G|g|克|[千干]克|kg|KG|斤|公斤)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克", "kg", "KG", "斤", "公斤","干克"]:
                                if float(p_res[0]) <= 30:
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
                                if float(p_res[0]) <= 30:
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

    pattern = r'\d+\.?\d*\D*[g克]\D{0,3}\d+\D?[包袋盒罐支杯粒瓶片]装?\)?'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克)\D{0,3}(\d+)\D?[包袋盒罐支杯粒瓶片]装?\)?'
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
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0] or len(re.compile("/[包袋盒罐支杯粒瓶片]").findall(p_res[0])) > 0:
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "", p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[g克][*xX]\d+[包袋盒罐支杯粒瓶片\)]?'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克)[*xX](\d+)[包袋盒罐支杯粒瓶片\)]?'
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

    pattern = r'\d+[包袋盒罐支杯粒瓶片][*xX]\d+\.?\d*\D*[g克]'
    pattern_2 = r'(\d+)[包袋盒罐支杯粒瓶片][*xX](\d+\.?\d*)\W*(g|克)'
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

    return "不分","不分"

def get_Capacity_2_bak(texts_list):
    p_bak = re.compile(r'(\d+)(\s?[包袋盒罐支杯粒瓶片]装)')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1]

    p_bak = re.compile(r'(\d+)([包袋盒罐支杯粒瓶片])\w*(装)$')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1] + p_res[2]

    p_bak = re.compile(r'内[装含](\d+)(小?[包袋盒罐支杯粒瓶片])')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return "内装"+ p_res[0] + p_res[1]
    return "不分"

def get_type(texts_list):
    result = "不分"
    pattern_1 = "(粥|羹|汤)"
    pattern_2 = "(营养粉|[玉小]?米[粉乳]|莲子粉|藕粉|核桃粉|芝麻糊|葡萄糖|豆浆?粉|豆腐脑粉?|油茶|五谷粉)"
    pattern_3 = "粉|糊"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                result = p_res[0]

    if result == "不分":
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern_2)
                if len(p_res) > 0 and "、" not in text and "," not in text:
                    result = p_res[0]
        if "豆" in result:
            result = "豆粉"
        if "莲子" in result or "藕" in result:
            result = "莲子、藕粉"
        if "五谷" in result:
            result = "米粉"
        if "米乳" in result:
            result = "米粉"
        if "玉米粉" in result or "小米粉" in result:
            result = "其他粉、糊"

    if result == "不分":
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern_3)
                if len(p_res) > 0:
                    result = "其他粉、糊"

    return result

def category_rule_117(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    taste = "不分"
    type = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    people = "不分"
    type_2 = "不分"

    brand_tmp = "不分"

    dataprocessed.sort(key= lambda c : (len(c),len(str(c))), reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed,["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,Brand_list_2,["北大荒","冬梅","日膳","金麦","VEYA","好的","一家人","方广"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("啵元", "啵兀", brand_1)
    brand_1 = re.sub("山SHANHONG鸿", "山鸿", brand_1)

    if product_name == "不分":
        product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("粉[美蒙望费葵堂菱奠蟹蔻煲]", "粉羹", product_name)
    product_name = re.sub("玉米[美蒙望费葵堂菱奠蟹蔻煲]", "玉米羹", product_name)
    product_name = re.sub("银耳[美蒙望费葵堂菱业真蔻煲]", "银耳羹", product_name)
    product_name = re.sub("山植", "山楂", product_name)
    product_name = re.sub("构杞", "枸杞", product_name)
    product_name = re.sub("^配料:?", "", product_name)
    product_name = re.sub("配料?$", "", product_name)
    product_name = re.sub("桑[甚基]", "桑葚", product_name)
    product_name = re.sub("意米", "薏米", product_name)
    product_name = re.sub("^杞", "枸杞", product_name)
    product_name = re.sub("果芝麻", "黑芝麻", product_name)

    product_name = re.sub("^品?名1?", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)

    # if (brand_1 == "不分" or product_name == "不分") and uie_obj is not None:
    #     uie_brand,uie_productname = uie_obj.get_info_UIE(datasorted)
    #     brand_1 = brand_1 if brand_1 != "不分" else uie_brand
    #     product_name = product_name if product_name != "不分" else uie_productname

    # type = get_keyValue(dataprocessed, ["品类"])
    if type == "不分":
        type = get_type([[product_name, ], ])
    if type == "不分":
        type = get_type(datasorted)

    if "芝麻粉" in product_name:
        type = "芝麻糊"

    capcity_1 = get_Capacity(dataprocessed, datasorted)
    capcity_1_bak, capcity_2 = get_Capacity_2(dataprocessed,datasorted)
    if capcity_1_bak != "不分":
        capcity_1 = capcity_1_bak
    if capcity_1 == "不分":
        capcity_1 = get_Capacity_bak(datasorted)
    if capcity_2 == "不分":
        capcity_2 = get_Capacity_2_bak(datasorted)

    taste = get_taste(datasorted, product_name)

    if "银耳羹" in product_name:
        tmp_taste = taste.replace("银耳","")
        if len(tmp_taste) > 1:
            taste = tmp_taste

    people = get_info_by_RE([[product_name,],], PEOPLE_RULE)
    if people in ["宝宝","宝贝"]:
        people = "婴儿"

    result_dict['info1'] = taste
    result_dict['info2'] = type
    result_dict['info3'] = type_2
    result_dict['info4'] = people
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 4
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = ""

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_1\117-营养糊营养粉'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3034811"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_117(image_list)
        with open(os.path.join(root_path, product) + r'\%s_new.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)
