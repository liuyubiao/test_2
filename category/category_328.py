
import os
import re

from util import *
from glob import glob
import itertools


'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,包装形式,类型,包装类型,配料
'''
Brand_list_1 = [i.strip() for i in set(open("Labels/328_brand_list",encoding="utf-8").readlines())]
suffix_name_list = [i.strip() for i in open("Labels/328_suffix_name_list",encoding="utf-8").readlines()]

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

# 提取分类信息
def get_type(texts_list,product_name,capcity_1):
    '''
    提取分类信息
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    相关信息：共有卷筒有芯厨房纸巾、可携带小包面巾纸、盒装抽取式面巾纸、卷筒无芯厨房纸巾、袋装抽取式面巾纸
                平板式厨房纸巾、卷筒无芯卫生纸、抽取式厨房纸巾、卷筒有芯卫生纸、平板式卫生纸、抽取式卫生纸、平板式纸巾、餐巾纸等
              生活用纸定义
                1、卷纸
                    1.1、厨房用：卷筒有芯厨房纸巾、卷筒无芯厨房纸巾
                    1.2、生活用：卷筒有芯卫生纸、卷筒无芯卫生纸
                2、抽纸
                    2.1、面巾纸：盒装抽取式面巾纸、袋装抽取式面巾纸、可携带小包面巾纸、平板式纸巾
                    2.2、厨房纸：平板式厨房纸巾、抽取式厨房纸巾
                    2.3、餐巾纸：餐巾纸
                    2.4、卫生纸：平板式卫生纸、抽取式卫生纸、卷筒无芯卫生纸、卷筒有芯卫生纸
    提取步骤：
            1、根据测试数据了解，袋装抽取式面巾纸 和 卷筒无芯卫生纸比较多
            2、首先确定是卷纸还是抽纸
            3、其次确定是面巾纸还是厨房纸
            4、再次确定是有芯还是无芯，默认是无芯
            5、再次确定是袋装还是盒装，默认是袋装
            6、不分、平板式纸巾、餐巾纸等没有明显特征，暂时无法判断
    :param texts_list :有序文本列表
    :param product_name: 商品全称
    :param capcity_1: 容重量
    :return:
    '''
    # type_1 = ["卷纸","抽纸"]
    # type_2 = ["生活","面巾","厨房"]
    # type_3 = ["有芯","无芯"]
    type_1 = ""
    type_2 = ""
    type_3 = ""
    type_4 = ''
    type_5 = ''
    #确定卷纸、抽纸
    if "卷" in capcity_1 or "卷纸" in product_name:
        type_1 = "卷纸"
    elif "抽" in capcity_1 or "抽" in product_name :
        type_1 = "抽纸"

    # 确定面巾纸、厨房纸
    if "面巾纸" in product_name or "面纸" in product_name or '面巾' in product_name or product_name.endswith('纸巾纸') or product_name.endswith('纸巾'):
        type_2 = "面巾"
    elif "厨房" in product_name:
        type_2 = "厨房"
    # 确定无芯、有芯
    if '无芯' in product_name:
        type_3 = "无芯"
    elif '有芯' in product_name:
        type_3 = "有芯"

    if  '卫生纸' in product_name:
        type_5 = '卫生纸'

    # 确定卷纸/抽纸、面巾纸/厨房纸、无芯/有芯、袋装/盒装
    for text_list in texts_list:
        for text in text_list:
            if len(type_1) == 0:
                if '卷' in text or "卷纸" in text:
                    type_1 = "卷纸"
                elif "抽" in capcity_1 or "抽" in text:
                    type_1 = "抽纸"
            if len(type_2) == 0:
                if "面巾纸" in text or "面纸" in product_name or '面巾' in text or text.endswith('纸巾纸') or text.endswith('纸巾'):
                    type_2 = "面巾"
                elif "厨房" in text:
                    type_2 = "厨房"
            if len(type_3) == 0:
                if '无芯' in text:
                    type_3 = "无芯"
                elif '有芯' in text or '空芯' in text:
                    type_3 = "有芯"
            if len(type_4) == 0:
                if len(re.compile("盒装|[\/每]盒").findall(text)) > 0:
                    type_4 = '盒装'
                elif len(re.compile("袋装|[\/每]袋").findall(text)) > 0:
                    type_4 = '袋装'
            if len(type_5) == 0 or '卫生纸' in text:
                type_5 = '卫生纸'


    if len(type_3) == 0:
        type_3 = '无芯'
    if len(type_4) == 0:
        type_4 = '袋装'

    #判断纸的类型
    if type_1 == '抽纸':
        if type_2 == '面巾':
            if type_4 == '袋装':
                return '袋装抽取式面巾纸'
            elif type_4 == '盒装':
                return '盒装抽取式面巾纸'
        elif type_2 == '厨房':
            return '抽取式厨房纸巾'
        else:
            return '抽取式卫生纸'
    elif type_1 == '卷纸':
        if type_2 == "厨房":
            if type_3 == "有芯":
                return "卷筒有芯厨房纸巾"
            else:
                return "卷筒无芯厨房纸巾"
        else:
            if type_3 == "有芯":
                return "卷筒有芯卫生纸"
            else:
                return "卷筒无芯卫生纸"
    else:
        if len(type_5)>0:
            return '卷筒无芯卫生纸'

    return '不分'


def get_productName_voting_bak(kvs_list,texts_list):
    pattern_text = "[、，,]"
    pattern_pres = "的|避免|加热|[揭撕][开取]|放入|\d+[个只张条]"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w{2,}卫生纸|\w{2,}面巾纸?|\w{2,}[面抽柔卷]纸|\w+纸巾|\w{2,}保湿纸|\w{2,}纸抽)($|\()"
    pattern_2 = "(卫生纸|保湿纸)($|\()"
    pattern_3 = "(\w+纸)($|\()"

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
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0]:
        return count[1][0]
    return count[0][0]

def TextFormat(texts_list):
    full_text = []
    for texts in texts_list:
        tmp_str = ""
        l = len(texts)
        for index, txt in enumerate(texts):
            if len(txt) > 2 or index > 8:
                split_flag = "&"
                if tmp_str != "" and tmp_str[-1] != "&":
                    tmp_str += "&"
            else:
                split_flag = ""
                if "酒" in txt:
                    if tmp_str != "" and tmp_str[-1] == "&":
                        tmp_str = tmp_str[:-1]
            tmp_str += txt
            if index != l - 1:
                tmp_str += split_flag
        full_text.append(tmp_str.split("&"))
    return full_text

def get_brand_list_test(texts_list):
    brand_1_list = []
    brand_2 = []
    for texts in texts_list:
        for text in texts:
            for b1 in Brand_list_1:
                if b1.upper() in text.upper() or b1 in text:
                    brand_1_list.append(b1)

    if len(brand_2) > 0:
        brand_2 = ",".join(list(set(brand_2)))
    else:
        brand_2 = "不分"

    if len(brand_1_list) == 0:
        brand_1 = "不分"
    else:
        brand_1_list.sort(key=len,reverse=True)
        count = Counter(brand_1_list).most_common(12)
        brand_1 = ",".join([i[0] for i in count])
    return brand_1,brand_2

def get_capacity_keyword(kvs_list,unit="[g克抽卷]"):
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

    pattern = r'^\(?(\d{2,3})\)$'
    p = re.compile(pattern)
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0 and float(p_res[0]) < limit_top and float(p_res[0][0]) > limit_floor:
                if "加量" in text:
                    continue
                result_list.append(p_res[0] + unit_default)

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if count[0][1] > 1:
            return count[0][0],True

    return "不分",True

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

def get_Capacity_mul_bak(texts_list,unit_1 = "[个只克条]|[Pp][Cc][Ss]",unit_2 = "[卷包]",limit_top=2000):
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

#提取重容量*数量
def get_Capacity_mul(texts_list,unit_1 = "[个只克条]|[Pp][Cc][Ss]",unit_2 = "[卷包]",limit_top=2000):
    capacity_1 = "不分"
    capacity_2 = "不分"
    res_list = []
    total_weight = 0
    total_weight1 = 0
    packege_count = 0
    # pattern_1 = r'(\d+)\W*(%s)(\D{0,3})(\d+)\D?(%s)装?\)?'%(unit_1,unit_2)
    pattern_1 = r'(\d+)\W*(%s)(\D{0,3})(\d+)\D?(%s)装?\)?' % (unit_1, unit_2)
    pattern_2 = r'总重量:(\d+\.?\d?)千克|总重量:(\d+)克'
    pattern_3 = r'(\d+\.?\d?)千克|(\d+)克'
    pattern_4 = r'(\d+)包/提'
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
                        return ("%d%s" % (int(p_res[0]) * int(p_res[3]), unit)),pre_text , [],total_weight,packege_count
                    else:
                        return ("%d%s" % (int(p_res[0]) * int(p_res[3]), unit)),pre_text, [p_res[0] + unit],total_weight,packege_count
            else:
                p_res = get_info_by_pattern(text, pattern_2)
                if len(p_res) > 0 and total_weight == 0:
                    p_res = p_res[0]
                    if len(p_res[0]) > 0:
                        total_weight = int(float(p_res[0]) * 1000)
                    elif len(p_res[1]) > 0:
                        total_weight = int(p_res[1])
                else:
                    p_res = get_info_by_pattern(text, pattern_3)
                    if len(p_res) > 0 and total_weight1 == 0:
                        p_res = p_res[0]
                        if len(p_res[0]) > 0:
                            total_weight1 = int(float(p_res[0]) * 1000)
                        elif len(p_res[1]) > 0:
                            total_weight1 = int(p_res[1])
                    else:
                        p_res = get_info_by_pattern(text, pattern_4)
                        if len(p_res) > 0 and packege_count == 0:
                            packege_count = int(p_res[0])
    if total_weight==0 and total_weight1>0:
        total_weight = total_weight1
    if total_weight>100000 or total_weight<50:
        total_weight = 0
    return capacity_1,capacity_2,res_list,total_weight,packege_count

def get_packagePlus(texts_list):
    pattern = "加量|补充装"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                return "有补充装"
    return "不分"

def get_bense(texts_list):
    pattern = "本[色布]"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "本色"
    return "不分"

#提取层数
def get_cengshu(product_name,texts_list):
    '''
    提取纸巾层数
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：1层、2层、3层、4层、5层、6层等。如产品包装上无层数注明，则按如下规则人为判断层数，
    分为几类：1、卷筒有芯卫生纸、卷筒无芯卫生纸、可携带小包面巾纸默认3层
              2、袋装抽取式面巾纸、盒装抽取式面巾纸、餐巾纸、抽取式卫生纸默认2层
              3、平板式纸巾、平板式卫生纸、平板式厨房纸巾、卷筒有芯厨房纸巾、卷筒无芯厨房纸巾、抽取式厨房纸巾默认1层

    :param texts_list:有序文本
    :return:
    '''
    abort_list = ['地址']
    pattern = "(^|\D)([123456二三四五六]层)"
    pattern1 = "(\d+)张/抽"
    result_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                flag = False
                for it in abort_list:
                    if it in text:
                        flag = True
                        break
                if flag:
                    continue
                p_res = p_res[0]
                result_list.append(p_res[1])
            else:
                p_res = get_info_by_pattern(text, pattern1)
                if len(p_res) > 0:
                    result_list.append(p_res[0]+'层')
    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        res = count[0][0]
        res = re.sub("二","2",res)
        res = re.sub("三","3",res)
        res = re.sub("四", "4", res)
        res = re.sub("五", "5", res)
        res = re.sub("六", "6", res)
        return res

    pattern2 = '抽取式面巾纸|抽取式卫生纸|餐巾纸|抽纸|抽取式生活用纸|抽式|抽取'
    # pattern3 = '卷筒有芯卫生纸|卷筒无芯卫生纸|小包面巾纸|无芯卷筒卫生纸|有芯卷筒卫生纸'
    p_res = get_info_by_pattern(product_name, pattern2)
    if len(p_res) > 0:
        return '2层'

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern2)
            if len(p_res) > 0:
                return '2层'

    # return "---2层"
    return "3层"

# 提取每卷克重
def get_capacity_unit(capacity_mul):
    res = "不分"
    pattern = "\d+\.?\d*[gG克]"
    p_res = get_info_by_pattern(capacity_mul,pattern)

    if len(p_res) > 0:
        res = p_res[0]

    return res

def get_package_type_bak(texts_list,capacity_mul):
    pattern = "(\d+)[抽]"
    p_res = get_info_by_pattern(capacity_mul,pattern)
    if len(p_res) > 0:
        if float(p_res[0]) < 15:
            for texts in texts_list:
                for text in texts:
                    if "迷你" in text:
                        return "迷你型"
            return "普通型"
    return "不分"

#提取可携带小包纸巾类型
def get_package_type(product_name,texts_list,length):
    '''
    提取可携带小包纸巾类型
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：共有迷你型、普通型、荷包装、超迷你型等四种
              1、迷你型尺寸标准为5.5cm*7.5cm
              2、普通型尺寸标准为5.5cm*10.5cm
              3、荷包装手帕纸外形类似于钱包状，可左右或上下打开。
              4、超迷你型根据产品包装上或全称里含有“超迷你”的字样归类
    :param product_name:商品名称全称
    :param texts_list:有序文本列表
    :param capacity_mul:
    :return:
    '''
    type1 = '超迷你'
    if type1 in product_name:
        return type1
    if length!='不分' and '*' in length:
        len1 = length.split('*')[1]
        if 'CM' in len1:
            l = float(len1.replace('CM',''))*10
        elif 'MM' in len1:
            l = float(len1.replace('MM',''))
        if l==75:
            return '迷你型'
        elif l==105:
            return '普通型'
    for texts in texts_list:
        for text in texts:
            if type1 in text:
                return type1
    return '不分'

def lenth_filter(lenth_str):
    pattern = "\d+\.?\d*"
    p_res = get_info_by_pattern(lenth_str,pattern)
    if len(p_res) >= 2:
        if float(p_res[0]) < 10 or float(p_res[0]) > 1000:
            return False
        if float(p_res[1]) < 10 or float(p_res[1]) > 1000:
            return False

    return True

def get_lenth_fun(texts_list):
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

def get_lenth_bak(texts_list):
    pattern_1 = "(\d+)(厘米|CM|cm|MM|mm)[xX*]?[宽长]?(\d+)(厘米|CM|cm|MM|mm)"
    pattern_2 = "(^|\()\D?([1234]\d)[宽长]?([1234]\d)(厘米|CM|cm|MM|mm)"
    pattern_3 = "([1]\d)(厘米|CM|cm|MM|mm)[xX*]?([1]\d)$"
    pattern_4 = "([1]\d)(厘米|CM|cm|MM|mm)[xX*]?([1]\d)(厘米|CM|cm|MM|mm)"
    result = "不分"
    result_2 = "不分"
    result_list = []
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

    if result_2 != "不分" and result != "不分":
        return result + "*" + result_2,[]

    return result,res_list

def get_length_bak(texts_list):
    res,_ = get_lenth_fun(texts_list)
    if res == "不分":
        res,_ = get_lenth_bak(texts_list)
    return res

#提取尺寸信息
def get_length(texts_list,type):
    '''
    提取尺寸信息
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    相关信息：
        1、这里的尺寸只针对盒装抽取式面巾纸和袋装抽取式面巾纸和卷筒无芯卫生纸，其它类型不用判断，都给成“不分”，即使包装上面有尺寸描述也不需要注明
        2、单位统一为mm，如果原包装为MM、CM则换算过来进行统一。
    :param texts_list:
    :return:
    '''
    if type in ['盒装抽取式面巾纸','袋装抽取式面巾纸','卷筒无芯卫生纸','抽取式卫生纸']:
        res, _ = get_lenth_fun(texts_list)
        if res == "不分":
            res, _ = get_lenth_bak(texts_list)
        return res
    else:
        return '不分'

def get_series(texts_list,brand_1):
    if "清风" in brand_1:
        res = get_info_list_by_list_taste(texts_list,["新韧时代","超质感","绿茶","原木","原木金装","2次方","Joy","Mini","缤纷心情","粉红嘟嘟","风车","花语心室","花韵","绿花","绿叶","马蹄莲","欧院清香","伊甸幽香","紫罗兰","卡通"])
        if len(res) > 0:
            return "清风" + res[0]
    elif "维达" in brand_1:
        res = get_info_list_by_list_taste(texts_list,["超韧","倍韧","蓝色经典","至有分量","柔滑","绵柔","花之韵","威","feel","雅致","东京猫","满天星","旺佳","逸彩","格调","旺宝","果园飘香","健康家庭","浪漫心曲","喜羊羊与灰太狼"])
        if len(res) > 0:
            return "维达" + res[0]
    elif "心相印" in brand_1:
        res = get_info_list_by_list_taste(texts_list,["品诺","优选","冬已","茶语","薰衣草","红悦","特柔","柔肤"])
        if len(res) > 0:
            return "心相印" + res[0]
    elif "洁柔" in brand_1:
        res = get_info_list_by_list_taste(texts_list, ["Face", "Lotion", "C&S", "青春校园","布艺"])
        if len(res) > 0:
            return "洁柔" + res[0]
    elif "洁云" in brand_1:
        res = get_info_list_by_list_taste(texts_list, ["丝柔", "雅致生活", "原茶清香","卡通"])
        if len(res) > 0:
            return "洁云" + res[0]

    return "不分"


#提取产品代码
def get_product_code(kvs_list,texts_list):
    '''
    提取产品代码
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：开放细分：BL－C009，HCDZ175等。
              注意：是产品代码，不是执行标准、不是产品标准、不是卫生标准。
                产品包装上标注“产品代码”、“产品编号”或“货号”字样，由英文、数字、标点符合组成。
                产品编号（代码）的位置一般在条码旁边。注意最新要求，产品编号（代码）不要放在全称中。（15年5月的全称里放“产品代码”的内容已经作废）

    :param kvs_list:文本键值对
    :param texts_list:有序文本列表
    :return:
    '''
    abort_list = ['邮政','许可证','产品执行','股权','企业代码']
    result_list = []
    result_list1 = []
    pattern1 = '产品代码|产品编号|产品编码|货号|QualityInspectionNo|产品代母|SKU'
    pattern2 = '代码|编号|编码|型号'
    pattern3='[a-zA-Z.\-\d]{3,}'
    pattern4= '(产品代码|产品编号|产品编码|货号|QualityInspectionNo|产品代母|SKU|型号)(:?[a-zA-Z.\-\d]{4,})'
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                flag = True
                for it in abort_list:
                    if it in k:
                        flag = False
                        break
                if flag:
                    p_res = get_info_by_pattern(k, pattern1)
                    if len(p_res)>0:
                        p_res = get_info_by_pattern(kv[k], pattern3)
                        if len(p_res) > 0:
                            if "GB" not in p_res[0] and 'GB' not in kv[k]:
                                result_list.append(p_res[0])
                    else:
                        p_res = get_info_by_pattern(k, pattern2)
                        if len(p_res)>0:
                            p_res = get_info_by_pattern(kv[k], pattern3)
                            if len(p_res) > 0:
                                if "GB" not in p_res[0] and 'GB' not in kv[k] and '产品执行' not in kv[k]:
                                    result_list1.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]
    elif len(result_list1) > 0:
        count = Counter(result_list1).most_common(2)
        return count[0][0]
    for texts in texts_list:
        txt_join = ''.join(texts)
        p_res = get_info_by_pattern(txt_join, pattern4)
        if len(p_res) > 0:
            p_res = p_res[0]
            if len(p_res[0]) > 0 and len(p_res[1]) > 0:
                if p_res[1].startswith(':'):
                    return p_res[1][1:]
                else:
                    return p_res[1]

    return "不分"

# 提取颜色信息
def get_color(texts_list):
    '''
    提取颜色信息
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    相关信息：1、包装上的信息，凡是品牌、系列、全称、背面原料或者包装任何地方出现的例如：本色、原色、理文原色、竹浆本色、竹本、竹纤维原浆本色、低白度、本色竹浆的即判断为本色纸
              2、凡是包装上出现例如：竹纤维原浆不漂白，原生木浆不漂白、原麦纤维、秸秆这类关键词需要拍摄清楚包装上的关键词，由DICC进行判断。
              3、某些固定品牌，例如：心相印竹π、清风原色纸系列、洁柔自然木系列、洁云AIRPLUS系列、顺清柔共享本色系列、理文、斑布、泉林本色、韶能本色都为本色纸，由DICC统一加规则无需抄录人为判断。
    :param texts_list:有序文本列表
    :return:
    '''
    pattern = "原色|本色|理文原色|竹本|低白度"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                return "本色"

    return "不分"


#提取单多包装对应条码
def get_barcode(texts_list):
    '''
    提取单多包装对应条码
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern = "(^|\D)(\d{13})($|\D)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                p_res = p_res[0]
                return p_res[1]

    return "不分"

