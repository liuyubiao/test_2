import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity
import itertools

Brand_list_1 = [i.strip() for i in set(open("Labels/492_brand_list",encoding="utf-8").readlines())]

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

def get_type(product_name):
    result_type = "保鲜袋"
    if "膜" in product_name:
        result_type = "保鲜膜"

    if "膜" in product_name and "袋" in product_name and "袋子" not in product_name:
        info = 3
    elif "膜" in product_name:
        info = 2
    elif "袋" in product_name:
        info = 1
    else:
        info = 0

    return result_type,info

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
    pattern_text = "[、，,]"
    pattern_pres = "[的将]|避免|加热|[揭撕][开取]|放入|\d+[个只张条]"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w{2,}保鲜[袋膜]实惠装|\w{2,}保鲜[袋膜]|\w{2,}滑锁袋|\w+密实袋)($|\()"
    pattern_2 = "(\w{2,}保鲜\w+[袋膜])($|\()"
    pattern_3 = "\w{2,}保鲜\w*[袋膜]"
    pattern_4 = "(\w+[袋膜])($|[\(\)])"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 :
                        p_res = re.compile("\w+[膜袋]").findall(kv[k])
                        if len(p_res) > 0:
                            result_list.append(p_res[0])
                        else:
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
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0]:
        return count[1][0]
    return count[0][0]

def get_capacity_keyword(kvs_list,unit="[个只g克条]|[Pp][Cc][Ss]"):
    kvs_list.sort(key=len, reverse=False)
    pattern_key = r'(净含量?|净重|^含量$|[Nn][Ee][Tt][Ww]|重量)'
    result_list = []
    p = re.compile(pattern_key)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+)\s?({})'.format(unit)
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
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
                    pattern = r'(\d+)\s?({})'.format(unit)
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            result_list.append(p_res[0] + p_res[1])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return "不分"

def get_Capacity_texts(texts_list,unit = "[个只条]|[Pp][Cc][Ss]",unit_default = "只",limit_floor = 10,limit_top = 1000):
    pattern = r'(\d+)\s?({})装'.format(unit)
    result_list = []
    p = re.compile(pattern)
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                if "加量" in text:
                    continue
                p_res = p_res[0]
                result_list.append(p_res[0] + p_res[1])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0],False

    result_list = []
    pattern = r'(\d+)\s?({})'.format(unit)
    p = re.compile(pattern)
    for texts in texts_list:
        tmp_list = []
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0 and float(p_res[0][0]) < limit_top and float(p_res[0][0]) > limit_floor:
                if "加量" in text:
                    continue
                p_res = p_res[0]
                tmp_list.append(p_res[0] + p_res[1])
                result_list.append(p_res[0] + p_res[1])
        if len(tmp_list) == 1:
            return tmp_list[0],False

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0],False

    pattern = r'^\(?(\d{2,3})\)?$'
    p = re.compile(pattern)
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0 and float(p_res[0]) < limit_top and float(p_res[0]) > limit_floor and p_res[0][-1] == "0":
                if "加量" in text:
                    continue
                result_list.append(p_res[0] + unit_default)

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if count[0][1] > 1 or len(count) == 1:
            return count[0][0],True

    return "不分",True

def get_Capacity_492(texts_list):
    result_list = []
    pattern = r'^(\d{2,3})($|.?平口)'
    p = re.compile(pattern)
    for texts in texts_list:
        total_len = len(texts)
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if "加量" in text:
                    continue
                for i in [-1, 0, 1]:
                    if index + i >= 0 and index + i < total_len:
                        if "平口" in texts[index + i]:
                            result_list.append(p_res[0] + "只")

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    # pattern = r'(\d{2,3})([克g])'
    # p = re.compile(pattern)
    # for texts in texts_list:
    #     for index, text in enumerate(texts):
    #         p_res = p.findall(text)
    #         if len(p_res) > 0:
    #             p_res = p_res[0]
    #             result_list.append(p_res[0] + p_res[1])
    #
    # if len(result_list) > 0:
    #     count = Counter(result_list).most_common(2)
    #     return count[0][0]

    pattern = r'^\(?(\d{2,3})[\)PC元]{0,2}$'
    p = re.compile(pattern)
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0 and float(p_res[0]) < 800 and float(p_res[0]) >= 100:
                if "加量" in text:
                    continue
                result_list.append(p_res[0] + "只")

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if count[0][1] > 1:
            return count[0][0]

    return "不分"


