import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity
LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/160_brand_list_1",encoding="utf-8").readlines())]
# Brand_list_2 = [i.strip() for i in set(open("Labels/160_brand_list_2",encoding="utf-8").readlines())]
additive_list = [i.strip() for i in set(open("Labels/160_additive_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/160_taste_list",encoding="utf-8").readlines())]
type_list = [i.strip() for i in set(open("Labels/160_type_list",encoding="utf-8").readlines())]
product_type_list = [i.strip() for i in set(open("Labels/160_product_type_list",encoding="utf-8").readlines())]
mixture_list = [i.strip() for i in set(open("Labels/160_mixture_list",encoding="utf-8").readlines())]
suffix_name_list = [i.strip() for i in open("Labels/160_suffix_name_list",encoding="utf-8").readlines()]


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


#调用公告方法提取口味
def get_taste(texts_list,product_name):
    '''
    调用公告方法提取口味
    基本思路是要维护口味列表160_taste_list，根据商品名称全程和口味列表进行匹配提取
    :param texts_list:
    :param product_name:
    :return:
    '''
    pattern = "(\w+味)"
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
                # result.append(p_res[0])
                result.append(p_res[0])

    if len(result) == 0:
        res = get_taste_normal(texts_list, Taste_list)
        res = res.replace('，','')
    else:
        res = "".join(result)

    if res == '香辣' or res=='麻辣' or res=='甜辣':
        res = res + '味'
    else:
        res = res.replace('香辣口味', '香辣味')
        res = res.replace('，', '')
        res = res.replace('地道味', '')
        res = res.replace('招牌风味', '')
        if len(res) == 0:
            res = '不分'

    return res

#提取商品全称
def get_productName_voting(texts_list):
    result_list = []
    abort_list = ['把','含有']
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

#提取系列
def get_SubBrand(texts_list):
    '''
    提取系列
    提取依据：160定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、只抄肉类的描述，按照实际包装配料表抄录；如鸭脖、鸡肉、猪肉、牛板筋等。
    2、如果配料含两种及以上的**肉都要抄全；配料里有含肉量百分比，也要抄一下
    3、配料里的调味料、调味汁等信息不用抄录；如下图抄录“猪软骨”即可
    :param texts_list: 有序文本列表
    '''
    pattern = '\w+系列'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]
    return '不分'

#提取配料
def get_mixture(kvs_list,texts_list):
    '''提取配料
    提取依据：160定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、包装上注有**系列的字样，或除品牌外的大字，没有给“不分”；
    :param kvs_list: 文本键值对
    :param texts_list: 有序文本列表
    :return:
    '''

    pattern = "("
    for i in mixture_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    pattern1='鸡|牛|鸭'

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if k=='配料':
                    p_res = get_info_by_pattern(kv[k], pattern)
                    if len(p_res) > 0:
                        mixture = p_res[0]
                        return mixture

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                mixture = p_res[0]
                return mixture

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern1)
            if len(p_res) > 0:
                return p_res[0]

    return '不分'

#提取产品类型
def get_product_type(product_type,kvs_list,texts_list):
    '''
    提取产品类型
    提取依据：160定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、根据包装背面“产品类型”或全称后(括号)里的内容抄录，没有给不分。
    :param product_type:
    :param kvs_list:文本键值对
    :param texts_list:有序文本列表
    :return:
    '''

    pattern = "("
    for i in product_type_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"

    product_type = re.sub(':', "", product_type)
    if  product_type == '不分' or len(product_type) == 0:
        product_type = get_keyValue(kvs_list, ["产品类别","类别","型", '英别'])
        product_type = re.sub(':', "", product_type)
        if len(product_type)==0 or product_type not in product_type_list:
            for texts in texts_list:
                for text in texts:
                    p_res = get_info_by_pattern(text, pattern)
                    p_res.sort(key=len, reverse=True)
                    if len(p_res) > 0:
                        product_type = p_res[0]
                        product_type = re.sub("尚内", "卤肉", product_type)
                        product_type = re.sub("卤内", "卤肉", product_type)

                        return product_type
            return '不分'
    if '(' in product_type:
        product_type = product_type.split('(')[0]
    if len(product_type)>0:
        product_type = re.sub("各卤", "酱卤", product_type)
        product_type = re.sub("薯卤", "酱卤", product_type)
        product_type = re.sub("客点", "酱卤", product_type)
        product_type = re.sub("尚内", "卤肉", product_type)
        product_type = re.sub("卤内", "卤肉", product_type)
        product_type = re.sub("备离", "畜禽", product_type)
        product_type = re.sub("内制品", "肉制品", product_type)
        product_type = re.sub("人制品", "肉制品", product_type)
        product_type = re.sub("品炎", "品类", product_type)
        return product_type

    return '不分'