# 提取添加物
def get_inside(texts_list):
    '''
    提取添加物
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    相关信息：抄录包装上出现“添加保湿因子、乳霜”等添加成分。
    :param texts_list: 有序文本列表
    :return:
    '''
    res = get_info_list_by_list(texts_list,["保湿因子","乳霜"])
    if len(res) > 0:
        return "，".join(res)
    return "不分"

#提取压花工艺
def get_yahua(texts_list):
    '''
    提取压花工艺
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    相关信息：
        1、压花、压纹、压边、立体、纹理、印花、图案等…../不分
        2、根据整体包装文字出现“压花”、“压纹”、“压边”、“立体”、“纹理”、“印花”、“图案”等压花有关工艺描述按包装抄录
        3、不限以上举例，若没有工艺描述给不分
    :param texts_list: 有序文本列表
    :return:
    '''
    result_list = []
    pattern = "\w{2,}压花|\w{2,}压纹|\w{2,}压边|\w{2,}纹理|\w{2,}印花"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return "不分"

#提取环保概念
def get_huanbao(texts_list):
    '''
    提取环保概念
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    相关信息：
        1、“可冲”、“可降解”、“速溶”、“即溶”、“可溶”、 “免垃圾分类”、“冲散”、“环保”……/不分
        2、根据整体包装文字出现“可冲”、“可降解”、“速溶”、“即溶”、“可溶”、 “免垃圾分类”、“冲散”、“环保”等新的环保概念或新环保原料的关键字按包装抄录，
        3、不限以上举例若没有给不分。
        4、注意区分“不易溶解”、“不易冲散”等容易混淆的不可冲描述，给不分。
    :param texts_list: 有序文本列表
    :return:
    '''
    # lst = ["可降解","速溶","免垃圾分类"]
    lst = ["可冲", "可降解", "速溶","即溶","可溶","免垃圾分类","冲散","环保"]
    res = get_info_list_by_list(texts_list,lst)

    if len(res) > 0:
        return "，".join(res)
    return "不分"

