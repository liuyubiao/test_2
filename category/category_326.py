import os
import re

from util import *
from glob import glob
# from utilCapacity import get_capacity


LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/326_brand_list",encoding="utf-8").readlines())]
function_list = [i.strip() for i in set(open("Labels/326_function_list",encoding="utf-8").readlines())]
function_list.sort(key=len,reverse=True)
type_list = [i.strip() for i in set(open("Labels/326_type_list",encoding="utf-8").readlines())]
suffix_name_list = [i.strip() for i in open("Labels/326_suffix_name_list",encoding="utf-8").readlines()]
type_english_list = [i.strip() for i in open("Labels/326_type_english_list",encoding="utf-8").readlines()]

#取出所有品牌，目的是为了刷选品牌用
def get_brand_list_test(texts_list):
    brand_1_list = []
    brand_2 = []
    for texts in texts_list:
        text_str = "".join(texts)
        text_str_ori = ",".join(texts)
        for bb in Brand_list_1:
            if bb in text_str :
                if len(bb) > 2 and len(re.compile("[\u4e00-\u9fa5]").findall(bb)) > 0:
                    brand_1_list.append(bb)
                elif len(re.compile("(,|^)%s($|,)"%(",".join(list(bb)))).findall(text_str_ori)) > 0:
                    brand_1_list.append(bb)

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
        count = Counter(brand_1_list).most_common(6)
        brand_1 = ",".join([i[0] for i in count])
    return brand_1,brand_2

#提取商品全称
def get_productName_voting(texts_list):
    result_list = []
    abort_list = ['打开']
    pre_result_list = []
    pattern_1 = "("
    for i in suffix_name_list:
        pattern_1 += "\w+" + i + "|"

    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1.replace("+", "*")[:-1]


    for texts in texts_list:
        for text in texts:
            flag = True
            for it in abort_list:
                if it in text:
                    flag = False
                    break
            if flag:
                p_res = get_info_by_pattern(text, pattern_1)
                if len(p_res) > 0 and '的' not in p_res[0]:
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
                if len(p_res) > 0 and '的' not in p_res[0]:
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

# 提取功能信息
def get_function(product_name,texts_list):
    '''
    提取功能信息
    提取依据：326定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    :param product_name: 商品全称
    :param texts_list: 有序文本列表
    '''
    list1 = []
    for it in function_list:
        if it in product_name:
            if it not in list1:
                if len(list1) == 1:
                    if it in list1[0]:
                        continue
                    elif list1[0] in it:
                        list1[0] = it
                    else:
                        if product_name.find(it) < product_name.find(list1[0]):
                            list1[0] = it
                        else:
                            list1.append(it)
                else:
                    list1.append(it)
            if len(list1) == 2:
                return '，'.join(list1)
    if len(list1)>0:
        return list1[0]
    for texts in texts_list:
        txt_orgi = ''.join(texts)
        list1 = []
        for it in function_list:
            if it in txt_orgi:
                if it not in list1:
                    if len(list1)==1:
                        if it in list1[0]:
                            continue
                        elif list1[0] in it:
                            list1[0] = it
                        else:
                            if txt_orgi.find(it)<txt_orgi.find(list1[0]):
                                list1[0] = it
                            else:
                                list1.append(it)
                    else:
                        list1.append(it)
                if len(list1) == 2:
                    return '，'.join(list1)
        if len(list1)>0:
            return '，'.join(list1)
    return '不分'

# 提取系列
def get_SubBrand(texts_list):
    '''
    提取系列
    提取依据：326定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：包含类似XX系列
    :param texts_list:有序文本列表
    :return:
    '''
    pattern = '\w+系列'
    abort_list = ['使用','请','配合']
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                flag = True
                for it in abort_list:
                    if it in text:
                        flag = False
                        break
                if flag:
                    return p_res[0]
    return '不分'