# 提取子品类
def get_subcategory(product_name,texts_list):
    '''
    提取子品类
    提取依据：160定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：鸡肉类、鸭肉类、鹅肉类、牛肉类、猪肉类、混合、其它（请注明）
    1、鸡肉类：根据配料表肉类信息判断，产品只属于“鸡的部位”制成的零食；
    2、鸭肉类：根据配料表肉类信息判断，产品只属于“鸭的部位”制成的零食；
    3、牛肉类：根据配料表肉类信息判断，产品只属于“牛的部位”制成的零食；
    4、根据配料表肉类信息判断，产品只属于“鹅的部位”制成的零食；
    5、猪肉类：根据配料表肉类信息判断，产品只属于“猪的部位”制成的零食；
    6、混合：根据配料表肉类信息判断，产品属于两种以上动物部位制成的零食；
    7、根据配料表肉类信息判断，产品不属于以上肉类划分，请注明。
    :param product_name:商品全称
    :param texts_list:有序文本列表
    :return:
    '''
    meat_list = ['鸡','鸭','鹅','牛','猪','鱼','虾','兔']
    for it in meat_list:
        if it in product_name:
            return it+'肉类'
    for texts in texts_list:
        for text in texts:
            for it in meat_list:
                if it in text:
                    return it + '肉类'
    return '不分'

#提取种类
def get_type(product_name,texts_list):
    '''
    提取种类
    提取依据：160定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：爪、掌、锁骨、鸡翅、鸭翅、翅中、翅根、翅尖、板筋、蹄筋、毛肚、肝、肠、皮、舌头、头、屁股等
              注意：优先根据全称信息抄录，全称无法判断的可结合配料表里的肉归属部位信息抄录。
    :param product_name:商品全称
    :param texts_list:有序文本列表
    :return:
    '''
    pattern='肠|头|翅|脚|肝|舌|皮|心|脖|爪|肚|掌'
    pattern_meat= '鸡|鸭|鹅|牛|猪|鱼|虾|兔'
    # type_list
    for it in type_list:
        if it in product_name:
            return it

    for texts in texts_list:
        for text in texts:
            for it in type_list:
                if it in text:
                    return it
    pre =''
    p_res = get_info_by_pattern(product_name, pattern_meat)
    if len(p_res) > 0:
        pre = p_res[0]
    else:
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern_meat)
                if len(p_res) > 0:
                    pre = p_res[0]

    # for it in meat_list:
    #     if it in product_name:
    #         pre = it
    #         break
    # if len(pre) == 0:
    #     for texts in texts_list:
    #         for text in texts:
    #             for it in meat_list:
    #                 if it in text:
    #                     pre = it
    #                     break
    return '不分'

