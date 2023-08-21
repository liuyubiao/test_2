import os
import re

from util import *
from glob import glob
import itertools


'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,包装形式,类型,包装类型,配料
'''

Brand_list_1 = [i.strip() for i in set(open("Labels/429_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/429_brand_list_2",encoding="utf-8").readlines())]
Net_list = [i.strip() for i in set(open("Labels/429_net_list",encoding="utf-8").readlines())]
Thickness_list = [i.strip() for i in set(open("Labels/429_thickness_list",encoding="utf-8").readlines())]
Usage_list = [i.strip() for i in set(open("Labels/429_usage_list",encoding="utf-8").readlines())]

Chaca_list_ori = [i.strip() for i in open("Labels/429_chaca_list",encoding="utf-8").readlines()]
Chaca_list = []
for line in Chaca_list_ori:
    Chaca_list.extend(re.split("[^\-0-9a-zA-Z\u4e00-\u9fa5\+]",line))
Chaca_list = set(Chaca_list)
Chaca_list.remove("")
Chaca_list = list(Chaca_list)
Chaca_list.sort(key=len,reverse=True)

# 通常来看需要20个非通用属性
LIMIT_NUM = 20


class BigWordUtil():
    def __init__(self):
        self.pattern = "的|^[开将]|[撕搬]开|\d+[Mm]+|^[中厚]+型"

    def isNear(self,box,bbox):
        box_x_min = min([x[0] for x in box])

        box_x_max = max([x[0] for x in box])
        box_y_min = min([x[1] for x in box])
        box_y_max = max([x[1] for x in box])

        near_x = 1000
        near_y = 1000
        # for bbox in box_list:
        bbox_x_min = min([x[0] for x in bbox])
        bbox_x_max = max([x[0] for x in bbox])
        bbox_y_min = min([x[1] for x in bbox])
        bbox_y_max = max([x[1] for x in bbox])

        if box_x_max < bbox_x_min or box_x_min > bbox_x_max:
            tmp_x = min(abs(box_x_max - bbox_x_min), abs(box_x_min - bbox_x_max))
        else:
            tmp_x = 0
        if box_y_max < bbox_y_min or box_y_min > bbox_y_max:
            tmp_y = min(abs(box_y_max - bbox_y_min), abs(box_y_min - bbox_y_max))
        else:
            tmp_y = 0

        if tmp_x < near_x:
            near_x = tmp_x
        if tmp_y < near_y:
            near_y = tmp_y

        return near_x + near_y

    def process(self,dataoriginals):
        result_list = []
        max_size = 0
        min_size = 10000
        top_list = []
        bottom_list = []
        max_size_list = []
        min_size_list = []
        max_size_box_list = []
        for dataoriginal in dataoriginals:
            top = 10000
            bottom = 0
            tmp_max_size = 0
            tmp_min_size = 1000
            tmp_box = []
            for index, info in enumerate(dataoriginal):
                box = info["box"]
                size = min(abs(box[0][1] - box[3][1]), abs(box[0][0] - box[1][0]))
                dataoriginal[index]["size"] = size
                if size > max_size:
                    max_size = size
                if size < min_size:
                    min_size = size
                if box[0][1] < top:
                    top = box[0][1]
                if box[0][1] > bottom:
                    bottom = box[0][1]
                if size > tmp_max_size:
                    tmp_max_size = size
                    tmp_box = box
                if size < tmp_min_size:
                    tmp_min_size = size

            top_list.append(top)
            bottom_list.append(bottom)
            max_size_list.append(tmp_max_size)
            min_size_list.append(tmp_min_size)
            max_size_box_list.append(tmp_box)

        for index, dataoriginal in enumerate(dataoriginals):
            top = top_list[index]
            bottom = bottom_list[index]
            m_size = max_size_list[index]
            mm_size = min_size_list[index]
            m_box = max_size_box_list[index]

            height = bottom - top
            if float(m_size / mm_size) > 2.5 and m_size > 80:
                result_txt = []
                for info in dataoriginal:
                    if info["size"] > m_size * 0.7 or (info["size"] > m_size * 0.6 and self.isNear(info["box"], m_box) < info["size"] / 3):
                        if len(re.compile("[a-zA-Z0-9]+$|\W").findall(info["txt"])) == 0 and len(re.compile(self.pattern).findall(info["txt"])) == 0:
                            result_txt.append([info["txt"], info["box"][2][1] + info["box"][0][0]])
                result_txt = sorted(result_txt, key=lambda x: x[1])
                result_txt = [x[0] for x in result_txt]

                res_tmp = []
                if len(result_txt) > 0:
                    for i in result_txt:
                        flag = True
                        for j in result_txt:
                            if i == j:
                                continue
                            if i in j:
                                flag = False
                        if flag:
                            res_tmp.append(i)
                    result_list.append("".join(res_tmp))

        result_list = sorted(result_list, key=len)
        res = []
        if len(result_list) > 0:
            for index, i in enumerate(result_list):
                flag = True
                for j in result_list[index + 1:]:
                    if i in j:
                        flag = False
                if flag:
                    res.append(i)
        res = sorted(result_list, key=len, reverse=True)
        if len(res) == 0:
            return "不分"
        count = Counter(res).most_common(2)
        return count[0][0]

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
    pattern_text = "[、，,]|公司|有限|^卫生护垫$"
    pattern_pres = "[的勿]|^[用开将请]|[撕搬]开|\d+[Mm]+|^[中厚]+型|贴于|内含"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w{2,}卫生[巾裤中]|\w{2,}迷你[巾中]|安[心睡]裤|\w+组合装|\w+[日夜]用装)($|\()"
    pattern_2 = "(\w+护理?垫)($|\()"
    pattern_3 = "\w*卫生[巾裤]"
    pattern_4 = "\w+护理?垫|\w+裤$|\w*医用垫巾$"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("[巾裤装]").findall(kv[k])) > 0:
                        result_list.append(kv[k])
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

    product_name_pre = get_productName_pre(texts_list)
    if product_name_pre != "不分":
        return product_name_pre

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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0]:
        return count[1][0]
    return count[0][0]

def get_productName_pre(texts_list):
    key_list_1 =["超瞬吸","炫吸芯","弹力中凸","魔力瞬吸","超熟睡360","氧气七日","空气棉","灰姑娘三重奏","自由主义","零感·棉","红豆杉复合芯片","舒适V感"]
    key_list_2 = ["日夜组合","旅行装","护翼","棉柔日用","日用","夜用","加长夜用"]
    res_1 = []
    res_2 = []

    for texts in texts_list:
        for text in texts:
            if text in key_list_1 and text not in res_1:
                res_1.append(text)
            if text in key_list_2 and text not in res_2:
                res_2.append(text)
    if len(res_1) > 0:
        return "".join(res_1) + "".join(res_2) + "卫生巾"

    return "不分"

def get_Capacity_1(texts_list):
    unit = "[片条]|[pP][cC][sS]|[Pp]ads"
    unit_default = "片"
    pattern_text = "内含|加量|(%s)\w+(%s)"%(unit_default,unit_default)
    num_limit = 60
    allnum = {'一': "1", '二': "2", '三': "3", '四': "4", '五': "5", '六': "6", '七': "7", '八': "8", '九': "9", '零': "0"}
    pattern_1 = r'(\d+)\s?(%s)$' %(unit)
    pattern_2 = r'(\d+)\s?(%s)' % (unit)
    pattern_25 = r'([一二三四五六七八九十])(%s)装'%unit
    pattern_3 = r'^(\d{1,2})$'
    pattern_4 = r'([\u4e00-\u9fa5]|[cMmC][Mm])[*xX](\d{1,2})($|\D)'
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text,pattern_1)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(p_res[0] + "\s?片[^片]*护垫").findall(text)) > 0:
                    continue
                if int(p_res[0]) > num_limit or p_res[0][0] == "0":
                    continue
                if len(re.compile(pattern_text).findall(text)) == 0:
                    tmp_list.append(p_res[0] + p_res[1])

        if len(tmp_list) == 1:
            return tmp_list[0],False

    result_num_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern_1)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(p_res[0] + "\s?片[^片]*护垫").findall(text)) > 0:
                    continue
                if int(p_res[0]) > num_limit or p_res[0][0] == "0":
                    continue
                if len(re.compile(pattern_text).findall(text)) == 0:
                    result_num_list.append(p_res[0] + p_res[1])

    if len(result_num_list) > 0:
        count = Counter(result_num_list).most_common(2)
        return count[0][0],False

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern_2)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(p_res[0] + "\s?片[^片]*护垫").findall(text)) > 0:
                    continue
                if int(p_res[0]) > num_limit or p_res[0][0] == "0":
                    continue
                if len(re.compile(pattern_text).findall(text)) == 0:
                    result_num_list.append(p_res[0] + p_res[1])

    if len(result_num_list) > 0:
        count = Counter(result_num_list).most_common(2)
        return count[0][0],False

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern_25)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0:
                    result_num_list.append(allnum[p_res[0]] + p_res[1])

    if len(result_num_list) > 0:
        count = Counter(result_num_list).most_common(2)
        return count[0][0]

    result_num_list_1 = []
    result_num_list_2 = []
    for texts in texts_list:
        total_len = len(texts)
        for index, text in enumerate(texts):
            p_res = get_info_by_pattern(text,pattern_3)
            if len(p_res) > 0:
                if int(p_res[0]) > num_limit or p_res[0][0] == "0":
                    continue
                if len(re.compile(pattern_text).findall(text)) == 0:
                    for i in [-2, -1, 0, 1, 2]:
                        if index + i >= 0 and index + i < total_len:
                            p_res_tmp = re.compile("^%s$"%(unit)).findall(texts[index + i])
                            if len(p_res_tmp) > 0:
                                result_num_list_1.append(p_res[0] + p_res_tmp[0])
                    result_num_list_2.append(p_res[0] + unit_default)

    if len(result_num_list_2) > 0:
        count = Counter(result_num_list_2).most_common(2)
        return count[0][0],False

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[1]) > num_limit or p_res[1][0] == "0":
                    continue
                if len(re.compile(pattern_text).findall(text)) == 0:
                    result_num_list.append(p_res[1] + unit_default)

    if len(result_num_list) > 0:
        count = Counter(result_num_list).most_common(2)
        return count[0][0],False

    if len(result_num_list_1) > 0:
        count = Counter(result_num_list_1).most_common(2)
        return count[0][0],True

    return "不分",True

def get_Capacity_2_plus(texts_list):
    unit = "片"
    unit_default = "片"
    pattern_text = "护垫|内含|加量|%s[/\\][包]"%(unit)
    num_limit = 300
    pattern_1 = r'(\d+)\s?%s'%(unit)
    pattern_2 = "(\d{1,2})%s/?[装包]?[*xX]?(\d)[包]"%(unit)
    result_num_list = []

    capacity_1 = "不分"
    capacity_2 = "不分"
    res_list = []
    for texts in texts_list:
        tmp_list_1 = []
        tmp_list_2 = []
        for index, text in enumerate(texts):
            p_res = get_info_by_pattern(text,pattern_2)
            if len(p_res) > 0:
                for p_r in p_res:
                    num_tmp = int(p_r[0]) * int(p_r[1])
                    if num_tmp < num_limit and num_tmp not in tmp_list_2:
                        tmp_list_2.append(num_tmp)

            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0:
                    for p_r in p_res:
                        if int(p_r) < num_limit:
                            result_num_list.append(int(p_r))
                            if int(p_r) not in tmp_list_1 and int(p_r) not in tmp_list_2:
                                tmp_list_1.append(int(p_r))

        if len(tmp_list_2) <= 2:
            result_num_list.extend(tmp_list_2)

        if len(tmp_list_2) == 2 and len(tmp_list_2) > len(res_list):
            capacity_1 = str(sum(tmp_list_2)) + "片"
            res_list = [str(i) + "片" for i in tmp_list_2]
            capacity_2 = "+".join(res_list)
        elif len(tmp_list_1) == 2 and len(tmp_list_1) > len(res_list):
            capacity_1 = str(sum(tmp_list_1)) + "片"
            res_list = [str(i)+"片" for i in tmp_list_1]
            capacity_2 = "+".join(res_list)

    result_num_list = sorted(set(result_num_list), key=result_num_list.index)
    result_num_list_uniq = result_num_list.copy()
    result_num_list_uniq.sort()
    l = len(result_num_list_uniq)

    if l < 2:
        return capacity_1,capacity_2,res_list

    if l > 3:
        for i in range(3, l):
            for j, k ,v in itertools.combinations(result_num_list_uniq[:i],3):
                if j + k + v == result_num_list_uniq[i]:
                    j, k, v = sorted([j,k,v],reverse=True)
                    return str(result_num_list_uniq[i]) + "片", "%d片+%d片+%d片" % (j, k, v),None

    if l > 2:
        for i in range(2, l):
            for j, k in itertools.combinations(result_num_list_uniq[:i],2):
                if j + k == result_num_list_uniq[i]:
                    j, k = sorted([j,k],reverse=True)
                    return str(result_num_list_uniq[i]) + "片", "%d片+%d片" % (j, k),None

    for i in range(1,l):
        for j in range(i):
            if j*2 == result_num_list_uniq[i]:
                return str(result_num_list_uniq[i]) + "片" , "%d片+%d片" %(j,j),None

    if l > 2:
        capacity_1 = str(result_num_list_uniq[-1]) + "片"
        res_list = [str(i) + "片" for i in result_num_list_uniq]
        capacity_2 = "不分"
    return capacity_1,capacity_2,res_list

def get_Capacity_2_mul(texts_list):
    unit = "片"
    unit_default = "片"
    num_limit = 300
    pattern_1 = "(\d{1,2})%s/?[装包]?[*xX]?(\d{1,2})[包]"%(unit)
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                for p_r in p_res:
                    num_tmp = int(p_r[0]) * int(p_r[1])
                    if num_tmp < num_limit:
                        return str(num_tmp) + unit_default,p_r[0] + unit_default + "*" + p_r[1] ,[p_r[0] + unit_default,]

    return "不分","不分",[]

def get_net(texts_list):
    res = get_info_list_by_list(texts_list, Net_list)
    if len(res) == 0:
        return "不分"
    return "".join(res)

def get_shape(product_name):
    if "裤" in product_name:
        return "裤型"
    return "护翼"

def get_dayornight(texts_list):
    pattern_0 = "日夜两用|日/?夜用|日夜组合|[加特]长夜用"
    pattern_1 = "日用"
    pattern_2 = "夜用"
    pattern_3 = "迷你卫生巾|迷你巾"
    result_1 = []
    result_2 = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern_0)
            if len(p_res) > 0:
                p_res[0] = re.sub("迷你卫生巾","迷你巾",p_res[0])
                return p_res[0]
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern_1)
            if len(p_res) > 0:
                result_1.append(p_res[0])

            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                result_2.append(p_res[0])
    result = []
    if len(result_1) > 0:
        result.append("日用")
    if len(result_2) > 0:
        result.append("夜用")

    if len(result) > 0:
        return "+".join(result)

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern_3)
            if len(p_res) > 0:
                p_res[0] = re.sub("迷你卫生巾","迷你巾",p_res[0])
                return p_res[0]
    return "不分"

def get_thickness(texts_list):
    res = get_info_list_by_list(texts_list,Thickness_list)
    if len(res) == 0:
        return "不分"
    return "+".join(res)

def get_chaca(texts_list):
    res = get_info_list_by_list(texts_list, Chaca_list)
    if len(res) == 0:
        return "不分"
    return "，".join(res)

def get_usage(texts_list):
    res = get_info_list_by_list(texts_list, Usage_list)
    if len(res) == 0:
        return "不分"
    return "，".join(res)

def get_lenth(texts_list):
    pattern = "\d+\.?\d*[Cc厘毫Mm][mM米]"
    res_single = "不分"
    res_list = []
    for texts in texts_list:
        tmp_list = []
        if res_single == "不分":
            for text in texts:
                p_res = get_info_by_pattern(text, pattern)
                if len(p_res) > 0:
                    tmp_list.append(p_res[0])

            if len(tmp_list) == 1:
                res_single = tmp_list[0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                res_list.append(p_res[0])

    if res_single == "不分" and len(res_list) > 0:
        count = Counter(res_list).most_common(2)
        res_single = count[0][0]

    if len(res_list) > 0:
        res_list = sorted(set(res_list), key=res_list.index)

    return res_single,res_list

def format_lenth_unit(length):
    pattern = "(\d+\.?\d*)([Cc厘毫Mm][mM米])"
    p_res = get_info_by_pattern(length,pattern)
    if len(p_res) > 0:
        p_res = p_res[0]
        num = p_res[0]
        unit = p_res[1]
        if len(re.compile("[毫Mm][mM米]").findall(unit)) > 0:
            len_num = float(num)/10.0
            if len_num <10 or len_num > 50:
                return "不分"
            if len_num.is_integer():
                return "%dCM" % (int(len_num))
            else:
                return "%.1fCM"%(len_num)
        else:
            len_num = float(num)
            if len_num < 10 or len_num > 50:
                return "不分"
            return num + "CM"
    else:
        return "不分"

def get_size(kvs_list,texts_list):
    pattern_key_0 = "(NB|M|S|[Xx]*L)\-(NB|M|S|[Xx]*L)"
    pattern_key_1 = "(NB|M|S|[Xx]*L)"
    pattern_0 = "(^|[\u4e00-\u9fa5])(NB|M|S|[Xx]*L)(码|$|\()"
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if "规格" in k:
                    p_res = get_info_by_pattern(kv[k], pattern_key_0)
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        return "%s-%s"%(p_res[0],p_res[1])
                    p_res = get_info_by_pattern(kv[k],pattern_key_1)
                    if len(p_res) > 0:
                        return p_res[0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_0)
            if len(p_res) > 0:
                p_res = p_res[0]
                return p_res[1]

    return "不分"

def get_unit_info(capcity_2,length,dayornight):
    capcity_2_list = capcity_2.split("+")
    length_list = length.split("+")
    capacity_num = len(capcity_2_list)
    length_num = len(length_list)
    res = "不分"
    if "日" in dayornight and "夜" in dayornight:
        if capacity_num == 2:
            if length_num == 2:
                res = "日用，%s，%s+夜用，%s，%s"%(capcity_2_list[0],length_list[0],capcity_2_list[1],length_list[1])
            else:
                res = "日用，%s+夜用，%s" % (capcity_2_list[0], capcity_2_list[1])
    return res

def get_pad_num(texts_list):
    pattern = r'(\d+)\s?片[^片]*护垫'
    result_num_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                result_num_list.append(p_res[0])

    if len(result_num_list) > 0:
        count = Counter(result_num_list).most_common(2)
        return count[0][0] + "片"

    return "无护垫"

def category_rule_429(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    unit_type = "不分"
    pad_num = "不分"
    net = "不分"
    shape = "不分"
    dayornight = "不分"
    thickness = "不分"
    feeling = "不分"
    characteristic = "不分"
    length = "不分"
    usage = "不分"
    unit_info = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,Brand_list_2,["ADC","ADG","Mac","完美","REE","EDO","维度","宜婴","JAYA"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("FREEMORE","自由点FREEMORE",brand_1,re.IGNORECASE)
    brand_1 = re.sub("XIMIVOGUE", "熙美诚品", brand_1,re.IGNORECASE)

    capcity_1,flag = get_Capacity_1(datasorted)
    capcity_1 = re.sub("[pP][cCad]+[sS]","片",capcity_1)
    capcity_1 = re.sub("[日夜]用", "片", capcity_1)
    # 加法重容量
    capcity_1_plus , capcity_2_plus , flag_list_plus = get_Capacity_2_plus(datasorted)
    if capcity_1 != capcity_1_plus :
        if capcity_1_plus != "不分":
            if flag_list_plus is None or flag:
                capcity_1 = capcity_1_plus
                capcity_2 = capcity_2_plus
            else:
                if capcity_1 != "不分" and capcity_1 in flag_list_plus and len(flag_list_plus) < 4:
                    capcity_1 = capcity_1_plus
                    capcity_2 = capcity_2_plus
    else:
        capcity_2 = capcity_2_plus

    # 乘法重容量
    capcity_1_mul ,capcity_2_mul , flag_list_mul = get_Capacity_2_mul(datasorted)
    if capcity_1 == "不分" or capcity_1 in flag_list_mul:
        capcity_1 = capcity_1_mul
        capcity_2 = capcity_2_mul

    # datasorted = TextFormat(datasorted)
    if product_name == "不分":
        product_name = get_productName_voting(dataprocessed,datasorted)
    if product_name == "不分":
        bwOBJ = BigWordUtil()
        bwresult = bwOBJ.process(dataoriginal)
        if bwresult != "不分" and len(bwresult) > 1:
            if "卫生巾" not in bwresult:
                bwresult += "卫生巾"
            product_name = bwresult

    product_name = re.sub("卫生中", "卫生巾", product_name)
    product_name = re.sub("迷你中", "迷你巾", product_name)

    product_name = re.sub("\(\w+$", "", product_name)
    product_name = re.sub("^\w*名称", "", product_name)
    product_name = re.sub("^\w*品名", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    pad_num =get_pad_num(datasorted)
    net = get_net(datasorted)
    shape = get_shape(product_name)
    dayornight = get_dayornight(datasorted)
    if "组合" in product_name or capcity_2 != "不分":
        unit_type = "组合（混合）装"
    else:
        unit_type = "独立装"
    thickness = get_thickness(datasorted)
    characteristic = get_chaca(datasorted)
    length_single,length_list = get_lenth(datasorted)
    usage = get_usage(datasorted)

    length_num = len(capcity_2.split("+"))
    if length_num > 1:
        length_tmp = []
        for i in range(length_num):
            try:
                length_tmp.append(format_lenth_unit(length_list[i]))
            except:
                pass
        length = "+".join(length_tmp)
    else:
        length = format_lenth_unit(length_single)

    if length == "不分":
        length = get_size(dataprocessed,datasorted)

    unit_info = get_unit_info(capcity_2,length,dayornight)

    result_dict['info1'] = unit_type
    result_dict['info2'] = pad_num
    result_dict['info3'] = net
    result_dict['info4'] = shape
    result_dict['info5'] = dayornight
    result_dict['info6'] = thickness
    result_dict['info7'] = feeling
    result_dict['info8'] = characteristic
    result_dict['info9'] = length
    result_dict['info10'] = usage
    result_dict['info11'] = unit_info
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 11
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    pass