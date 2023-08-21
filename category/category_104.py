import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity
from utilInside import get_ingredients

'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,包装形式,类型,包装类型,配料
'''

Brand_list_1 = [i.strip() for i in set(open("Labels/104_brand_list_1",encoding="utf-8").readlines())]
Type_list = ["猪","牛","羊","鸡"]
product_name_keyWords = ["羊蝎子火锅","胸口油","牛腩煲","毛肚"]

Brand_list_1 = sorted(list(set(Brand_list_1)), key=len)

Ingredients_list_ori = [i.strip() for i in open("Labels/104_ingredients_list",encoding="utf-8").readlines()]
Ingredients_list = []
for line in Ingredients_list_ori:
    Ingredients_list.extend(re.split("[^\-0-9a-zA-Z\u4e00-\u9fa5]",line))
Ingredients_list = set(Ingredients_list)
Ingredients_list.remove("")
Ingredients_list = list(Ingredients_list)
Ingredients_list.sort(key=len,reverse=True)

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

def get_keyValue_list(kvs_list,keys):
    result = []
    tmp = []
    for kvs in kvs_list:
        for kv in kvs:
            for key in keys:
                for k in kv.keys():
                    if key in k :
                        tmp.append(kv[k])
    result.append(tmp)
    return result

def get_type(texts_list):
    result = []
    pattern = "("
    for i in Type_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and p_res[0] not in result:
                if "鸡精" not in text and "鸡蛋" not in text:
                    result.append(p_res[0])

    if len(result) == 1:
        type = result[0]
    elif len(result) > 1:
        type = "混合"
    else:
        type = "不分"
    return type

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
    pattern = "\w*羊蝎子|\w*毛肚|\w*火腿|\w*扣肉|\w*筒骨|\w*胸口油|\w*牛腩煲|\w*肘子|\w*培根"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "\w+肠$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "\w+[猪牛羊鸡]?[肉卷肠片脊排杂骨肘]+$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "\w*[猪牛羊鸡肉][肉卷肠片脊排杂]+"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "\w+肠|\w+骨"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

def get_productName_voting(kvs_list,texts_list):
    pattern_text = "[、,，.]|配料|每一"
    pattern_pres = "[的入不做吃]|^[烧炸]|配合|^腿肉$|拉出"
    result_list = []
    result_list_tmp = []
    pattern_1 = "\w*[羊牛]蝎子火?锅?|\w{2,}火腿片?|\w*扣肉|\w+筒骨|\w*胸口油|\w*牛腩[煲块]|\w*肘子|\w*培根|\w*花胶鸡|\w*狮子头|\w+火锅涮?片|\w*五香卷|\w*酱肘子?|\w*猪肚鸡|\w+酸菜鱼|[^可\W]+拼盘|\w+羊杂汤"
    pattern_2 = "\w+肠$|\w+肠[\(\)]|\w*[白黑]千层|\w+丸子?$|\w+锅底$"
    pattern_3 = "\w+[猪牛羊鸡驴兔]\w{0,3}[蹄腿脚块卷肠片脊排杂肘丝丸肚尾柳堡馅膀]+肉?$|\w+肉[块卷肠片脊排杂肘丝丸糜串粒饼馅]+$|\w+五花[肉块卷肠片丝丸馅]*$|\w*[^去\W]骨$|\w*牛腱子?$|\w+牛百叶$|\w+牛排边$|\w+牛霖$|\w+板腱$|\w+西冷$"
    pattern_4 = "\w*肥[牛羊]$|\w+兔|\w*五花肉?条|\w+上脑|\w+里脊|\w+牛腩块?|\w+前尖|\w+小排|\w*毛肚丝?|\w*黄喉|\w*[腰脑]花|\w*肋排|\w*排[骨条]|\w*牛腱子?|\w*牛百叶|\w*牛排边|\w*排骨粒|\w+牛霖|\w+板腱"
    pattern_5 = "\w*[猪牛羊鸡驴兔]\w{0,3}[蹄腿脚块卷肠片脊排杂肘丝丸肚尾柳堡膀馅]+|\w+五花肉?[肉块卷肠片丝丸]+"
    pattern_6 = "\w+肠|\w+[肚肉]$|\w+[肚肉]\(\w+\)"

    pattern_tmp = pattern_1 + "|" + pattern_2 + "|" + pattern_3 + "|" + pattern_3.replace("+","*").replace("$","\(")
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]) and len(k) < 6:
                    if len(re.compile(pattern_tmp).findall(kv[k])) == 0:
                        if len(kv[k]) > 1:
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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 2 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_6)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 and "隔夜肉" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) == 2 and count[0][0] in count[1][0]:
        return count[1][0]
    return count[0][0]

def get_Capacity(kvs_list,texts_list):
    kvs_list.sort(key=len, reverse=False)
    pattern = r'(净含量?|净重|[Nn][Ee][Tt][Ww]|[重质]量)'
    result_list = []
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\W*(G|g|克|[千干]克|kg|KG|斤|公斤)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克","斤","公斤","kg","KG","干克"]:
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
                    pattern = r'(\d+\.?\d*)\W*(G|g|克|千克|kg|KG|斤|公斤)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] == "千克" or p_res[1] == "斤" or p_res[1] == "公斤" or p_res[1] == "kg" or p_res[1] == "KG":
                                if float(p_res[0]) <= 30:
                                    return p_res[0] + p_res[1]
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= 1:
                                    return p_res[0] + p_res[1]

    return "不分"

def get_Capacity_bak(texts_list):
    result_list = []
    p = re.compile(r'^(\d+\.?\d*)\s?(Kg|g|G|kg|KG|克|千克|斤|公斤)$')
    for texts in texts_list:
        for index,text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if not isNutritionalTable(text,texts,index):
                    continue
                if p_res[1] == "千克" or p_res[1] == "斤" or p_res[1] == "公斤" or p_res[1] == "kg" or p_res[1] == "KG" or p_res[1] == "Kg":
                    if float(p_res[0]) <= 30:
                        result_list.append(p_res[0] + p_res[1])
                else:
                    if float(p_res[0]) < 5000 and "." not in p_res[0]:
                        result_list.append(p_res[0] + p_res[1])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    p = re.compile(r'(^|[^0-9a-zA-Z])(\d+\.?\d*)\s?(Kg|G|g|kg|KG|克|千克)([^0-9a-zA-Z]|$)')
    for texts in texts_list:
        for index,text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if not isNutritionalTable(text,texts,index):
                    continue
                if p_res[2] == "千克" or p_res[2] == "斤" or p_res[2] == "公斤" or p_res[2] == "kg" or p_res[2] == "KG" or p_res[2] == "Kg":
                    if float(p_res[1]) <= 30:
                        result_list.append(p_res[1] + p_res[2])
                else:
                    if float(p_res[1]) < 5000 and "." not in p_res[1]:
                        result_list.append(p_res[1] + p_res[2])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    p = re.compile(r'^(\d+\.?\d*)\s?(Kg|G|g|kg|KG|克|千克)\d+[gG克]\W?$')
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if not isNutritionalTable(text, texts, index):
                    continue
                if p_res[1] == "千克" or p_res[1] == "斤" or p_res[1] == "公斤" or p_res[1] == "kg" or p_res[1] == "KG" or \
                        p_res[1] == "Kg":
                    if float(p_res[0]) <= 30:
                        result_list.append(p_res[0] + p_res[1])
                else:
                    if float(p_res[0]) < 5000 and "." not in p_res[0]:
                        result_list.append(p_res[0] + p_res[1])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    p = re.compile(r'(\d+\.?\d*)\s?(Kg|G|g|kg|KG|克|千克)([^0-9a-zA-Z]|$)')
    for texts in texts_list:
        for index,text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if not isNutritionalTable(text,texts,index):
                    continue
                if p_res[1] == "千克" or p_res[1] == "斤" or p_res[1] == "公斤" or p_res[1] == "kg" or p_res[1] == "KG" or \
                        p_res[1] == "Kg":
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

    pattern = r'\d+\.?\d*\D*[g克斤]\D{0,3}\d+\D*[包袋盒罐]装?\)?'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克|千克|kg|斤|公斤)\D{0,3}(\d+)\D*[包袋盒罐]装?\)?'
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

    pattern = r'\d+\.?\d*\D*[g克斤][*xX]\d+[包袋盒罐\)]?'
    pattern_2 = r'(\d+\.?\d*)\W*(g|克|千克|kg|斤|公斤)[*xX](\d+)[包袋盒罐\)]?'
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

def get_EXP_all(texts_list):
    pattern = "-18[度C][\u4e00-\u9fa5]*\d+个?[天月]|零下18[度C][\u4e00-\u9fa5]*\d+个?[天月]"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]
    return "不分"

def get_process(kvs_list,texts_list,EXP,store,product_name):
    pattern_standard = "GB/?T?2726|[^非]*熟制品"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_standard)
            if len(p_res) > 0:
                return "熟肉（冷冻）"

    S = "（冷冻）"
    T = "不分"
    if "0-4" in EXP or "冷藏" in EXP or "0-4" in store or "冷藏" in store:
        S = "（非冷冻）"

    pattern = "调制食?品|菜肴制品"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                T = "半成品"

    pattern = "[丸肠饼]"
    if len(re.compile(pattern).findall(product_name)) > 0:
        T = "半成品"

    if T == "不分":
        pattern_mix = r'\w*配[料科]表?$|^[料科]表?$'
        ingredients = []
        for kvs in kvs_list:
            for kv in kvs:
                for k in kv.keys():
                    p_res = get_info_by_pattern(kv[k],pattern_mix)
                    if len(p_res) > 0:
                        ingredients.append(re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\(\)]", kv[k]))

        for ingredient in ingredients:
            if len(re.compile("[,、，盐糖料钠]").findall(ingredient)) > 0:
                T = "半成品"
                break
            if len(re.compile("[肉蹄腿脚块卷肠片脊排杂肘丝丸肚尾柳堡馅膀]$").findall(ingredient)) > 0:
                T = "生肉"

    if T == "不分":
        T = "生肉"
    return T + S

def category_rule_104(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    EXP = "不分"
    store = "不分"
    type = "不分"
    package = "不分"
    processed_method = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    type_list = []
    brand_tmp = "不分"
    ingredients = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,[],["家宴","好帮手","小羔羊","餐时","迎宾","安大","美好","包原味","一腿"],["盒马"])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("羊馆叔叔", "羊倌叔叔", brand_1)
    brand_1 = re.sub("儿草原路过", "从草原路过", brand_1)
    brand_1 = re.sub("HiLOFRESH", "嗨啰HILO FRESH", brand_1)

    # product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(dataprocessed,datasorted)

    # if (brand_1 == "不分" or product_name == "不分") and uie_obj is not None:
    #     uie_brand,uie_productname = uie_obj.get_info_UIE(datasorted)
    #     brand_1 = brand_1 if brand_1 != "不分" else uie_brand
    #     product_name = product_name if product_name != "不分" else uie_productname

    product_name = re.sub("肥午", "肥牛", product_name)
    product_name = re.sub("午肉", "牛肉", product_name)
    product_name = re.sub("[盖落关]羊", "羔羊", product_name)
    product_name = re.sub("营冷", "西冷", product_name)
    product_name = re.sub("机肘子", "扒肘子", product_name)
    product_name = re.sub("牛子骨", "牛仔骨", product_name)
    product_name = re.sub("^饲", "谷饲", product_name)
    product_name = re.sub("^NAME", "", product_name)

    product_name = re.sub("^\w?\W+", "", product_name)

    if product_name == "":
        product_name = "不分"

    EXP = get_EXP_all(datasorted)
    if EXP != "不分":
        EXP = re.sub("^-", "零下", EXP)
        EXP = re.sub("[度C]", "度", EXP)

    if EXP == "不分":
        store = get_EXP_store(dataprocessed, datasorted)
        EXP = get_EXP(dataprocessed, datasorted)

        store = re.sub("^-","零下",store)
        store = re.sub("[度C]?以下", "度以下", store)
        store = re.sub("0[度Cc]?[-至]4[度C]?", "0-4度", store)
        EXP = re.sub("^-", "零下", EXP)
        EXP = re.sub("[度C]?以下", "度以下", EXP)
        EXP = re.sub("0[-至]4[度C]?", "0至4度", EXP)
        EXP = re.sub("0[-至]5[度C]?", "0至5度", EXP)

        if len(re.compile("\d$").findall(store)) > 0:
            store += "度"

        store = "零下18度以下冷冻保存" if store == "冷冻" or store == "不分" else store
        if store != "不分":
            if EXP != "不分" and len(re.compile(r'(-?\d+[-至]\d+[度C]|零下\d+以?下?|-\d+[度C]?以?下?|冷藏|冷冻|常温)').findall(EXP)) == 0:
                EXP = store + EXP

    capcity_1 ,capcity_2= get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋罐", 0)

    if product_name != "不分":
        for i in Type_list:
            if i in product_name:
                type_list.append(i)
        if len(type_list) == 1:
            type = type_list[0]
        if len(type_list) > 1:
            type = "混合"

    if type == "不分":
        type = get_type([[product_name,],])
    if type == "不分":
        type = get_type(datasorted)

    processed_method = get_process(dataprocessed,datasorted,EXP,store,product_name)
    package = get_package_104(base64strs)
    ingredients = get_ingredients(dataprocessed, datasorted,Ingredients_list)

    result_dict['info1'] = package
    result_dict['info2'] = EXP
    result_dict['info3'] = type
    result_dict['info4'] = processed_method
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

    # 全部配料
    result_dict['info19'] = ingredients

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_1\104-生肉类'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3043478"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_104(image_list)
        with open(os.path.join(root_path, product) + r'\%s_new.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)