#提取商品全称
def get_productName_voting(texts_list):
    pattern_pres = "的|^用"
    result_list = []
    abort_list = ['感谢','公司']
    pre_result_list = []
    pattern_1 = "("
    for i in suffix_name_list:
        pattern_1 += "\w+" + i + "|"

    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1.replace("+", "*")[:-1]
    pattern_3='\w+纸'

    for texts in texts_list:
        for text in texts:
            flag = True
            for it in abort_list:
                if it in text:
                    flag = False
                    break
            if flag:
                p_res = get_info_by_pattern(text, pattern_1)
                if len(p_res) > 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 :
                    result_list.append(p_res[0])
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        if len(pre_result_list) > 0:
            return pre_result_list[0]
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            flag = True
            for it in abort_list:
                if it in text:
                    flag = False
                    break

            if flag:
                p_res = get_info_by_pattern(text, pattern_2)
                if len(p_res) > 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 :
                    result_list.append(p_res[0])
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        if len(pre_result_list) > 0:
            return pre_result_list[0]
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            flag = True
            for it in abort_list:
                if it in text:
                    flag = False
                    break

            if flag:
                p_res = get_info_by_pattern(text, pattern_3)
                if len(p_res) > 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        if len(pre_result_list) > 0:
            return pre_result_list[0]
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return '不分'