def get_Capacity_plus(texts_list,unit = "[个只条]|[Pp][Cc][Ss]",limit_top = 2000):
    capacity_1 = "不分"
    capacity_2 = "不分"
    res_list = []

    result_num_list = []
    res_unit_list = []
    pattern = r'(\d+)\s?({})'.format(unit)
    for texts in texts_list:
        result_tmp_dict = {}
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                if "每份" in text:
                    continue
                for p_r in p_res:
                    if int(p_r[0]) > limit_top:
                        continue
                    if p_r[1] not in result_tmp_dict.keys():
                        result_tmp_dict[p_r[1]] = []
                    result_num_list.append(int(p_r[0]))
                    res_unit_list.append(p_r[1])

                    if int(p_r[0]) in result_tmp_dict[p_r[1]]:
                        if int(p_r[0]) < 100:
                            result_tmp_dict[p_r[1]].append(int(p_r[0]))
                    else:
                        result_tmp_dict[p_r[1]].append(int(p_r[0]))

        result_tmp_list = sorted(result_tmp_dict.items(), key= lambda x: len(x[1]), reverse=True)
        for u,num_list in result_tmp_list:
            tmp_list_1 = num_list.copy()
            if len(tmp_list_1) in [2,3] and len(tmp_list_1) > len(res_list):
                capacity_1 = str(sum(tmp_list_1)) + u
                res_list = [str(i) + u for i in tmp_list_1]
                capacity_2 = "+".join(res_list)
            break

    total_num = len(res_unit_list)
    if total_num == 0:
        return capacity_1, capacity_2, res_list

    result_unit = Counter(res_unit_list).most_common(1)[0][0]
    result_num_list = [result_num_list[i] for i in range(total_num) if res_unit_list[i] == result_unit]

    result_num_list = sorted(set(result_num_list), key=result_num_list.index)
    result_num_list_uniq = result_num_list.copy()
    result_num_list_uniq.sort()
    l = len(result_num_list_uniq)

    if l < 2:
        return capacity_1, capacity_2, res_list

    if l > 3:
        for i in range(3, l):
            for j, k, v in itertools.combinations(result_num_list_uniq[:i], 3):
                if j + k + v == result_num_list_uniq[i]:
                    j, k, v = sorted([j, k, v], reverse=True)
                    return str(result_num_list_uniq[i]) + result_unit, "%d%s+%d%s+%d%s" % (j,result_unit,k,result_unit,v,result_unit), None

    if l > 2:
        for i in range(2, l):
            for j, k in itertools.combinations(result_num_list_uniq[:i], 2):
                if j + k == result_num_list_uniq[i]:
                    j, k = sorted([j, k], reverse=True)
                    return str(result_num_list_uniq[i]) + result_unit, "%d%s+%d%s" % (j,result_unit,k,result_unit), None

    if l >= 2 and result_num_list_uniq[-1] >= 2*result_num_list_uniq[-2]:
        capacity_1 = str(result_num_list_uniq[-1]) + result_unit
        res_list = [str(i) + result_unit for i in result_num_list_uniq]
        capacity_2 = "不分"
    return capacity_1, capacity_2, res_list