#提取去骨/去皮信息
def get_boning(product_name,texts_list):
    '''
    提取去骨/去皮信息
    提取依据：160定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：去骨/去皮(开放字段)：去骨、去皮、去甲、不分等
              注意：该字段是指产品经过单独去骨、去皮、去甲等工艺处理，不是指产品本身有骨、无骨、有皮、无皮！
              比如： “去骨鸡爪、去皮鸭腿、去甲凤爪”这些产品符合该字段定义，像牛蹄筋、内脏、鸡爪、鸭脖、鸡翅等产品，不用区分本身是否带骨，只要包装上无相关关键字，就给“不分”。
              去骨：产品经过单独去骨工艺处理；全称或包装上含“去骨、脱骨、剔骨、无骨”等字样，多见于鸡爪、凤爪、鸭掌产品。
              去皮：产品经过单独去皮工艺处理；全称或包装上含“去皮、脱皮”等字样，多见于腿类产品。
              去甲：产品经过单独去甲工艺处理；全称或包装上含“去甲、剃甲、剪甲”等字样，多见于爪、掌产品。
              不分：没有经过单独“去骨”、“去甲”、“去皮”处理的产品，包装上无相关关键字，不需要根据包装上的图画进行人为判断。
    :param product_name:商品全称
    :param texts_list:有序文本列表
    :return:
    '''
    result = ''
    pattern1 = '去骨\w+|脱骨\w+|剔骨\w+|无骨\w+|去皮\w+|去甲\w+|剃甲\w+|剪甲\w+'
    p_res = get_info_by_pattern(product_name, pattern1)
    if len(p_res) > 0:
        result =  p_res[0]
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern1)
            if len(p_res) > 0:
                result = p_res[0]
                break
        if len(result)>0:
            break
    if len(result)>0:
        if '骨' in result:
            return '去骨'
        elif '甲' in result:
            return '去甲'
        else:
            return '去皮'

    return '不分'