#重容量
def get_capacity(texts_list,cengnum,unit="[抽卷]"):
    '''
    提取重容量
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：一般为抽卷，卷一般有明显的数据，比如28卷，抽是根据张数换算出来的：抽 =张数/层 数或（张数*包数）/层数
    :param texts_list:
    :param unit:
    :return:
    '''
    pattern ='\d+[抽卷]'
    pattern1 = r'(\d+)包/提\D*(\d+)抽/包'
    pattern2 = r'(\d+)张.*(\d+)包'
    pattern6 = r'(\d+)包\D*(\d+)张'
    pattern5 = r'(\d+)系列\D*(\d+)包'
    pattern3 = r'(\d+)张'
    pattern4 = r'(\d+)包'
    # 300系列10包

    result_list = []
    for texts in texts_list:
        txt_join = ''.join(texts)
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                num = int(p_res[0].replace('抽','').replace('卷',''))
                #过大，肯定是识别错误
                if '抽' in text and num > 8000:
                    continue
                if '卷' in text and num>100:
                    # num = str(int(num / 10) + num % 10) + '卷'
                    # result_list.append(num)
                    continue
                result_list.append(p_res[0])
            p_res = get_info_by_pattern(text, pattern1)
            if len(p_res) > 0 and p_res[0][1]!='0':
                bagnum, unit = int(p_res[0][0]), int(p_res[0][1])
                result = str(bagnum * unit) + '抽'
                result_list.append(result)
            p_res = get_info_by_pattern(text, pattern2)
            if len(p_res) > 0 and p_res[0][1]!='0':
                bagnum, unit = int(p_res[0][0]), int(p_res[0][1])
                #抽 = （张数*包数）/层数
                result = str(int((bagnum * unit)/cengnum)) + '抽'
                result_list.append(result)
            p_res = get_info_by_pattern(text, pattern6)
            if len(p_res) > 0 and p_res[0][1] != '0':
                bagnum = int(p_res[0][1])
                if '包/提' in txt_join:
                    unit = int(p_res[0][0])
                    bagnum = bagnum * unit
                result = str(int(bagnum / cengnum)) + '抽'
                result_list.append(result)
            p_res = get_info_by_pattern(txt_join, pattern5)
            if len(p_res) > 0 and p_res[0][1] != '0':
                bagnum, unit = int(p_res[0][0]), int(p_res[0][1])
                result = str(int((bagnum * unit) / cengnum)) + '抽'
                result_list.append(result)
        p_res = get_info_by_pattern(txt_join, pattern)
        if len(p_res) > 0:
            num = int(p_res[0].replace('抽', '').replace('卷', ''))
            # 过大，肯定是识别错误
            if '抽' in txt_join and num > 8000:
                continue
            if '卷' in txt_join and num > 100:
                if num>=1000:
                    num = str(num % 100) + '卷'
                else:
                    num = str(int(num/10)+ num %10)+'卷'
                result_list.append(num)
                continue
            if p_res[0] not in result_list:
                result_list.append(p_res[0])
        p_res = get_info_by_pattern(txt_join, pattern1)
        if len(p_res) > 0 and p_res[0][1]!='0':
            bagnum, unit = int(p_res[0][0]), int(p_res[0][1])
            result = str(bagnum * unit) + '抽'
            if result not in result_list:
                result_list.append(result)
        p_res = get_info_by_pattern(txt_join, pattern2)
        if len(p_res) > 0 and p_res[0][1]!='0':
            bagnum, unit = int(p_res[0][0]), int(p_res[0][1])
            result = str(int((bagnum * unit) / cengnum)) + '抽'
            if result not in result_list:
                result_list.append(result)
        p_res = get_info_by_pattern(txt_join, pattern6)
        if len(p_res) > 0 and p_res[0][1] != '0':
            bagnum= int(p_res[0][1])

            if '包/提' in txt_join and bagnum<1000:
                unit = int(p_res[0][0])
                bagnum = bagnum*unit
            result = str(int(bagnum/cengnum)) + '抽'
            if result not in result_list:
                result_list.append(result)
        else:
            p_res = get_info_by_pattern(txt_join, pattern5)
            if len(p_res) > 0 and p_res[0][1] != '0':
                bagnum, unit = int(p_res[0][0]), int(p_res[0][1])
                result = str(int((bagnum * unit) / cengnum)) + '抽'
                if result not in result_list:
                    result_list.append(result)
            else:
                p_res = get_info_by_pattern(txt_join, pattern3)
                if len(p_res) > 0 :
                    p_res1 = get_info_by_pattern(txt_join, pattern4)
                    p_res1.sort(key=len, reverse=True)
                    pagenum = 0
                    if len(p_res1) > 0:
                        pagenum = int(p_res1[0])
                    else:
                        p_res1 = get_info_by_pattern(txt_join, pattern5)
                        if len(p_res1) > 0:
                            pagenum = int(p_res1[0])
                    if pagenum>1000:
                        continue
                    unit = int(p_res[0])
                    if unit>1000:
                        continue
                    if pagenum > 0:
                        unit = unit * pagenum
                    result = str(int((unit) / cengnum)) + '抽'
                    result_list.append(result)

    if len(result_list)>0:
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return "不分"