def get_Capacity_mul(texts_list,unit_1 = "[个只克条]|[Pp][Cc][Ss]",unit_2 = "[卷包]",limit_top=2000):
    capacity_1 = "不分"
    capacity_2 = "不分"
    res_list = []
    pattern_1 = r'(\d+)\W*(%s)(\D{0,3})(\d+)\D?(%s)装?\)?'%(unit_1,unit_2)
    for text_list in texts_list:
        for text in text_list:
            if len(re.split("[*xX]\d", text)) > 2:
                continue
            if "每份" in text:
                continue
            p_res = get_info_by_pattern(text,pattern_1)
            if len(p_res) > 0:
                p_res = p_res[0]
                if float(p_res[0]) > limit_top:
                    continue
                unit = p_res[1]
                pre_text = p_res[0] + p_res[1] + p_res[2] + p_res[3] + p_res[4]
                if p_res[3] != "0" and p_res[3] != "":
                    if "*" in p_res[2] or "x" in p_res[2] or "X" in p_res[2]:
                        return ("%d%s" % (int(p_res[0]) * int(p_res[3]), unit)),pre_text , []
                    else:
                        return ("%d%s" % (int(p_res[0]) * int(p_res[3]), unit)),pre_text, [p_res[0] + unit]
    return capacity_1,capacity_2,res_list

def get_packagePlus(texts_list):
    pattern = "加量|补充装"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0 and "不加价" not in text:
                return "有补充装"
    return "不分"

def get_jiahou(texts_list):
    pattern = "加厚|厚实|厚韧"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "加厚"
    return "不分"

def lenth_filter(lenth_str):
    pattern = "\d+\.?\d*"
    p_res = get_info_by_pattern(lenth_str,pattern)
    if len(p_res) >= 2:
        if float(p_res[0]) < 10 or float(p_res[0]) > 1000:
            return False
        if float(p_res[1]) < 10 or float(p_res[1]) > 1000:
            return False

    return True

