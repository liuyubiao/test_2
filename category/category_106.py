import os
import re

from util import *
from glob import glob
# from utilCapacity import get_capacity
from utilInside import get_ingredients

'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,包装形式,类型,包装类型,配料
'''

Brand_list_1 = [i.strip() for i in set(open("Labels/106_brand_list_1",encoding="utf-8").readlines())]
Brand_replace_dict_1 = {i.strip().split(':')[0]:i.strip().split(':')[1] for i in set(open("Labels/106_brand_list_3", encoding="utf-8").readlines())}
Type_list = [i.strip() for i in set(open("Labels/106_type_list",encoding="utf-8").readlines())]
Type_list.sort(key=len,reverse=True)

Ingredients_list_ori = [i.strip() for i in open("Labels/106_ingredients_list",encoding="utf-8").readlines()]
Ingredients_list = []
for line in Ingredients_list_ori:
    Ingredients_list.extend(re.split("[^\-0-9a-zA-Z\u4e00-\u9fa5]",line))
Ingredients_list = set(Ingredients_list)
Ingredients_list.remove("")
Ingredients_list = list(Ingredients_list)
Ingredients_list.sort(key=len,reverse=True)

jipi = ["海星","海胆","海蜇","海参","海葵"]

ruanti = ["鱿鱼","章鱼","墨鱼","乌贼","泥鳅","籽乌","墨斗鱼","海肠","非即食的海蜇"]
#贝类
bei = ["贝","花蛤","蛏子","生蚝","扇贝","带子","蚌","鲍","蛤","蚝","花甲","蛎","蛎蝗","牡蛎","螺","青口贝","全贝","鲜贝","蚬","柱连籽","小仁仙","瑶柱","青口","象拔蚌","贻贝"]



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

def get_brand(kvs_list):
    pattern = r'(生产商|经销商)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    return kv[k].replace("有限公司","").replace("有限责任公司","").replace("实业","")
    return "不分"


def get_productName_voting(texts_list):
    result_list = []
    pattern_1 = "(\w+虾[仁滑球饼]|\w*鱼[滑腩柳]|\w+鱼[片段饼籽]|\w+鱼豆腐|\w+三文鱼|\w{2,}切片|\w+生蚝|\w+[带鱿章墨]鱼圈?|\w+海[星胆蜇参葵带]|\w+极[参]|\w+花蛤|\w+乌贼|\w+[蛏蚬]子|\w+乌贼|\w+大闸蟹|\w+叉尾鮰|\w+叉尾触|\w*墨鱼仔|\w*大黄鱼)($|\()"
    pattern_2 = "(\w+虾[仁滑球饼]|\w+鱼[片段块饼滑腩柳]|\w+鱼豆腐|\w+三文鱼|\w+生蚝|\w+[带鱿章墨鲳鲈]鱼|\w+海[星胆蜇参葵]|\w+花蛤|\w+乌贼|\w+[蛏蚬]子|\w+乌贼|\w+大闸蟹|\w+大黄鱼)"
    pattern_3 = pattern_2.replace("+","*")
    pattern_4 = "\w+[鱼虾贝蟹藻]$"

    pattern_res = "[的是用不做]|[好类][虾鱼]$|含有|加油虾$|宝贝|所有|放入|这款"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_res).findall(p_res[0])) == 0 :
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if len(re.compile(pattern_res).findall(p_res[0])) == 0 :
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if len(re.compile(pattern_res).findall(p_res[0])) == 0 :
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                if len(re.compile(pattern_res).findall(p_res[0])) == 0 :
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    return count[0][0]


def get_Capacity(kvs_list,texts_list):
    pattern = r'(净含量?|净重|[Nn][Ee][Tt][Ww]|重量|毛重)'
    pattern1 = r'(\d+\.?\d*)\W*(G|g|克|千克|kg|KG|斤|公斤)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:

                    p_res = re.compile(pattern1).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] == "千克" or p_res[1] == "斤" or p_res[1] == "公斤" or p_res[1] == "kg" or p_res[1] == "KG":
                                if float(p_res[0]) <= 30:
                                    return p_res[0] + p_res[1]
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= 1:
                                    return p_res[0] + p_res[1]

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

    p = re.compile(r'(^|[^0-9a-zA-Z])(\d+\.?\d*)\s?(Kg|G|g|kg|KG|克|千克)')
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if not isNutritionalTable(text, texts, index):
                    continue
                if p_res[2] == "千克" or p_res[2] == "斤" or p_res[2] == "公斤" or p_res[2] == "kg" or p_res[2] == "KG" or \
                        p_res[2] == "Kg":
                    if float(p_res[1]) <= 30:
                        result_list.append(p_res[1] + p_res[2])
                else:
                    if float(p_res[1]) < 5000 and "." not in p_res[1]:
                        result_list.append(p_res[1] + p_res[2])

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

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    p = re.compile(r'(\d+\.?\d*)\s?(Kg|G|g|kg|KG|克|千克)')
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

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    return count[0][0]

def get_Capacity_2(texts_list):
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

def get_EXP_bak(texts_list):
    pattern = re.compile('([保质期])(\d+个月)\w*(-\d+)')
    for txt in texts_list:
        text_str = "".join(txt)
        p_res = get_info_by_pattern(text_str, pattern)
        if len(p_res) > 0:
            degree=abs(int(p_res[0][2]))
            if degree>10:
                continue
            result = p_res[0][2].replace('-', '零下') + '度' + p_res[0][1]
            return result

    pattern = '([质期]).*(\d+天).*(\d-\d+C|\d-\d+度|\d-\d+c)'
    for txt in texts_list:
        text_str = "".join(txt)
        p_res = get_info_by_pattern(text_str, pattern)
        if len(p_res) > 0:
            result = p_res[0][2].replace('c', '度').replace('C', '度') + p_res[0][1]
            return result
    pattern = '([质期]).*(\d+天).*(\d:\d+|\d-\d+冷|\dC-\dC)'
    for txt in texts_list:
        text_str = "".join(txt)
        p_res = get_info_by_pattern(text_str, pattern)
        if len(p_res) > 0:
            result = p_res[0][2].replace(':','-').replace('冷','').replace('C','') +'度'+ p_res[0][1]
            return result
    pattern = '(储存).*(-\d+至-\d+).*([质期:])(\d+个月)'
    for txt in texts_list:
        text_str = "".join(txt)
        p_res = get_info_by_pattern(text_str, pattern)
        if len(p_res) > 0:
            result = p_res[0][1].replace('-', '零下') + '度' + p_res[0][3]
            return result
    pattern = '([质期:])(\d+个月).*(保存条件:-\d+)'
    for txt in texts_list:
        text_str = "".join(txt)
        p_res = get_info_by_pattern(text_str, pattern)
        if len(p_res) > 0:
            result = p_res[0][2].replace('保存条件', '').replace('-', '零下')  + '度' + p_res[0][1]
            return result
    return '不分'

def get_EXP(kvs_list,texts_list):

    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    p_1 = re.compile(r'[0-9一-十]+个?[年天月]')
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    p_res_1 = p_1.findall(kv[k])
                    if len(p_res_1) > 0:
                        if len(re.compile(r'20[12]\d年[01]?\d月[0123]?\d日?').findall(kv[k])) > 0:
                            continue
                        return kv[k]

    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    if kv[k] in ["12","18"]:
                        return kv[k] + "个月"

    pattern = "-?\d{0,2}[-至]\d+[度C]?以?下?\d+个月|零下\d+以?下?\d+个月|-\d+以?下?\d+个月"
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                tmp_list.append(p_res[0])
        if len(tmp_list) > 0:
            return ",".join(tmp_list)


    pattern = r'(\D+[12]年|^[12]年|\d+个月|[一-十]+个月|\d+天)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "无理由" not in text and "退" not in text and '挂果期' not in text:
                return p_res[0]

    pattern = r'20[12]\d[-\\/\s\.]?[01]\d[-\\/\s\.]?[0123][\d]'
    date_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                date_list.append(re.sub("\D","",p_res[0]))

    for ddate in date_list:
        try:
            d0 = datetime.datetime.strptime(ddate, "%Y%m%d")
        except:
            date_list.remove(ddate)

    date_list = list(set(date_list))
    date_list.sort(reverse=True)
    if len(date_list) >=2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y%m%d")
        df = datetime.datetime.strptime(date_list[-1], "%Y%m%d")
        d_res = (d0 - df).days
        if d_res > 1:
            if d_res>800:
                return '不分'
            return str(d_res) + "天"

    pattern = r'20[12]\d年[01]?\d月[0123]?\d日?'
    date_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "日" not in p_res[0]:
                    date_list.append(p_res[0] + "日")
                else:
                    date_list.append(p_res[0])

    for ddate in date_list:
        try:
            d0 = datetime.datetime.strptime(ddate, "%Y年%m月%d日")
        except:
            date_list.remove(ddate)

    date_list = list(set(date_list))
    date_list.sort(reverse=True)
    if len(date_list) >= 2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y年%m月%d日")
        df = datetime.datetime.strptime(date_list[-1], "%Y年%m月%d日")
        d_res = (d0 - df).days
        if d_res > 1:
            if d_res>800:
                return '不分'
            return str(d_res) + "天"

    return "不分"

def get_Exp_new(dataprocessed,datasorted):
    EXP = get_EXP_bak(datasorted)
    if EXP == "不分":
        EXP = get_EXP(dataprocessed, datasorted)
        EXP = EXP.replace('存', '').replace(',', '，').replace('C', '度').replace('-18以下', '零下18度').replace('冷冻存',
                                                                                                         '').replace(
            '监条件:', '').replace('18C及以下', '零下18度').replace('18度及以下', '零下18度')
        pattern = '^-\d+度'
        p_res = get_info_by_pattern(EXP, pattern)
        if len(p_res) > 0:
            EXP = EXP.replace('-', '零下')
        EXP = EXP.replace('保', '')
        pattern = '\d天'
        p_res = get_info_by_pattern(EXP, pattern)

        if '-' not in EXP and '零下18度' not in EXP and '常温' not in EXP and EXP != '不分' and len(p_res) == 0:
            EXP = '零下18度' + EXP
    EXP = EXP.replace('冷冻', '').replace('保', '').replace(':', '')
    return EXP

def get_package_106(base64strs):
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

    if "真空袋" in result_shape:
        return "真空塑料袋"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if material == "塑料底" or "塑料" in material:
        material = "塑料"
    elif material == "玻璃底":
        material = "玻璃"

    if "袋" in shape:
        shape = "袋"
    elif "托盘" in shape:
        shape = "托盘"
    else:
        shape = "盒"

    return material + shape

def get_key_Value_106(kvs_lists,list_key):
    result_list = []
    for kvp_list in kvs_lists:
        for kvp in kvp_list:
            keys_list = kvp.keys()
            for key in list_key:
                if key in keys_list:
                    kvalue = kvp[key]
                    if len(kvalue)>=2:
                        result_list.append(kvalue)

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) >1 and count[0][1] == count[1][1] and len(count[0][0]) < len(count[1][0]) and len(re.compile("[0-9,，、]").findall(count[1][0])) == 0:
        return count[1][0]
    else:
        return count[0][0]

# 提取存储温度/加工程度
def get_store_temperature_process(EXP,kvs_list,texts_list):
    '''
    提取存储温度/加工程度
    提取依据：106定义文档
    存储温度/加工程度，共四种数据类型：生肉(冷冻)、生肉(非冷冻)、半成品(冷冻)，半成品(非冷冻)
    1、需要从包装后面的原料（配料）和贮藏方法（储存方式）里找。
    2、生肉(冷冻)：配料表中只有肉，没有任何配料、调料的且在0摄氏度以下，一般为-10℃、-18℃等，跨冷冻和非冷冻温度的，取最低温度（通常标号为GB2707、GB16869
    3、生肉(非冷冻)：配料表中只有肉，没有任何配料、调料的且0摄氏度以上（包括0℃，一般为“0-4度”、“-2-2度”）或没有标注具体温度，只写“可冷藏也可冷冻”的
    4、半成品(冷冻)：配料表中不仅有肉，还有其他配料、调料的且在0摄氏度以下，一般为-10℃、-18℃等，跨冷冻和非冷冻温度的，取最低温度（通常标号为GB2707、GB16869）
    5、半成品(非冷冻)：配料表中不仅有肉，还有其他配料、调料的且0摄氏度以上（包括0℃，一般为“0-4度”、“-2-2度”）或没有标注具体温度，只写“可冷藏也可冷冻”的
    :param EXP: 保质期
    :param kvs_list: 文本键值对
    :param texts_list: 文本列表
    :return:
    '''
    semi_finished_products = '生肉'
    mixture_list = ['食盐','食用盐','食用站','白砂糖','白砂器','食品添加剂','味精','植物油','调味料','鸡蛋清','大豆油','鸡蛋白','香辛料','碳酸钠','保持剂','磷龄钠']
    freeze = ''
    if '零下18度' in EXP or '冷冻' in EXP:
        freeze = '冷冻'
    elif '0-4度' in EXP:
        freeze = '非冷冻'
    result = get_key_Value_106(kvs_list, ['配料表','配科表','配料','配科','成分','酱料包'])
    if result!='不分':
        for it in mixture_list:
            if it in result:
                semi_finished_products ='半成品'
                break

    if result == '不分' or len(freeze)==0 or semi_finished_products == '生肉':
        for texts in texts_list:
            for txt in texts:
                if len(freeze) == 0:
                    if '冷藏' in txt:
                        freeze = '非冷冻'
                    elif '冷冻' in txt:
                        freeze = '冷冻'
                for it in mixture_list:
                    if it in txt:
                        semi_finished_products = '半成品'
                        break

    if len(freeze) == 0:
        freeze = '冷冻'
    result = '%s（%s）' %(semi_finished_products,freeze)
    return result

def category_rule_106(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    product_replace_dict_1={'·':'','鲜皮':'紫皮','鍋鱼':'鲳鱼','馒鱼':'鳗鱼','献鱼':'鱿鱼','赠鱼':'鳕鱼','渍鱼':'鲭鱼',
                            '鲮':'鲅','/':'','叉尾触':'叉尾鮰','潮海':'渤海','福美海产':'禧美海产'}
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    EXP = "不分"
    type = "不分"
    package = "不分"
    store_temperature_process = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    ingredients = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed,["商标"])
    brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["新梦想","鲜食","美佳","海星","远洋","海优","华贵","明奋","七鲜"], [])
    # if brand_1 == "不分":
    #     brand_1 = get_brand(dataprocessed)
    for key in Brand_replace_dict_1.keys():
        brand_1 = re.sub(key, Brand_replace_dict_1.get(key), brand_1)

    product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)
    for key in product_replace_dict_1.keys():
        product_name = re.sub(key, product_replace_dict_1.get(key), product_name)

    product_name = re.sub("\d+袋包邮","",product_name)

    product_name = re.sub("^\w*名称", "", product_name)
    product_name = re.sub("^\w*品名", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    if product_name != "不分":
        for i in Type_list:
            if i in product_name:
                type = i
                break
        if type == "不分":
            type = get_type(datasorted)
    EXP = get_Exp_new(dataprocessed,datasorted)


    capcity_1 = get_Capacity(dataprocessed, datasorted)
    capcity_1_bak, capcity_2 = get_Capacity_2(datasorted)
    if capcity_1_bak != "不分" and capcity_1_bak[0] != "0":
        capcity_1 = capcity_1_bak
    if capcity_1 == "不分":
        capcity_1 = get_Capacity_bak(datasorted)
    if capcity_2 == "不分":
        capcity_2 = get_Capacity_2_bak(datasorted)
    # #     包袋盒罐]装
    # capcity_1 ,capcity_2= get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐", 0)

    if type in jipi:
        type = "棘皮类"
    if type in bei:
        type = "贝类"
    if type in ruanti:
        type = "软体类"

    package = get_package_106(base64strs)

    store_temperature_process = get_store_temperature_process(EXP, dataprocessed, datasorted)
    ingredients = get_ingredients(dataprocessed, datasorted, Ingredients_list)

    result_dict['info1'] = package
    result_dict['info2'] = EXP
    result_dict['info3'] = type
    result_dict['info4'] = store_temperature_process
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

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
    root_path = r'D:\Data\商品识别\stage_1\106-水产品'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3055862"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_106(image_list)
        with open(os.path.join(root_path, product) + r'\%s_new.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)