#提取香型
def get_taste(kvs_list,texts_list):
    '''
    提取香型
    提取依据：328定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：香型封闭为有香和无香，不再区分具体香型内容了。
    :param texts_list:
    :return:
    '''
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if k=='香型':
                    if '有香' in kv[k]:
                        return '有香'
                    elif '无香' in kv[k]:
                        return '无香'
    pattern = r'香型(有香|无香)'
    for texts in texts_list:
        txt_join = ''.join(texts)
        p_res = get_info_by_pattern(txt_join, pattern)
        if len(p_res) > 0:
            return p_res[0]

    return '无香'

def category_rule_328(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"


    ceng = "不分"
    capcity_unit = "不分"
    type = "不分"
    package_type = "不分"
    taste = "无香"
    length = "不分"
    series = "不分"
    product_code = "不分"
    color = "不分"
    bar_code = "不分"
    additives =''
    inside = "不分"
    yahua = "不分"
    huanbao = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["新生","BPS","UEH","依柔","欢喜","珍爱","清风","欢关","Scala","ISDG","ZKH"], [])
    #     # brand_1_test, brand_2_test = get_brand_list_test(datasorted)


    brand_1 = re.sub("班布","斑布",brand_1)
    brand_1 = re.sub("蓝源", "蓝漂", brand_1)
    brand_1 = re.sub("欢关", "欢笑", brand_1)

    # datasorted = TextFormat(datasorted)
    # product_name = get_productName_voting(dataprocessed,datasorted)
    product_name = get_productName_voting(datasorted)
    product_name = re.sub("^\w*名称", "", product_name)
    product_name = re.sub("工生", "卫生", product_name)
    product_name = re.sub("牌", "", product_name)
    product_name = re.sub("级", "纸", product_name)
    product_name = re.sub("^\w*品名", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)
    if product_name != '不分' and brand_1 != '不分' and brand_1.title() in product_name.title():
        product_name = product_name.title().replace(brand_1.title(), '')


    ceng = get_cengshu(product_name,datasorted)
    # capcity_1 = get_capacity_keyword(dataprocessed,unit="[g克抽卷]")
    # 层数
    cengnum = int(ceng.replace('层',''))
    capcity_1 = get_capacity(datasorted,cengnum,unit="[抽卷]")
    capcity_flag = False
    # if capcity_1 == "不分":
    #     capcity_1, capcity_flag = get_Capacity_texts(datasorted, unit="[g克抽卷]")

    # 乘法重容量
    capcity_1_mul, capcity_2_mul, flag_list_mul, total_weight,packege_count = get_Capacity_mul(datasorted, unit_1="[g克抽卷]")
    if capcity_1 == "不分" or capcity_1 in flag_list_mul:
        capcity_1 = capcity_1_mul
        capcity_2 = capcity_2_mul
    if capcity_2 == '不分' and capcity_1 != '不分':
        pattern = '\d+'
        p_res = get_info_by_pattern(capcity_1, pattern)
        if len(p_res) > 0:
            amount = int(p_res[0])
            if amount > 0:
                if total_weight > 0:
                    amount = int(round(total_weight / amount))
                    if amount > 20:
                        capcity_2 = str(amount) + '克*' + capcity_1
                elif packege_count > 0:
                    capcity_2 = str(int(round(amount / packege_count))) + '抽*' + str(packege_count) + '包'
    capcity_2 = re.sub("/包", "*", capcity_2)
    # 分类
    type = get_type(datasorted,product_name,capcity_1)
    # 每卷克重
    capcity_unit = get_capacity_unit(capcity_2)
    taste = get_taste(dataprocessed,datasorted)
    length = get_length(datasorted,type)
    package_type = get_package_type(product_name,datasorted,length)
    series = get_series(datasorted,brand_1)
    product_code = get_product_code(dataprocessed,datasorted)
    color = get_color(datasorted)
    bar_code = get_barcode(datasorted)
    inside = get_inside(datasorted)
    yahua = get_yahua(datasorted)
    huanbao = get_huanbao(datasorted)

    # 层数
    result_dict['info1'] = ceng
    # 每卷克重
    result_dict['info2'] = capcity_unit
    # 分类
    result_dict['info3'] = type
    # 可携带小包纸巾类型
    result_dict['info4'] = package_type
    # 香型
    result_dict['info5'] = taste
    # 尺寸
    result_dict['info6'] = length
    # 系列
    result_dict['info7'] = series
    # 产品编码/货号/SKU码/产品编号
    result_dict['info8'] = product_code
    # 颜色
    result_dict['info9'] = color
    # 单多包装对应条码
    result_dict['info10'] = bar_code
    # 添加物/添加成分
    result_dict['info11'] = inside
    # 压花工艺
    result_dict['info12'] = yahua
    # 环保
    result_dict['info13'] = huanbao
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    # result_dict['info14'] = brand_1_test

    real_use_num = 13
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Tools\KWPOTools\KWPO数据获取\格式化数据\328'
    # root_path = r'C:\Users\zhangxuan\Desktop\00001'
    for product in os.listdir(root_path):
        image_list = []
        # product = "4713220"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_328(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)