def get_lenth_mo(texts_list):
    pattern_1 = "\d+\.?\d*[Cc厘毫Mm][mM米][xX*]\d+\.?\d*[Cc厘毫Mm][mM米][xX*]\d+[mM米]"
    pattern_2_0 = "\d+\.?\d*[Cc厘毫Mm][mM米][xX*]\d+\.?\d*[Cc厘毫Mm][mM米]"
    pattern_2_1 = "\d+\.?\d*[Cc厘毫Mm][mM米][xX*]\d+[mM米]"
    pattern_3 = "\d+[mM米][xX*]\d+\.?\d*[Cc厘毫Mm][mM米]"
    pattern_4 = "(\d+\.?\d*[Cc厘毫Mm][mM米])\D{0,1}(\d+\.?\d*[mM米])"
    result_list = []
    res_list = []
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                p_res[0] = re.sub("[xX*]", "*", p_res[0])
                p_res[0] = re.sub("[Cc厘][mM米]", "CM", p_res[0])
                p_res[0] = re.sub("[Mm毫][mM米]", "MM", p_res[0])
                p_res[0] = re.sub("[mM米]", "M", p_res[0])
                if lenth_filter(p_res[0]):
                    result_list.append(p_res[0])
                    tmp_list.append(p_res[0])

        if len(tmp_list) > len(res_list):
            res_list = tmp_list

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0],res_list

    for texts in texts_list:
        tmp_list = []
        tmp_list_0 = []
        tmp_list_1 = []
        for text in texts:
            p_res_0 = get_info_by_pattern(text, pattern_2_0)
            p_res_1 = get_info_by_pattern(text, pattern_2_1)
            if len(p_res_0) > 0:
                p_res = p_res_0
                p_res[0] = re.sub("[xX*]", "*", p_res[0])
                p_res[0] = re.sub("[Cc厘][mM米]", "CM", p_res[0])
                p_res[0] = re.sub("[Mm毫][mM米]", "MM", p_res[0])
                p_res[0] = re.sub("[mM米]", "M", p_res[0])
                if lenth_filter(p_res[0]):
                    tmp_list_0.append(p_res[0])

            if len(p_res_1) > 0:
                p_res = p_res_1
                p_res[0] = re.sub("[xX*]", "*", p_res[0])
                p_res[0] = re.sub("[Cc厘][mM米]", "CM", p_res[0])
                p_res[0] = re.sub("[Mm毫][mM米]", "MM", p_res[0])
                p_res[0] = re.sub("[mM米]", "M", p_res[0])
                if lenth_filter(p_res[0]):
                    tmp_list_1.append(p_res[0])

        if len(tmp_list_1) > 0 and len(tmp_list_0) > 0:
            for t_1 in tmp_list_1:
                for t_0 in tmp_list_0:
                    t_s = t_0.split("*")
                    if t_s[-1] in t_1:
                        t_1 = t_s[0] + "*" + t_1
                        break
                tmp_list.append(t_1)
                result_list.append(t_1)

        if len(tmp_list) > len(res_list):
            res_list = tmp_list

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0],res_list

    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                p_res[0] = re.sub("[xX*]", "*", p_res[0])
                p_res[0] = re.sub("[Cc厘][mM米]", "CM", p_res[0])
                p_res[0] = re.sub("[Mm毫][mM米]", "MM", p_res[0])
                p_res[0] = re.sub("[mM米]", "M", p_res[0])
                if lenth_filter(p_res[0]):
                    result_list.append(p_res[0])
                    tmp_list.append(p_res[0])

        if len(tmp_list) > len(res_list):
            res_list = tmp_list

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0],res_list

    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                p_res = list(p_res[0])
                p_res[0] = p_res[0] + "*" + p_res[1]
                p_res[0] = re.sub("[xX*]", "*", p_res[0])
                p_res[0] = re.sub("[Cc厘][mM米]", "CM", p_res[0])
                p_res[0] = re.sub("[Mm毫][mM米]", "MM", p_res[0])
                p_res[0] = re.sub("[mM米]", "M", p_res[0])
                if lenth_filter(p_res[0]):
                    result_list.append(p_res[0])
                    tmp_list.append(p_res[0])

        if len(tmp_list) > len(res_list):
            res_list = tmp_list

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0],res_list

    return "不分",[]

def get_lenth_dai(texts_list):
    pattern_1 = "\d+\.?\d*[Cc厘毫Mm][mM米][xX*]\d+\.?\d*[Cc厘毫Mm][mM米]"
    pattern_2 = "(\d+\.?\d*)[xX*](\d+\.?\d*)([Cc厘毫Mm][mM米])"
    pattern_3 = "(\d+\.?\d*[Cc厘毫Mm][mM米])\D{0,1}(\d+\.?\d*[Cc厘毫Mm][mM米])"

    result_list = []
    res_list = []
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                p_res[0] = re.sub("[xX*]", "*", p_res[0])
                p_res[0] = re.sub("[Cc厘][mM米]", "CM", p_res[0])
                p_res[0] = re.sub("[Mm毫][mM米]", "MM", p_res[0])
                p_res[0] = re.sub("[mM米]", "M", p_res[0])
                if lenth_filter(p_res[0]):
                    result_list.append(p_res[0])
                    tmp_list.append(p_res[0])

        if len(tmp_list) > len(res_list):
            res_list = tmp_list

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0], res_list

    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                p_res = list(p_res[0])
                p_res[2] = re.sub("[Cc厘][mM米]", "CM", p_res[2])
                p_res[2] = re.sub("[Mm毫][mM米]", "MM", p_res[2])
                p_res[2] = re.sub("[mM米]", "M", p_res[2])
                p_res[0] = p_res[0] + p_res[2] + "*" + p_res[1] + p_res[2]
                if lenth_filter(p_res[0]):
                    result_list.append(p_res[0])
                    tmp_list.append(p_res[0])

        if len(tmp_list) > len(res_list):
            res_list = tmp_list

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0], res_list

    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                p_res = list(p_res[0])
                p_res[0] = p_res[0] + "*" + p_res[1]
                p_res[0] = re.sub("[xX*]", "*", p_res[0])
                p_res[0] = re.sub("[Cc厘][mM米]", "CM", p_res[0])
                p_res[0] = re.sub("[Mm毫][mM米]", "MM", p_res[0])
                p_res[0] = re.sub("[mM米]", "M", p_res[0])
                if lenth_filter(p_res[0]):
                    result_list.append(p_res[0])
                    tmp_list.append(p_res[0])

        if len(tmp_list) > len(res_list):
            res_list = tmp_list

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0], res_list

    return "不分", []

