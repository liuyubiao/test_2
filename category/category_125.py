import os
import re

from util import *
from glob import glob

'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,类型,包装类型,代餐功能,食用方法用量,适宜/不适宜人群
'''
# 目前已知的属性列表, 可以进行扩展
Brand_list_1 = [i.strip() for i in set(open("Labels/125_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/125_brand_list_2",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/125_taste_list",encoding="utf-8").readlines())]

Brand_list_1 = sorted(list(set(Brand_list_1)), key=len)

Ingredients_list_ori = [i.strip() for i in open("Labels/125_ingredients_list",encoding="utf-8").readlines()]
Ingredients_list = []
for line in Ingredients_list_ori:
    Ingredients_list.extend(re.split("[^\-0-9a-zA-Z\u4e00-\u9fa5]",line))
Ingredients_list = set(Ingredients_list)
Ingredients_list.remove("")
Ingredients_list = list(Ingredients_list)
Ingredients_list.sort(key=len,reverse=True)

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")
# 通常来看需要20个非通用属性
LIMIT_NUM = 20


def LCS(string1, string2):
    len1 = len(string1)
    len2 = len(string2)
    res = [[0 for i in range(len1 + 1)] for j in range(len2 + 1)]
    for i in range(1, len2 + 1):
        for j in range(1, len1 + 1):
            if string2[i - 1] == string1[j - 1]:
                res[i][j] = res[i - 1][j - 1] + 1
            else:
                res[i][j] = max(res[i - 1][j], res[i][j - 1])
    return res[-1][-1]

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
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

    if len(result) == 0:
        return get_taste_normal(texts_list, Taste_list)
    else:
        # result = list(set(result))
        return "".join(result)

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

def get_type_list(texts_list,search_list,abort_list = []):
    result_list = []
    for texts in texts_list:
        for text in texts:
            for t in search_list:
                if t in text:
                    flag = True
                    for abort in abort_list:
                        if abort in text:
                            flag = False
                    if flag:
                        if t not in result_list:
                            result_list.append(t)

    return result_list

def get_type_productName(product_name):
    result = "不分"
    pattern = "(米饼|薯片|薯条|薯|雪饼)"
    result_list = []
    p_res = get_info_by_pattern(product_name, pattern)
    if len(p_res) > 0:
        result_list.append(p_res[-1])
    if "雪饼" in result_list or "米饼" in result_list:
        result = "米制雪/米饼"

    if "薯片" in result_list:
        result = "土豆薯片"
    elif "薯条" in result_list:
        result = "土豆薯条"
    elif "薯" in result_list:
        result = "土豆非薯片、非薯条"

    return result

def get_type(texts_list):
    result = "不分"
    type_key_1 = ["玉米","玉米糁"]
    type_key_2 = ["小麦","面粉"]
    type_key_3 = ["大米","糙米","黑米"]
    type_key_4 = ["土豆","马铃薯"]
    type_key_5 = ["糖蜜豆", "糖豆", "荷兰豆", "青豆","大豆"]
    type_key_6 = ["小米", "栗米"]

    if result == "不分":
        result_1 = len(get_type_list(texts_list,type_key_1,abort_list =["玉米淀粉"]))
        result_2 = len(get_type_list(texts_list,type_key_2))
        result_3 = len(get_type_list(texts_list,type_key_3))
        result_4 = len(get_type_list(texts_list,type_key_4))
        result_5 = len(get_type_list(texts_list, type_key_5,abort_list =["大豆油","大豆及"]))
        result_6 = len(get_type_list(texts_list, type_key_6))


        result_1 = result_1 if result_1 <= 1 else 1
        result_2 = result_2 if result_2 <= 1 else 1
        result_3 = result_3 if result_3 <= 1 else 1
        result_4 = result_4 if result_4 <= 1 else 1
        result_5 = result_5 if result_5 <= 1 else 1
        result_6 = result_6 if result_6 <= 1 else 1

        score = result_1 + result_2 + result_3 + result_5
        if score == 1:
            if result_1 == 1:
                result = "玉米制品"
            if result_2 == 1:
                result = "其他面制品"
            if result_3 == 1:
                result = "其他米制品"
            if result_5 == 1:
                result = "豆制品"
        elif score == 0:
            if result_4 == 1:
                result = "土豆非薯片、非薯条"
            if result_6 == 1:
                result = "栗米制品"
        else:
            result = "混合"
    return result

def get_productName(texts_list):
    pattern = "(\w+薯片|\w+脆片|\w+甜甜圈|\w+巧克力圈|\w+洋葱圈|\w+雪饼|\w+酥|\w+薯条|\w+脆棒|\w+泡芙条?|\w+火鸡面|\w+礼盒|\w+虾\w?条)$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "(\w+薯片|\w+脆片|\w+甜甜圈|\w+巧克力圈|\w+洋葱圈|\w+雪饼|\w+酥|\w+薯条|\w+脆棒|\w+泡芙条?|\w+火鸡面|\w+礼盒|\w+虾\w?条)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "(\w*薯片|\w*脆片|\w*甜甜圈|\w*巧克力圈|\w*洋葱圈|\w*雪饼|\w*薯条|\w*脆棒|\w*泡芙条?|\w*火鸡面|\w*礼盒|\w*虾\w?条)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "(\w+片|\w+圈|\w+饼|\w+面)$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "背面" not in p_res[0] and "图片" not in p_res[0] and "正面" not in p_res[0]:
                    return p_res[0]

    pattern = "(\w+片|\w+圈|\w+饼|\w+面)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "背面" not in p_res[0] and "图片" not in p_res[0] and "正面" not in p_res[0]:
                    return p_res[0]

    pattern = "(\w+脆)$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

def get_productName_voting(kvs_list,texts_list):
    pattern_pres = "^油?炸型膨化食品$|^起酥$|酥酥"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+薯[片条块]|\w{2,}土豆|[\w·]*土豆条|\w+锅巴|\w*果蔬脆|\w+脆[片棒条圈薯果角]|\w+麦角|\w+[爆鸡]米花|\w+卷|\w+玉米片|\w+荷兰豆|\w+蚕豆|\w+桃仁|\w+麦芽球|\w+燕麦球|\w+膨化球|\w+甜甜圈|\w+巧克力圈|\w+洋葱圈|\w+芝士[球条]|\w+米[球条棒]|\w+雪饼|\w*[^香]酥|\w+米[饼球条棒烧]|\w+泡芙[条圈]?|\w+火鸡面|\w+礼[盒包]|\w+虾\w?[条片]|\w*八爪烧)($|\(|\d+[k千]?[g克])"
    pattern_2 = "(\w+薯[片条]|\w+锅巴|\w*果蔬脆|\w+脆[片棒条圈薯果角]|[\w·]+土豆条|\w+[爆鸡]米花|\w+蔬菜卷|\w+多层卷|\w+玉米片|\w+荷兰豆|\w+桃仁|\w+麦芽球|\w+燕麦球|\w+膨化球|\w+甜甜圈|\w+巧克力圈|\w+洋葱圈|\w+芝士[球条]|\w+雪饼|\w*[^香]酥|\w+米[饼果球条棒烧]|\w+泡芙[条圈]?|\w+火鸡面|\w+礼[盒包]|\w+虾\w?[条片])"
    pattern_3 = "\w+味\w+\(\w*膨化食品\)|\w{4,}味\(\w*膨化食品\)|\w+\(\w+味\)$"
    pattern_4 = "(\w*薯[片条]|\w*脆[片棒条圈薯果]|\w*[爆鸡]米花|\w*蔬菜卷|\w+多层卷|\w*玉米片|\w*荷兰豆|\w*桃仁|\w*膨化球|\w*甜甜圈|\w*巧克力圈|\w*洋葱圈|\w*芝士[球条]|\w*年糕条?|\w*雪饼|\w*米[果烧]|\w*泡芙[条圈]?|\w*火鸡面|\w*礼盒|\w*虾\w?[条片])"
    pattern_5 = "(\w+[^\d图\W]片|\w+圈|\w+薯|\w+饼|\w+[脆]面|\w+[^真好太]棒|\w*[^香够]脆|\w*香[酥脆][\w\(\)-]+)($|\(|\d+[k千]?[g克])"
    pattern_6 = "(\w+[^\d图\W]片|\w+圈|\w+饼|\w+[脆]面|\w+膨化食品$)"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]) and len(k) < 6:
                    if len(kv[k]) < 2:
                        continue
                    if len(re.compile("[薯片条脆棒圈果卷球饼酥豆角]|泡芙|锅巴|[爆鸡]米花|礼包").findall(kv[k])) == 0 or len(kv[k]) == 2:
                        result_list_tmp.append(kv[k])
                    elif len(kv[k]) > 2:
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
                if "的" not in text and "是" not in text and "酥脆" not in text and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
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
                if "的" not in p_res[0] and "是" not in p_res[0] and "酥脆" not in text and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 2 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "是" not in p_res[0] and "酥脆" not in text and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
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
                if "的" not in text and "是" not in text and "酥脆" not in text and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 2 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_5)
            if len(p_res) > 0:
                p_res = p_res[0]
                if "包装" not in text and "背面" not in p_res[0] and "图片" not in p_res[0] and "正面" not in p_res[0] and "酥脆" not in text and len(re.compile("[市的是,，、]").findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    continue

    if product_name_tmp != "不分":
        return product_name_tmp

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 2 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_6)
            if len(p_res) > 0:
                if "包装" not in text and "背面" not in p_res[0] and "图片" not in p_res[0] and "正面" not in p_res[0] and "酥脆" not in text and len(re.compile("[市的是,，、]").findall(text)) == 0 and len(re.compile("^含油").findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) == 2 and count[0][0] in count[1][0]:
        return count[1][0]
    return count[0][0]

def get_productName_bak(texts_list):
    result_list = []
    pattern_1 = "\w+\(\w*膨化食品\)"
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
                    pattern = r'(\d+\.?\d*)\s?(G|g|克|[千干]克|[kK][Gg]|斤|公斤)'
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
                    pattern = r'(\d+\.?\d*)\s?(G|g|克|千克|[kK][Gg]|斤|公斤)'
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
            if len(p_res) > 0 and float(p_res[0][0]) < 10000:
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

    pattern = r'\d+\.?\d*\D*[g克]\D{0,3}\d+\D?[包袋盒罐支]装?\)?'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克)\D{0,3}(\d+)\D?[包袋盒罐支]装?\)?'
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

    pattern = r'\d+\.?\d*\D*[g克][*xX]\d+[包袋盒罐支\)]?'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克)[*xX](\d+)[包袋盒罐支\)]?'
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

    pattern = r'\d+[包袋盒罐支][*xX]\d+\.?\d*\D*[g克]'
    pattern_2 = r'(\d+)[包袋盒罐支][*xX](\d+\.?\d*)\W*(g|克)'
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
    p_bak = re.compile(r'(\d+)(\s?[包袋盒罐支个]装)')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1]

    p_bak = re.compile(r'(\d+)([包袋盒罐支个])\w*(装)$')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1] + p_res[2]

    p_bak = re.compile(r'内[装含](\d+)(小?[包袋盒罐支个])')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return "内装"+ p_res[0] + p_res[1]
    return "不分"

def insertList(result,insertingList):
    result_str = ",".join(result)
    sortedResult = result.copy()
    for r_tmp in insertingList:
        index = len(sortedResult)
        for r in r_tmp[::-1]:
            if r in sortedResult:
                index = sortedResult.index(r)
            elif r in result_str:
                continue
            else:
                flag = True
                for j in sortedResult[:index + 1]:
                    if j not in Ingredients_list:
                        correct_num = LCS(r, j)
                        len_per_1 = float(correct_num / len(r))
                        len_per_2 = float(correct_num / len(j))
                        if len_per_1 > 0.5 or len_per_2 > 0.5:
                            index = sortedResult.index(j)
                            if "(" not in j :
                                sortedResult[index] = r
                            flag = False
                    else:
                        correct_num = LCS(r, j)
                        len_per_1 = float(correct_num / len(j))
                        if len_per_1 > 0.9:
                            index = sortedResult.index(j)
                            flag = False
                if flag:
                    sortedResult.insert(index, r)
                    index = sortedResult.index(r)
    return sortedResult

def insertList_bak(result,insertingList):
    sortedResult = result.copy()
    for r_tmp in insertingList:
        index = len(sortedResult)
        for r in r_tmp[::-1]:
            if r in sortedResult:
                index = sortedResult.index(r)
            else:
                flag = True
                if r not in Ingredients_list:
                    for j in sortedResult[:index+1]:
                        correct_num = LCS(r, j)
                        len_per_1 = float(correct_num / len(r))
                        len_per_2 = float(correct_num / len(j))
                        if len_per_1 > 0.5 or len_per_2 > 0.5:
                            index = sortedResult.index(j)
                            flag = False
                else:
                    for j in sortedResult[:index + 1]:
                        if j not in Ingredients_list and "(" not in j:
                            correct_num = LCS(r, j)
                            len_per_1 = float(correct_num / len(r))
                            len_per_2 = float(correct_num / len(j))
                            if len_per_1 > 0.5 or len_per_2 > 0.5:
                                index = sortedResult.index(j)
                                sortedResult[index] = r
                                flag = False
                        else:
                            correct_num = LCS(r, j)
                            len_per_1 = float(correct_num / len(j))
                            if len_per_1 > 0.9:
                                index = sortedResult.index(j)
                                flag = False
                if flag:
                    sortedResult.insert(index, r)
                    index = sortedResult.index(r)
    return sortedResult

def get_ingredients_list(texts_list):
    result = []
    result_bak = []
    for texts in texts_list:
        tmp = []
        tmp_bak_str = ""
        for text in texts:
            index = 0
            if "无添加" in text or "零添加" in text or "0添加" in text or "适量" in text or "入" in text :
                break
            # if ":" in text and len(re.compile("\w*[料科]表?:").findall(text)) == 0 and len(re.compile("\w*添加剂:").findall(text)) == 0:
            #     continue

            text = re.sub("^配?\W*[料科]表?\W*","",text)
            if text in ["海苔",]:
                continue

            for ingredient in re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\\/]", text):
                if ingredient in tmp:
                    continue
                if (ingredient in Ingredients_list and ingredient != "糖") or "固态复合调味料" in ingredient:
                    tmp.append(ingredient)
                    index += 1

            if index >= 2 :
                if ":" in text:
                    tmp_bak_str += text.split(":")[-1]
                else:
                    tmp_bak_str += text
        if len(tmp) > 0:
            result.append(tmp)
            result_bak.append([i for i in re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\(\)]", tmp_bak_str) if isIngredient(i)])

    result = [[re.sub("配料表?", "", i) for i in r] for r in result]
    result = [[re.sub("^料表?$", "", i) for i in r] for r in result]
    result = [[re.sub("\w*信息", "", i) for i in r] for r in result]
    result = [[re.sub("\w*编号", "", i) for i in r] for r in result]
    result = [[re.sub("^含有?", "", i) for i in r] for r in result]

    result_bak = [[re.sub("配料表?", "", i) for i in r] for r in result_bak]
    result_bak = [[re.sub("\w*信息", "", i) for i in r] for r in result_bak]
    result_bak = [[re.sub("^料表?$", "", i) for i in r] for r in result_bak]
    result_bak = [[re.sub("\w*编号", "", i) for i in r] for r in result_bak]
    result_bak = [[re.sub("^含有?", "", i) for i in r] for r in result_bak]

    result.sort(key=len, reverse=True)
    result_bak.sort(key=len, reverse=True)

    return result,result_bak

def get_ingredients(kvs_list, texts_list):
    pattern = r'\w*配[料科]表?$|^[料科]表?$'
    pattern_pre = r'\w*配[料科]表?\W?$|^[料科]表?\W?$'
    ingredients = []
    ingredients_group = []
    p = re.compile(pattern)
    for kvs in kvs_list:
        group = []
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    ingredients.append(re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\(\)]", kv[k]))
                    group.append([k,re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\(\)]", kv[k])])
        if len(group) > 1:
            ingredients_group.append(group)

    if len(ingredients_group) > 0:
        ingredients_group.sort(key=len,reverse=True)
        res_str = ""
        return_flags = []
        for g in ingredients_group[0]:
            tmp_list = [i for i in g[1] if isIngredient(i)]
            tmp_list_limit = [i for i in tmp_list if i in Ingredients_list]
            if tmp_list_limit != []:
                res_str += g[0] + ":" + ",".join(tmp_list) + "\n"

            return_flag = 1 if len(tmp_list_limit) > 0 else 0
            return_flags.append(return_flag)
        if sum(return_flags) > 1:
            return res_str

    if len(ingredients) == 0:
        for texts in texts_list:
            for index, text in enumerate(texts):
                p_res_pre = get_info_by_pattern(text, pattern_pre)
                total_len = len(texts)
                if len(p_res_pre) > 0:
                    tmp_str = ""
                    for i in [1,2,3,4]:
                        if index + i >= 0 and index + i < total_len:
                            tmp_list,_ = get_ingredients_list([[texts[index + i],],])
                            if len(tmp_list) > 0:
                                tmp_str += texts[index + i]
                    if tmp_str != "":
                        ingredients.append(re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\(\)]", tmp_str))

    ingredients = [[i for i in j if isIngredient(i) and len(i) < 7] for j in ingredients]
    ingredients.sort(key=len,reverse=True)
    # ingredients_list 认为是顺序可靠的，ingredients_list_bak认为内容是可靠且完整的
    ingredients_list = []
    best_score = 0
    for ingredient in ingredients:
        score = 0
        for i in ingredient:
            if i in Ingredients_list:
                score += 1
            elif not isIngredient(i):
                score -= 1
            else:
                score += 0.55

        if score > best_score:
            ingredients_list = ingredient.copy()
            best_score = score

    ingredients_list_bak,ingredients_list_bak_strs = get_ingredients_list(texts_list)
    if len(ingredients_list) == 0 :
        ingredients_list_tmp = ingredients_list_bak.copy()
        ingredients_list_tmp.extend(ingredients_list_bak_strs)
        ingredients_list_tmp = sorted(ingredients_list_tmp,key=len,reverse=True)

        if len(ingredients_list_tmp) > 0 and ingredients_list_tmp[0] != "":
            ingredients_list = ingredients_list_tmp[0].copy()

    ingredients_list = [i for i in ingredients_list if isIngredient(i)]

    result = insertList(ingredients_list, ingredients_list_bak)
    result = [re.sub(".*核苷酸二钠", "5-呈味核苷酸二钠", i) for i in result]
    result = [re.sub(".*甲氧基苯氧基.*", "2-(4-甲氧基苯氧基)丙酸钠", i) for i in result]
    result = [re.sub("^用盐$", "食用盐", i) for i in result]
    result = [re.sub("围体复合", "固体复合", i) for i in result]
    # result = sorted(list(set(result)), key=result.index)

    if len(result) > 0:
        result = ",".join(result)
    else:
        result = "不分"

    return result

def category_rule_125(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    taste = "不分"
    type = "不分"
    package = "不分"
    package_type = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    ingredients = "不分"

    brand_tmp = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,Brand_list_2,["好麦","新味","青青","AJI","MIXX","NBR","AOA","HIPP","OCOCO","MAKANAN"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("O水娃", "口水娃", brand_1)
    brand_1 = re.sub("翼友缘", "冀友缘", brand_1)

    if product_name == "不分":
        product_name = get_productName_voting(dataprocessed,datasorted)
    if product_name == "不分":
        product_name = get_productName_bak(datasorted)

    if len(re.compile("^[a-zA-Z1-9]+$").findall(product_name)) == 0:
        product_name = re.sub("^[a-zA-Z1-9\W]+","",product_name)

    product_name = re.sub("蒸麦", "燕麦", product_name)
    product_name = re.sub("器片", "薯片", product_name)
    product_name = re.sub("\(\w化\w品\)", "(膨化食品)", product_name)

    product_name = re.sub("^牌", "", product_name)
    product_name = re.sub("^[名称]+", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)

    # if (brand_1 == "不分" or product_name == "不分") and uie_obj is not None:
    #     uie_brand,uie_productname = uie_obj.get_info_UIE(datasorted)
    #     brand_1 = brand_1 if brand_1 != "不分" else uie_brand
    #     product_name = product_name if product_name != "不分" else uie_productname

    # 输出口味
    taste = get_taste(datasorted,product_name)

    # 输出类型
    if type == "不分":
        type = get_type_productName(product_name)
    if type == "不分":
        type = get_type(datasorted)

    capcity_1 = get_Capacity(dataprocessed, datasorted)
    capcity_1_bak, capcity_2 = get_Capacity_2(dataprocessed,datasorted)
    if capcity_1_bak != "不分":
        capcity_1 = capcity_1_bak
    if capcity_1 == "不分":
        capcity_1 = get_Capacity_bak(datasorted)
    if capcity_2 == "不分":
        capcity_2 = get_Capacity_2_bak(datasorted)

    if capcity_2 != "不分" and len(re.compile("(^|\D+)1($|\D+)").findall(capcity_2)) == 0:
        package = "多包装"
    else:
        package = "单包装"

    if ingredients == "不分":
        ingredients = get_ingredients(dataprocessed, datasorted)
    ingredients = re.sub("能化", "膨化", ingredients)

    if taste != "不分":
        if len(taste.split(brand_1)) > 1 and taste.split(brand_1)[-1] != "":
            taste = taste.split(brand_1)[-1]

    if type == "不分":
        if "面" in product_name or "虾条" in product_name or "虾味条" in product_name:
            type = "其他面制品"
    if "山药" in product_name:
        if "片" in product_name:
            type = "山药片"
        else:
            type = "山药"

    if "礼盒" in product_name or "礼包" in product_name:
        package = "多包装"
        type = "混合装"

    # package_type = get_package_penghua(base64strs, category_id="125")
    package_type = get_package_125(base64strs)

    result_dict['info1'] = taste
    result_dict['info2'] = package_type
    result_dict['info3'] = type
    result_dict['info4'] = package
    result_dict['info5'] = ingredients
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
    root_path = r'D:\Data\商品识别\stage_1\125-膨化食品'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        product = "3043322"
        for image_path in glob(os.path.join(root_path,product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_125(image_list)
        with open(os.path.join(root_path,product) + r'\%s_new.json'%(product),"w",encoding="utf-8") as f:
            json.dump(result_dict,f,ensure_ascii=False,indent=4)