#提取储藏方式
def get_storage(texts_list):
    '''
    提取储藏方式
    提取依据：160定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：常温、冷藏、常温/冷藏
              常温：类似阴凉、通风、干燥、避光保存
              冷藏：0-10度冷藏(冷冻)保存
              注意：“冷藏风味更佳、冷藏效果更佳”不属于“冷藏”
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern = '冷藏|冷冻'
    pattern1='常温保存|建议冷藏|阴凉干燥处|冷藏更佳|放置阴凉|低温储存更佳|置于用凉干燥处|常温'
    result = ''

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern1)
            if len(p_res) > 0:
                return '常温'
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result = '冷藏'

    if len(result)>0:
        return '冷藏'
    return '常温'

#提取健康概念信息
def get_health_concept(texts_list):
    '''
    提取健康概念信息
    提取依据：160定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：开放字段 ：涉及健康理念的信息，如低脂、零脂、高蛋白、零添加等
              注意抄录包装上的“0脂、低脂、0蔗糖、0油、高蛋白等信息”，可以互相组合
              注意包装有“无添加、零添加”时看下配料，只要有其中一种添加剂的都不给“无添加”
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern='低脂|零脂|高蛋白|零添加|0脂|0蔗糖|零蔗糖|0油|零油|无添加'
    result_list = []
    isadditive = 0
    pattern_1 = "("
    # 食品添加剂列表
    for i in additive_list:
        pattern_1 +=  i + "|"
    pattern_1 = pattern_1[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                p_res = p_res[0]
                if p_res not in result_list:
                    result_list.append(p_res)
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                isadditive = 1
    if isadditive==1:
        if '零添加' in result_list:
            result_list.remove('零添加')
        if '无添加' in result_list:
            result_list.remove('无添加')
    if len(result_list)>0:
        return '、'.join(result_list)
    return '不分'

#提取加工工艺信息
def get_processing_technology_bak(product_name,texts_list):
    '''
    提取加工工艺信息
    提取依据：160定义文档、及人为标注Excel测试数据
    提取思路：封闭字段 ：风干/手撕、熏烤、虎皮/油炸、盐焗、泡制、泡卤、其它（请注明）、酱卤、不分。（优先级按照从上至下，依次降低）
              1、风干/手撕：全称或包装上任何位置注明“风干”、“手撕”、“撕”字样；
              2、熏烤：全称或包装上任何位置注明“熏”、“烤”、“烧烤”字样；
              3、虎皮/油炸：全称或包装上任何位置注明“油炸”、“虎皮”字样；
              4、盐焗：全称或包装上任何位置注明“盐焗”、“盐水”字样；
              5、泡卤：全称或包装上任何位置注明“泡”字样并且配料表含“酱油”成分；
              6、泡制：全称或包装上任何位置注明“泡”字样并且配料表不含“酱油”成分；
              7、酱卤：全称或包装上任何位置注明“酱、卤、煮”字样；
              8、其它（请注明）：全称或包装上任何位置注明“糟制”、“腊”等其它加工工艺字样；
              9、不分：全称或包装上任何位置无相关加工工艺字样。
    :param product_name:商品全称
    :param texts_list: 有序文本列表
    '''
    pattern1='风干|手撕|撕'
    result1 = ''
    pattern2='熏|烧烤|烤'
    result2 = ''
    pattern3 = '油炸|虎皮'
    result3 = ''
    pattern4 = '盐焗|盐水'
    result4 = ''

    pattern5 = '泡'
    result5 = ''
    pattern6 = '酱油'
    result6 = ''
    pattern7 = '酱|卤|煮'
    result7 = ''
    pattern8 = '糟制|腊'
    result8 = ''

    p_res = get_info_by_pattern(product_name, pattern1)
    if len(p_res) > 0:
        # return '风干/手撕'
        return '风干、手撕'
    p_res = get_info_by_pattern(product_name, pattern2)
    if len(p_res) > 0:
        result2 = '熏烤'
    p_res = get_info_by_pattern(product_name, pattern3)
    if len(p_res) > 0:
        # result3 = '虎皮/油炸'
        result3 = '虎皮、油炸'
    p_res = get_info_by_pattern(product_name, pattern4)
    if len(p_res) > 0:
        result4 = '盐焗'
    p_res = get_info_by_pattern(product_name, pattern5)
    if len(p_res) > 0:
        result5 = '泡'
    p_res = get_info_by_pattern(product_name, pattern7)
    if len(p_res) > 0:
        result7 = '酱卤'
    p_res = get_info_by_pattern(product_name, pattern7)
    if len(p_res) > 0:
        result7 = p_res[0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern1)
            if len(p_res) > 0:
                return '风干/手撕'
            else:
                p_res = get_info_by_pattern(product_name, pattern2)
                if len(p_res) > 0:
                    result2 = '熏烤'
                p_res = get_info_by_pattern(product_name, pattern3)
                if len(p_res) > 0:
                    result3 = '虎皮/油炸'
                p_res = get_info_by_pattern(product_name, pattern4)
                if len(p_res) > 0:
                    result4 = '盐焗'
                p_res = get_info_by_pattern(product_name, pattern5)
                if len(p_res) > 0:
                    result5 = '泡'
                p_res = get_info_by_pattern(product_name, pattern6)
                if len(p_res) > 0:
                    result6 = '酱油'
                p_res = get_info_by_pattern(product_name, pattern7)
                if len(p_res) > 0:
                    result7 = '酱卤'
                p_res = get_info_by_pattern(product_name, pattern7)
                if len(p_res) > 0:
                    result8 = p_res[0]

    if len(result2)>0:
        return result2
    if len(result3)>0:
        return result3
    if len(result4)>0:
        return result4
    if len(result5)>0 and len(result6)>0:
        return '泡卤'
    if len(result5)>0 and len(result6)==0:
        return '酱卤'
    if len(result7)>0:
        return result7
    if len(result8)>0:
        return result8
    return '不分'

def get_processing_technology(product_name,product_type,texts_list):
    '''
    提取加工工艺信息
    提取依据：160定义文档、及人为标注Excel测试数据
    提取思路：封闭字段 ：风干/手撕、熏烤、虎皮/油炸、盐焗、泡制、泡卤、其它（请注明）、酱卤、不分。（优先级按照从上至下，依次降低）
              1、风干/手撕：全称或包装上任何位置注明“风干”、“手撕”、“撕”字样；
              2、熏烤：全称或包装上任何位置注明“熏”、“烤”、“烧烤”字样；
              3、虎皮/油炸：全称或包装上任何位置注明“油炸”、“虎皮”字样；
              4、盐焗：全称或包装上任何位置注明“盐焗”、“盐水”字样；
              5、泡卤：全称或包装上任何位置注明“泡”字样并且配料表含“酱油”成分；
              6、泡制：全称或包装上任何位置注明“泡”字样并且配料表不含“酱油”成分；
              7、酱卤：全称或包装上任何位置注明“酱、卤、煮”字样；
              8、其它（请注明）：全称或包装上任何位置注明“糟制”、“腊”等其它加工工艺字样；
              9、不分：全称或包装上任何位置无相关加工工艺字样。
    :param product_name:商品全称
    :param product_type:产品类型
    :param texts_list: 有序文本列表
    '''
    pattern7 = '酱|卤|煮'
    result7 = ''

    pattern1='风干|手撕|撕'
    result1 = ''
    pattern2='熏|烧烤|烤'
    result2 = ''
    pattern3 = '油炸|虎皮'
    result3 = ''
    pattern4 = '盐焗|盐水'
    result4 = ''

    pattern5 = '泡'
    result5 = ''
    pattern6 = '酱油'
    result6 = ''

    pattern8 = '糟制|腊'
    result8 = ''
    p_res = get_info_by_pattern(product_name, pattern7)
    if len(p_res) > 0:
        result7 = '酱卤'
    else:
        p_res = get_info_by_pattern(product_type, pattern7)
        if len(p_res) > 0:
            result7 = '酱卤'
    p_res = get_info_by_pattern(product_name, pattern4)
    if len(p_res) > 0:
        result4 = '盐焗'
    p_res = get_info_by_pattern(product_name, pattern1)
    if len(p_res) > 0:
        result1= '风干/手撕'
        # return '风干、手撕'
    p_res = get_info_by_pattern(product_name, pattern2)
    if len(p_res) > 0:
        result2 = '熏烤'
    p_res = get_info_by_pattern(product_name, pattern3)
    if len(p_res) > 0:
        # result3 = '虎皮/油炸'
        result3 = '虎皮、油炸'

    p_res = get_info_by_pattern(product_name, pattern5)
    if len(p_res) > 0:
        result5 = '泡'
    p_res = get_info_by_pattern(product_name, pattern7)
    if len(p_res) > 0:
        result8 = p_res[0]

    if len(result7)>0:
        return result7

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern1)
            if len(p_res) > 0:
                result1= '风干、手撕'
            p_res = get_info_by_pattern(product_name, pattern2)
            if len(p_res) > 0:
                result2 = '熏烤'
            p_res = get_info_by_pattern(product_name, pattern3)
            if len(p_res) > 0:
                result3 = '虎皮、油炸'
            p_res = get_info_by_pattern(product_name, pattern4)
            if len(p_res) > 0:
                result4 = '盐焗'
            p_res = get_info_by_pattern(product_name, pattern5)
            if len(p_res) > 0:
                result5 = '泡'
            p_res = get_info_by_pattern(product_name, pattern6)
            if len(p_res) > 0:
                result6 = '酱油'
            p_res = get_info_by_pattern(product_name, pattern7)
            if len(p_res) > 0:
                result7 = '酱卤'
            p_res = get_info_by_pattern(product_name, pattern7)
            if len(p_res) > 0:
                result8 = p_res[0]

    if len(result7)>0:
        return result7
    if len(result5)>0 and len(result6)>0:
        return '泡卤'
    if len(result5)>0 and len(result6)==0:
        return '泡制'
    if len(result4)>0:
        return result4

    if len(result2)>0:
        return result2
    if len(result1)>0:
        return result1

    if len(result3)>0:
        return result3
    if len(result8)>0:
        return result8
    return '不分'