def get_lenth_bak(texts_list,info):
    pattern_1 = "(\d+)(厘米|CM|cm|MM|mm)[xX*]?[宽长]?(\d+)(厘米|CM|cm|MM|mm)"
    pattern_2 = "(^|\()\D?([1234]\d)[宽长]?([1234]\d)(厘米|CM|cm|MM|mm)"
    pattern_3 = "([1234]\d)(厘米|CM|cm|MM|mm)[xX*]?([1234]\d)$"
    pattern_4 = "([1234]\d)(厘米|CM|cm|MM|mm)[xX*]?([1234]\d)(厘米|CM|cm|MM|mm)"
    result = "不分"
    result_2 = "不分"
    result_list = []
    result_list_2 = []
    res_list = []
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                p_res = list(p_res[0])
                p_res[0] = p_res[0] + p_res[1] + "*" + p_res[2] + p_res[3]
                p_res[0] = re.sub("[Cc厘][mM米]", "CM", p_res[0])
                p_res[0] = re.sub("[Mm毫][mM米]", "MM", p_res[0])
                if lenth_filter(p_res[0]):
                    result_list.append(p_res[0])
                    tmp_list.append(p_res[0])

        if len(tmp_list) > len(res_list):
            res_list = tmp_list

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        result = count[0][0]

    if result == "不分":
        for texts in texts_list:
            tmp_list = []
            for text in texts:
                p_res = get_info_by_pattern(text, pattern_2)
                if len(p_res) > 0:
                    p_res = list(p_res[0])
                    p_res[0] = p_res[1] + p_res[3] + "*" + p_res[2] + p_res[3]
                    p_res[0] = re.sub("[Cc厘][mM米]", "CM", p_res[0])
                    p_res[0] = re.sub("[Mm毫][mM米]", "MM", p_res[0])
                    if lenth_filter(p_res[0]):
                        result_list.append(p_res[0])
                        tmp_list.append(p_res[0])

            if len(tmp_list) > len(res_list):
                res_list = tmp_list

        if len(result_list) > 0:
            count = Counter(result_list).most_common(2)
            result = count[0][0]

    if result == "不分":
        for texts in texts_list:
            tmp_list = []
            for text in texts:
                p_res = get_info_by_pattern(text, pattern_3)
                if len(p_res) > 0:
                    p_res = list(p_res[0])
                    p_res[0] = p_res[0] + p_res[1] + "*" + p_res[2] + p_res[1]
                    p_res[0] = re.sub("[Cc厘][mM米]", "CM", p_res[0])
                    p_res[0] = re.sub("[Mm毫][mM米]", "MM", p_res[0])
                    if lenth_filter(p_res[0]):
                        result_list.append(p_res[0])
                        tmp_list.append(p_res[0])

            if len(tmp_list) > len(res_list):
                res_list = tmp_list

        if len(result_list) > 0:
            count = Counter(result_list).most_common(2)
            result = count[0][0]

    for texts in texts_list:
        tmp_list = []
        text_str = "".join(texts)
        p_res = get_info_by_pattern(text_str, pattern_4)
        if len(p_res) > 0:
            p_res = list(p_res[0])
            p_res[0] = p_res[0] + p_res[1] + "*" + p_res[2] + p_res[3]
            p_res[0] = re.sub("[Cc厘][mM米]", "CM", p_res[0])
            p_res[0] = re.sub("[Mm毫][mM米]", "MM", p_res[0])
            if lenth_filter(p_res[0]):
                result_list.append(p_res[0])
                tmp_list.append(p_res[0])

        if len(tmp_list) > len(res_list):
            res_list = tmp_list

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        result = count[0][0]

    if info == 2:
        pattern_0 = "(^|\(|CM|cm|厘米)(\d+)[Mm米]"
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern_0)
                if len(p_res) > 0:
                    p_res = p_res[0]
                    result_list_2.append(p_res[1] + "M")

        if len(result_list_2) > 0:
            count = Counter(result_list_2).most_common(2)
            result_2 = count[0][0]

    if result_2 != "不分" and result != "不分":
        return result + "*" + result_2,[]

    return result,res_list