#提取适用人群
def get_suitpeople(texts_list):
    '''
    提取适用人群
    提取依据：326定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：注意包装特色对特殊人群的辨别，像儿童、男士、孕产妇、婴幼儿
    :param texts_list: 有序文本列表
    :return:
    '''
    # 适合婴幼儿和准妈妈

    pattern0 ='(儿童|男士|孕产妇|婴幼儿|孕妇|婴儿|婴童|宝宝|成人|baby|BABY)'
    pattern = '适用人群' + pattern0
    pattern1 = '适合\w*' + pattern0
    pattern2 = r'专为' + pattern0 + '研制配方'
    pattern3 = "男士"
    for texts in texts_list:
        text_origi = ''.join(texts)
        p_res = get_info_by_pattern(text_origi, pattern)
        if len(p_res) > 0:
            result = p_res[0]
            if result == '婴儿' or result == '婴童' or result == 'BABY' or result == 'baby':
                return '婴幼儿'
            elif result == '宝宝':
                return '儿童'
            return result
        else:
            p_res = get_info_by_pattern(text_origi, pattern1)
            if len(p_res) > 0:
                result = p_res[0]
                if result == '婴儿' or result == '婴童' or result == 'BABY' or result == 'baby':
                    return '婴幼儿'
                elif result == '宝宝':
                    return '儿童'
                return result
            else:
                p_res = get_info_by_pattern(text_origi, pattern2)
                if len(p_res) > 0:
                    result = p_res[0]
                    if result == '婴儿' or result == '婴童' or result == 'BABY' or result == 'baby':
                        return '婴幼儿'
                    elif result == '宝宝':
                        return '儿童'
                    return result
                else:
                    p_res = get_info_by_pattern(text_origi, pattern3)
                    if len(p_res) > 0:
                        return p_res[0]
    return '不分'

# 提取状态
def get_status(product_name,type):
    '''
    提取状态
    提取依据：326定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    :param product_name: 商品全称
    :param type:类型
    :return:
    '''

    # pattern1 ='\w+(油$|洁面乳|洁面奶|清洁乳|洗面奶|泥|粒|粉|泡泡|泡沫|慕斯|膏|去角质)'
    pattern2= '\w+水$|\w+卸妆液'

    if product_name.endswith('油'):
        return '油状'
    elif '洁面乳' in product_name or '洁面奶' in product_name or '清洁乳' in product_name or '洗面奶' in product_name:
        return '乳液状'
    elif '慕斯' in product_name:
        return '露状，摩丝状'
    elif '啫喱' in product_name or '去角质' in product_name:
        return '啫喱状'
    elif '泥' in product_name:
        return '泥状'
    elif '粒' in product_name:
        return '粒状'
    elif '膏' in product_name or type in ['清洁霜','洁面霜','洁肤霜']:
        return '膏状'
    elif '粉' in product_name:
        return '粉状'
    elif '泡泡' in product_name or '泡沫' in product_name:
        return '露状，泡沫'

    p_res = get_info_by_pattern(product_name, pattern2)
    if len(p_res) > 0:
        return '水状'

    return '片状'


#提取适用时间
def get_applicable_time(texts_list):
    '''
    提取适用时间
    提取依据：326定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：早晚/日间/晚间
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern ='早晚|日间|晚间|日常|早脱|晚安'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result = p_res[0]
                if result=='日常':
                    return '日间'
                elif result=='早脱' and '洁面' in text:
                    return '早晚'
                elif '晚安' in result:
                    return '晚间'
                return result
    return '不分'

# 提取适用部位
def get_applicable_parts(product_name,texts_list):
    '''
    提取适用部位
    提取依据：326定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：肌肤/脸部/脸部、颈部/面部、身体/身体/手部/眼部/其它
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern = '\w+(手|眼|身体|鼻)'

    p_res = get_info_by_pattern(product_name, pattern)
    if len(p_res) > 0:
        result = p_res[0]
        if '手' in result:
            return '手部'
        elif '眼' in result:
            return '眼部'
        elif '身体' in result:
            return '身体'
        elif '鼻' in result:
            return '鼻部'

    return '面部'