def get_package_160(base64strs):
    '''
    调用服务提取包装信息
    :param base64strs: 图片列表
    :return:
    '''
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

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if material == "纸":
        material = "纸"
    else:
        material = "塑料"

    if shape in ["盒", "托盘"]:
        shape = "盒"

    result = material + shape
    if '袋' in result :
        return '袋装'
    elif '塑料瓶' in result:
        return '塑料瓶、桶'
    elif '纸' in result or "礼包" in result:
        return '纸盒、礼盒'
    return result


# 入口函数
def category_rule_160(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    # 系列	配料	产品类型	子品类	种类	口味	去骨/去皮	包装	储藏方式	独立装	健康概念	加工工艺
    SubBrand = "不分"
    # 配料
    mixture = "不分"
    # 产品类型
    product_type = "不分"
    # 子品类
    subcategory = "不分"
    # 种类
    type = "不分"
    # 口味
    taste = "不分"
    # 去骨/去皮
    boning = "不分"
    # 包装
    package = "不分"
    # 储藏方式
    storage='不分'
    # 独立装/非独立装
    independent_packet ='非独立装'
    # 健康概念
    health_concept ='不分'
    # 加工工艺
    processing_technology='不分'

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["a1","决心","爱鸭","抢鲜","有情","Aji","精武","快动","有才","拍手","KGA","香伴","优食","一扫光","全心","品品","OKQ","神仙"], [])

    brand_1 = re.sub('肥河牛', "淝河牛", brand_1)
    brand_1 = re.sub('壹学香', "一掌香", brand_1)
    brand_1 = re.sub('吃卷货子', "吃圈货子", brand_1)

    #测试用，暴露更多的品牌，过滤刷选用
    # brand_1_test, brand_2_test = get_brand_list_test(datasorted)
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)

        product_name = re.sub('鸭堂', "鸭掌", product_name)
        product_name = re.sub('鸭盹', "鸭肫", product_name)
        product_name = re.sub('蝴辣', "糊辣", product_name)
        product_name = re.sub('鸭拿', "鸭掌", product_name)
        product_name = re.sub('出椒', "山椒", product_name)

        product_name = re.sub('凤[爪瓜]', "凤爪", product_name)
        product_name = re.sub('鸭[爪瓜]', "鸭爪", product_name)
        product_name = re.sub('鸡[爪瓜]', "鸡爪", product_name)
        product_name = re.sub('多味[爪瓜]', "多味爪", product_name)

        product_name = re.sub('\W', "", product_name)
        if product_name.startswith('名'):
            product_name = product_name[1:]
        pattern = "\w+g|\w+克"
        p_res = get_info_by_pattern(product_name, pattern)
        if len(p_res) > 0:
            product_name = re.sub(p_res[0], "", product_name)
        if product_name != '不分' and brand_1 != '不分' and brand_1.title() in product_name.title():
            product_name = product_name.title().replace(brand_1.title(), '')
    taste = get_taste(datasorted,product_name)

    if product_name != '不分' and taste != '不分' and taste not in product_name and '风味' in taste:
        product_name = taste+product_name
    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋罐盒", 0)
    if capcity_2 != "不分":
        pattern = "\*(\d+)"
        # 独立装：包装内有独立小包，或重量注明内有几小包的产品类似：15克*4袋
        # 非独立装：包装内没有独立小包，或无法区分是否独立装时。
        p_res = get_info_by_pattern(capcity_2, pattern)
        if len(p_res) > 0 and int(p_res[0]) > 1:
            independent_packet = '独立装'

    # 系列
    SubBrand = get_SubBrand(datasorted)
    # 配料
    mixture = get_mixture(dataprocessed,datasorted)
    mixture = re.sub('鸭盹', "鸭肫", mixture)
    mixture = re.sub('凤爪', "鸡爪", mixture)
    mixture = re.sub('鸭堂', "鸭掌", mixture)
    mixture = re.sub('鸭拿', "鸭掌", mixture)

    product_type = get_keyValue(dataprocessed, ["产品类型",'产品菱型'])
    product_type = get_product_type(product_type,dataprocessed,datasorted)
    subcategory = get_subcategory(product_name,datasorted)
    type = get_type(product_name,datasorted)
    if type !='不分':
        type = re.sub('凤爪', "鸡爪", type)
    boning = get_boning(product_name, datasorted)
    storage = get_storage(datasorted)
    health_concept = get_health_concept(datasorted)
    processing_technology = get_processing_technology(product_name,product_type, datasorted)

    # image_list = ["/data/zhangxuan/images/43-product-images" + i.split("ocr_test")[-1].replace("\\", "/") for i in base64strs]
    package = get_package_160(base64strs)


    # 系列	配料	产品类型	子品类	种类	口味	去骨/去皮	包装	储藏方式	独立装	健康概念	加工工艺
    result_dict['info1'] = SubBrand
    # 配料
    result_dict['info2'] = mixture
    # 产品类型
    result_dict['info3'] = product_type
    # 子品类
    result_dict['info4'] = subcategory
    # 种类
    result_dict['info5'] = type
    # 口味
    result_dict['info6'] = taste
    # 去骨/去皮
    result_dict['info7'] = boning
    # 包装
    result_dict['info8'] = package
    # 储藏方式
    result_dict['info9'] = storage
    # 独立装
    result_dict['info10'] = independent_packet
    # 健康概念
    result_dict['info11'] = health_concept
    # 加工工艺
    result_dict['info12'] = processing_technology


    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])
    real_use_num = 12
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\160-肉类零食'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3124131"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_160(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)