def get_lenth(texts_list,flag,info):
    res_single = "不分"
    if info == 3:
        flag = True

    if info in [0,1]:
        res_single,res_list = get_lenth_dai(texts_list)
    elif info in [2]:
        res_single,res_list = get_lenth_mo(texts_list)
    else:
        dai_single,dai_list = get_lenth_dai(texts_list)
        mo_single,mo_list = get_lenth_mo(texts_list)

        res_list = dai_list.copy()
        res_list.extend(mo_list)

    if res_single == "不分":
        res_single, res_list = get_lenth_bak(texts_list,info)

    res_list = sorted(list(set(res_list)), key=res_list.index)
    if flag and len(res_list) > 0:
        return "，".join(res_list)

    return res_single

def get_use_dai(product_name,texts_list_ori,package):
    pattern_1 = "密[封实]\w*袋|[双滑]锁"
    pattern_2 = "背心|手提"
    pattern_3 = "点断|断点|手撕|抽取"

    flag_1 = False
    flag_2 = False
    flag_3 = False

    if package == "袋装":
        flag_3 = True

    texts_list = texts_list_ori.copy()
    texts_list.append([product_name, ])

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                return "抽取式，密封"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                flag_1 = True

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                for p_r in p_res:
                    if p_r in ["点断","断点","手撕"]:
                        flag_2 = True
                    if p_r in ["抽取"]:
                        flag_3 = True

    if flag_1:
        if flag_3:
            return "抽取式，背心"
        elif not flag_2:
            return "点断式（手撕式），背心"
    else:
        if flag_3:
            return "抽取式，普通"

    return "点断式（手撕式），普通"

def get_use_mo(texts_list):
    pattern_1 = "背心|点断"
    pattern_2 = "刀切|滑刀|切刀"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                return "点断式（手撕式）"
    flag_2 = False
    flag_1 = False
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0 and "免" not in text:
                flag_1 = True
            elif len(p_res) > 0 and "免" in text:
                flag_2 = True

    if flag_2:
        return "点断式（手撕式）"
    if flag_1:
        return "切割式（滑刀式）即包装盒上有刀片"

    return "点断式（手撕式）"

def get_package_492(base64strs):
    url_shape = url_classify + ':5029/yourget_opn_classify'
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    result_shape = task_shape.get_result()

    if len(result_shape) > 0:
        shape = Counter(result_shape).most_common(1)[0][0]
        if "袋" in shape:
            shape = "袋装"
        elif shape in ["托盘","格","盒"]:
            shape = "纸盒"
        else:
            shape = "卷筒"
        return shape
    else:
        return "卷筒"