# 提取类型
def get_type(product_name,texts_list):
    '''
    提取依据：326定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    :param product_name: 商品全称
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern_1 = "("
    for i in type_list:
        pattern_1 += i + "|"
    pattern_1 = pattern_1[:-1] + ")"

    flag = '免洗式'
    pattern2='清水洗净即可|清洗即可|清洗干净即可|清水\w*洗净|洗净即可|温水冲洗|温水洗干净|清水冲净即可'
    # pattern3='无须冲洗|免洗过夜|无需洗去'

    p_res = get_info_by_pattern(product_name, pattern_1)
    if len(p_res) > 0:
        result  =p_res[0]
        if '慕斯' in result:
            if '去角质' in result:
                result = '去角质慕斯'
            else:
                result = '洁面慕斯'
        elif '眼膜' in result:
            result='贴敷式眼膜'
        elif '鼻' in result:
            result = '贴敷式鼻膜'
        return result

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res)>0:
                result = p_res[0]
                if '慕斯' in result:
                    if '去角质' in result:
                        result = '去角质慕斯'
                    else:
                        result = '洁面慕斯'
                elif '眼膜' in result:
                    result = '贴敷式眼膜'
                elif '鼻' in result:
                    result = '贴敷式鼻膜'
                return result
            else:
                p_res = get_info_by_pattern(text, pattern2)
                if len(p_res) > 0:
                    flag = '水洗式'


    if flag =='水洗式' or '泥膜' in product_name:
        return '水洗式面膜'
    return '贴敷式面膜'

#提取容重量
def get_Capacity(kvs_list,texts_list):
    pattern = r'(净含量|净重|NETWT|重量)'
    pattern1 = r'(\d+\.?\d*)\W*(ml|毫升|克|g|mL|L|kg|ML)'
    pattern4 = '(\d+)(g|G|ml|mL|ML|Ml|毫升)/?[对片杯条包袋]?[Xx*]?(\d+)[对片杯条包袋p]?'
    capacity2 = '不分'
    capacity1 = '不分'
    pian ='片'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    kvalue = kv[k]
                    p_res = re.compile(pattern1).findall(kvalue)
                    if len(p_res) > 0:
                        if '对' in kvalue:
                            pian = '对'
                        elif '包' in kvalue:
                            pian = '包'
                        elif '条' in kvalue:
                            pian = '条'
                        elif '个' in kvalue:
                            pian = '个'
                        elif '杯' in kvalue:
                            pian = '杯'
                        elif '袋' in kvalue:
                            pian = '袋'
                        p_res1 = re.compile(pattern4).findall(kvalue)
                        if len(p_res1)>0:
                            p_res1 = p_res1[0]
                            if len(p_res1[2])>0 and len(p_res1[2])<3 and p_res1[2]!='0':
                                capacity2 = p_res1[2]
                        p_res = p_res[0]
                        result = p_res[0] + p_res[1]

                        if capacity2 != '不分':
                            capacity1  = str(int(float(p_res[0])*int(capacity2)))+ p_res[1] + '/'+capacity2 + pian
                            capacity2 = result + '*' + capacity2 + pian
                        else:
                            capacity1 = result
                        return capacity1,capacity2

    pattern = r'(规格)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    p_res = re.compile(pattern1).findall(kv[k])
                    if len(p_res) > 0:
                        if '对' in kv[k]:
                            pian = '对'
                        elif '包' in kv[k]:
                            pian = '包'
                        elif '条' in kv[k]:
                            pian = '条'
                        elif '个' in kv[k]:
                            pian = '个'
                        elif '杯' in kv[k]:
                            pian = '杯'
                        elif '袋' in kv[k]:
                            pian = '袋'
                        p_res1 = re.compile(pattern4).findall(kv[k])
                        if len(p_res1) > 0:
                            p_res1 = p_res1[0]
                            if len(p_res1[2]) > 0 and len(p_res1[2])<3 and p_res1[2]!='0':
                                capacity2 = p_res1[2]
                        p_res = p_res[0]
                        result = p_res[0] + p_res[1]
                        if capacity2 != '不分':
                            capacity1 = str(int(float(p_res[0]) * int(capacity2))) + p_res[1] + '/' + capacity2 + '片'
                            capacity2 = result + '*' + capacity2
                        else:
                            capacity1 = result
                        return capacity1,capacity2

    pattern = r'(净含量|净重|NETWT|重量|规格)'
    pattern3 = '\d+g?G?m?M?l?L?毫?升?/?[对片杯条包袋]?[Xx*]?\d+(对|片|杯|条|包|袋|p)?'
    for texts in texts_list:
        text_orig = ''.join(texts)
        text_orig=text_orig.replace('包装','')
        p_res = re.compile(pattern).findall(text_orig)
        if len(p_res) > 0:
            p_res = re.compile(pattern1).findall(text_orig)
            if len(p_res) > 0:
                p_res1 = re.compile(pattern3).findall(text_orig)
                if len(p_res1) > 0:
                    if '对' in p_res1[0]:
                        pian = '对'
                    elif '包' in p_res1[0]:
                        pian = '包'
                    elif '条' in p_res1[0]:
                        pian = '条'
                    elif '个' in p_res1[0]:
                        pian = '个'
                    elif '杯' in p_res1[0]:
                        pian = '杯'
                    elif '袋' in p_res1[0]:
                        pian = '袋'
                    elif 'p' in p_res1[0]:
                        pian = '片'

                p_res1 = re.compile(pattern4).findall(text_orig)
                if len(p_res1) > 0:
                    p_res1 = p_res1[0]
                    if len(p_res1[2]) > 0 and len(p_res1[2])<3 and p_res1[2]!='0':
                        capacity2 = p_res1[2]
                p_res = p_res[0]
                result = p_res[0] + p_res[1]

                if capacity2 != '不分':
                    capacity1 = str(int(float(p_res[0]) * int(capacity2))) + p_res[1] + '/' + capacity2 + pian
                    capacity2 = result + '*' + capacity2 + pian
                else:
                    capacity1 = result
                    capacity2 = result + '*1片'
                return capacity1, capacity2
        else:
            pattern = r'\d+pieces|\d+片'
            p_res = get_info_by_pattern(text_orig, pattern)
            if len(p_res) > 0:
                result = p_res[0]
                result = result.replace('pieces', '片')
                return result, '*' + result


    return "不分",'不分'

def get_Capacity_2(texts_list):
    pattern = r'\d+\.?\d*\D*[l升L]\D{0,3}\d+\D*[瓶支包]装?\)?'
    pattern_2 = r'(\d+\.?\d*)\W*(毫升|克|g|ml|mL|ML)\D{0,3}(\d+)\D*[瓶支包]装?\)?'
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
                            if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), p_res_2[1])), re.sub(u"\)", "",
                                                                                                        p_res[0])
                            else:
                                return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[l升L][*xX]\d+[瓶支包\)]?$'
    pattern_2 = r'(\d+\.?\d*)\W*(毫升|克|g|ml|mL|ML)[*xX](\d+)[瓶支包\)]?'
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
                            if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), p_res_2[1])), re.sub(u"\)", "",
                                                                                                        p_res[0])
                            else:
                                return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[l升L][*xX]\d+[瓶支包\)]?'
    pattern_2 = r'(\d+\.?\d*)\W*(毫升|克|g|ml|mL|ML)[*xX](\d+)[瓶支包\)]?'
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
                            if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), p_res_2[1])), re.sub(u"\)", "",
                                                                                                        p_res[0])
                            else:
                                return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    return "不分", "不分"

# 提取片数
def get_pieces(capcity_1,capcity_2):
    '''
    提取片数
    提取依据：326定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：根据容重量字段提取
    :param capcity_1: 重容量
    :param capcity_2: 重容量*数量
    :return:
    '''
    # 6克*10包

    weight = '不分'
    pieces = '不分'
    if capcity_2!='不分':
        capcity_2 = re.sub("ml|mL|Ml|ML", "毫升", capcity_2)
        capcity_2 = re.sub("g|G", "克", capcity_2)
        # 对片杯条包袋
        pattern = '\*(\d+[片包对条个])'
        pattern1 = '\d+(毫升|克)\*\d+(片|包|条|对|个)'

        p_res = get_info_by_pattern(capcity_2, pattern)
        if len(p_res) > 0:
            pieces = p_res[0]
            p_res = get_info_by_pattern(capcity_2, pattern1)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(p_res[0]) > 0 and len(p_res[1]) > 0:
                    weight = p_res[0] + '/' + p_res[1]
    elif capcity_1!='不分':
        capcity_1 = re.sub("g|G", "克", capcity_1)
        capcity_1 = re.sub("ml|mL|Ml|ML", "毫升", capcity_1)
        pattern2 = '\d+(毫升|克)'
        p_res = get_info_by_pattern(capcity_1, pattern2)
        if len(p_res) > 0:
            weight = p_res[0]
    return pieces,weight

# 提取膜类使用方式
def get_usage(type):
    '''
    提取膜类使用方式
    提取依据：326定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：根据类型字段提取
    :param type:
    :return:
    '''
    pattern ='免洗式|水洗式|贴敷式|撕拉型'
    p_res = get_info_by_pattern(type, pattern)
    if len(p_res) > 0:
        return p_res[0]
    return '不分'

# 提取英文全称
def get_englis_Full_Name(texts_list):
    '''
    英文全称
    提取思路：
    :param texts_list: 有序文本列表
    '''

    pattern = "([A-Z-\s]+)"
    # 关键词列表
    list_key = ['SKIOOEYRHANDWAXA', 'CLEANSER', 'ESSENCE', 'FOAMING', 'REMOVER', 'MASQUE', 'LOTION', 'POWDER', 'MOUSSE', 'CREAM', 'MILK', 'MASK', 'BALM', 'SOAP', 'FOAM', 'GEL', 'OIL']
    result_list =[]
    for text_list in texts_list:
        txt_orig = ' '.join(text_list).upper().strip()
        if len(txt_orig)>10:
            # 1、首先把英文字符串分离出来
            p_res = get_info_by_pattern(txt_orig, pattern)
            if len(p_res) > 0:
                for title in p_res:
                    # 2、排除长度小于10英文串
                    if len(title) > 10:
                        words_list = []
                        words = title
                        flag = False
                        for it in list_key:
                            if it in words:
                                flag = True
                                break
                        if flag:
                            # 3、把在英文字符串中出现的单词按照先后顺序存储在列表中，最后用空格链接起来就是英文全称
                            if len(type_english_list)>0:
                                for it in type_english_list:
                                    if it in words:
                                        words = words.replace(it, '*')
                                        if len(words_list) == 0:
                                            words_list.append(it)
                                        else:
                                            flag = True
                                            # 根据单词的先后顺序存在列表中
                                            for index, tt in enumerate(words_list):
                                                if title.find(it) < title.find(tt):
                                                    words_list.insert(index, it)
                                                    flag = False
                                                    break
                                            if flag:
                                                words_list.append(it)
                                        temp = words.replace('*', '')
                                        # 如果都找到并且替换完了，结束循环
                                        if len(temp) == 0:
                                            break
                            else:
                                words_list.append(title)
                            if len(words_list)>0:
                                result = ' '.join(words_list)
                                result_list.append(result)
    if len(result_list)>0:
        result_list.sort(key=len, reverse=True)
        return result_list[0]
    return '不分'


def category_rule_326(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    pieces='不分'
    SubBrand = '不分'
    function = '不分'
    #适用人群
    suitpeople = '不分'
    usage ='不分'
    applicable_parts = '面部'
    status = '不分'
    type = '不分'
    full_name = '不分'
    applicable_time = '不分'
    weight ='不分'

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], [], [])
        brand_1 = re.sub("花润坊", "花涧坊", brand_1)
        brand_1 = re.sub("^ClorisLand$", "花皙蔻ClorisLand", brand_1,re.IGNORECASE)
        brand_1 = re.sub("^SPRINGYL$", "诗珀樱SPRINGYL", brand_1, re.IGNORECASE)
        brand_1 = re.sub("^MERBLISS$", "茉贝丽思MERBLISS", brand_1, re.IGNORECASE)
        brand_1 = re.sub("^WETHERM$", "温碧泉WETHERM", brand_1, re.IGNORECASE)
        brand_1 = re.sub("^JOOCYEE$", "酵色JOOCYEE", brand_1, re.IGNORECASE)
        brand_1 = re.sub("^OSUFI$", "欧束菲OSUFI", brand_1, re.IGNORECASE)
        brand_1 = re.sub("^COGI$", "高姿COGI", brand_1, re.IGNORECASE)
        brand_1 = re.sub("^BOTANICAL$", "佩优棘BOTANICAL", brand_1, re.IGNORECASE)
    #
    # # product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)
    #
    if product_name != '不分' and brand_1 != '不分' and brand_1.title() in product_name.title():
        product_name = product_name.title().replace(brand_1.title(), '')

    capcity_1,capcity_2 = get_Capacity(dataprocessed,datasorted)
    if capcity_1 == '不分':
        capcity_1_bak, capcity_2 = get_Capacity_2(datasorted)
        if capcity_1_bak != "不分" and capcity_1_bak[0] != "0":
            capcity_1 = capcity_1_bak
    full_name = get_englis_Full_Name(datasorted)
    pieces,weight = get_pieces(capcity_1,capcity_2)
    SubBrand = get_SubBrand(datasorted)
    function = get_function(product_name,datasorted)
    suitpeople = get_suitpeople(datasorted)
    applicable_time = get_applicable_time(datasorted)
    applicable_parts = get_applicable_parts(product_name,datasorted)
    type = get_type(product_name,datasorted)
    status = get_status(product_name,type)
    usage = get_usage(type)
    # 片数
    result_dict['info1'] = pieces
    # 系列
    result_dict['info2'] = SubBrand
    # 功能
    result_dict['info3'] = function
    # 适用人群
    result_dict['info4'] = suitpeople
    # 类型
    result_dict['info5'] = type
    # 适用部位
    result_dict['info6'] = applicable_parts
    # 状态
    result_dict['info7'] = status
    # 英文全称
    result_dict['info8'] = full_name
    # 适用时间
    result_dict['info9'] = applicable_time
    # 膜类使用方式
    result_dict['info10'] = usage
    # 重量单位
    result_dict['info11'] = weight

    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])
    real_use_num = 11
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\325-包装饮用水'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3124131"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_325(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)