def category_rule_492(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    type = "不分"
    package_plus = "不分"
    length = "不分"
    package_type = "不分"
    use_dai = "不分"
    use_mo = "不分"
    jiahou = "不分"
    package = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["GLAD","好帮手","洁家","3M","新鲜生活","世家","EZn","清纯"], [])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("品幕", "品慕", brand_1)
    brand_1 = re.sub("CHAHUA茶花", "茶花CHAHUA", brand_1)
    brand_1 = re.sub("纤风菜", "纤风采", brand_1)
    brand_1 = re.sub("缅慕诺", "絔慕诺", brand_1)

    capcity_1 = get_capacity_keyword(dataprocessed)
    capcity_flag = False
    if capcity_1 == "不分":
        capcity_1, capcity_flag = get_Capacity_texts(datasorted, unit="[张个只条]|[Pp][Cc][Ss]")
    # 加法重容量
    capcity_1_plus, capcity_2_plus, flag_list_plus = get_Capacity_plus(datasorted, unit="[个只卷条]|[Pp][Cc][Ss]")
    if capcity_1 != capcity_1_plus:
        if capcity_1_plus != "不分":
            if flag_list_plus is None or capcity_flag:
                capcity_1 = capcity_1_plus
                capcity_2 = capcity_2_plus
            else:
                if capcity_1 != "不分" and capcity_1 in flag_list_plus and len(flag_list_plus) < 4:
                    capcity_1 = capcity_1_plus
                    capcity_2 = capcity_2_plus
    else:
        capcity_2 = capcity_2_plus

    # 乘法重容量
    capcity_1_mul, capcity_2_mul, flag_list_mul = get_Capacity_mul(datasorted, unit_1="[个只克条米]|[Pp][Cc][Ss]")
    if capcity_1 == "不分" or capcity_1 in flag_list_mul:
        capcity_1 = capcity_1_mul
        capcity_2 = capcity_2_mul

    if len(re.compile("^\d[张条只个]").findall(capcity_1)) > 0:
        capcity_1 = "不分"
    if capcity_1 == "不分":
        capcity_1 = get_Capacity_492(datasorted)
        if capcity_1 == "不分":
            capcity_1 = "1卷"

    package_flag = capcity_2 != "不分"

    if package_flag:
        package_type = "多包"
    else:
        package_type = "单包"

    # datasorted = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("^心型", "背心型", product_name)
    product_name = re.sub("昔心", "背心", product_name)
    product_name = re.sub("密袋", "密实袋", product_name)
    product_name = re.sub("厚卖", "厚实", product_name)
    product_name = re.sub("占断", "点断", product_name)
    product_name = re.sub("纤风菜", "纤风采", product_name)
    product_name = re.sub("缅慕诺", "絔慕诺", product_name)

    product_name = re.sub("^\w保鲜袋", "保鲜袋", product_name)
    product_name = re.sub("^\w保鲜膜", "保鲜膜", product_name)
    product_name = re.sub("^[号用]", "", product_name)

    product_name = re.sub("^\w*名称", "", product_name)
    product_name = re.sub("^\w*品名", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    type, info = get_type(product_name)
    package = get_package_492(base64strs)

    if info == 0:
        use_dai = "点断式（手撕式），普通"
        use_mo = "不分（不属于上述选项的）"
    elif info == 1:
        use_dai = get_use_dai(product_name, datasorted, package)
        use_mo = "不分（不属于上述选项的）"
    elif info == 2:
        use_dai = "不分（不属于上述选项的）"
        use_mo = get_use_mo(datasorted)
    elif info == 3:
        use_dai = get_use_dai(product_name, datasorted, package)
        use_mo = get_use_mo(datasorted)

    jiahou = get_jiahou(datasorted)
    package_plus = get_packagePlus(datasorted)
    length = get_lenth(datasorted, package_flag, info)

    result_dict['info1'] = type
    result_dict['info2'] = package_plus
    result_dict['info3'] = length
    result_dict['info4'] = package_type
    result_dict['info5'] = use_dai
    result_dict['info6'] = use_mo
    result_dict['info7'] = jiahou
    result_dict['info8'] = package
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 8
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
        result_dict = category_rule_492(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)