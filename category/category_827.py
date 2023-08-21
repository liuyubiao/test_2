import os
import re

from util import *
from glob import glob
# from util import get_info_item_by_list,get_info_list_by_list
from utilCapacity import get_capacity
from category_101 import FRUIT_LIST

LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/827_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/827_brand_list_2",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/827_taste_list",encoding="utf-8").readlines())]
suffix_name_list = [i.strip() for i in open("Labels/827_suffix_name_list",encoding="utf-8").readlines()]
absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")

Vegetable_List = [i.strip() for i in set(open("Labels/102_type_list",encoding="utf-8").readlines())]
Vegetable_List.append("藜麦")

Meat_List = ["牛","羊","鸡","猪","鱼","虾","鸭","鹅"]
FRUIT_LIST.append("果泥")


#调用公告方法提取口味
def get_taste(texts_list,product_name):
    '''
    调用公告方法提取口味
    基本思路是要维护口味列表827_taste_list，根据商品名称全程和口味列表进行匹配提取
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
        return res.replace('，','')
    else:
        return "".join(result)

def get_type_bak(product_name):
    if "米粉" in product_name or "米乳" in product_name or "米精" in product_name  or "米糊" in product_name \
            or "米稀" in product_name or "圈" in product_name or "谷物" in product_name or "谷粉" in product_name:
        return "婴儿米、麦粉(精)"

    if "奶" in product_name:
        return "奶制品"

    flag_f = 0
    flag_v = 0
    flag_m = 0
    for f in FRUIT_LIST:
        if f in product_name:
            flag_f = 1

    for v in Vegetable_List:
        if v in product_name:
            flag_v = 1

    for m in Meat_List:
        if m in product_name:
            flag_m = 1

    if flag_v + flag_m + flag_v >1:
        return "混合泥"
    elif flag_f == 1:
        return "水果泥"
    elif flag_v == 1:
        return "蔬菜泥"
    elif flag_m == 1:
        return "肉泥"

    return "不分"

#提取分类
def get_type(product_name):
    '''
    提取分类
    提取依据：827定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、全称包含：米粉、米乳、米精、米糊、谷粉、虾片、燕麦粉、谷物、米稀、泡芙条、米饼 ：统一为：“婴儿米、麦粉(精)”
    2、全称包含：奶字的，给“酸奶块”或“奶制品”
    3、全称包含：包含水果并且包含“汁”的给果汁泥
    4、全称包含：包含水果并且包含“泥”的给水果泥
    5：全称包含：包含蔬菜并且包含“泥”的给蔬菜泥
    :param product_name: 商品全称
    :return:
    '''
    list1_type = ['米粉','米乳','米精','米糊','谷粉','虾片','燕麦粉','谷物','米稀','泡芙条','米饼']
    for it in list1_type:
        if it in product_name:
            return "婴儿米、麦粉(精)"
    if "奶" in product_name:
        return "酸奶块"
    flag_f = 0
    flag_v = 0
    flag_m = 0
    flag_j = 0
    for f in FRUIT_LIST:
        if f in product_name:
            flag_f = 1
        if flag_f==1 and  '汁' in product_name:
            flag_j =1

    for v in Vegetable_List:
        if v in product_name:
            flag_v = 1

    for m in Meat_List:
        if m in product_name:
            flag_m = 1

    if flag_v + flag_m + flag_v >1:
        return "混合泥"
    elif flag_j == 1:
        return "果汁泥"
    elif flag_f == 1:
        return "水果泥"
    elif flag_v == 1:
        return "蔬菜泥"
    elif flag_m == 1:
        return "肉泥"

    return "不分"

#提取子类型subtype
def get_type_2(product_name,type_1):
    '''
    子类型subtype
    :提取依据：827定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、根据分类（婴儿米、麦粉(精)、果汁泥、水果泥、混合泥）进行子类型的划分
    :param product_name: 商品全称
    :param type_1: 分类
    '''
    type_mi_list = ['DHA铁锌钙','铁锌钙益生菌','铁锌钙小米','强化铁','维C加铁','益生菌','高铁高钙蔬菜','高钙高铁','AD钙铁锌','维D加钙','铁锌钙','钙铁锌',
                    '多维高钙','胡萝卜小米','胡萝卜苹果','胡萝卜蔬菜','果蔬多维','强化锌','强化铁','水果蔬菜','维C加铁','高锌乳酸菌','氨基酸','蔬菜']
    type_gu_list = ['藜麦','燕麦']
    if type_1 == "婴儿米、麦粉(精)":
        for it in type_mi_list:
            if it in product_name:
                return it
        return '不分'
    elif type_1 == '果汁泥':
        return '水果'
    elif type_1 == '水果泥':
        return '水果'
    elif type_1 == '混合泥':
        flag_f = 0
        flag_g = 0
        flag_s = 1 if '蔬' in product_name else 0
        for f in FRUIT_LIST:
            if f in product_name:
                flag_f = 1
                break
        for f in type_gu_list:
            if f in product_name:
                flag_g = 1
                break
        if flag_f==1:
            if flag_s == 1 and flag_g == 1:
                return '谷物+蔬菜+水果'
            elif flag_g == 1:
                return '谷物+水果'
            elif flag_s == 1:
                return '蔬菜+水果'
        else:
            if flag_s == 1 and flag_g == 1:
                return '蔬菜+谷物'

    return "不分"

def get_productName_voting(texts_list):
    pattern_pres = "的|\d+\.?\d*[CcMm][mM]"
    result_list1 = []
    result_list2 = []
    result_list3 = []
    # abort_list = ['入','只做','与','吸','要','加']
    abort_list = ['入', '只做', '与', '吸','要','含']
    pre_result_list = []
    pattern_1 = "("
    for i in suffix_name_list:
        pattern_1 += "\w+" + i + "|"
    pattern_1 = pattern_1[:-1] + ")($|\()"
    pattern_2 = pattern_1.replace("+", "*")[:-6]
    # pattern_3 = "\w+泥|\w+汁"
    pattern_3 = "\w+泥$|\w+汁$|\w*米[粉乳糊]"
    for texts in texts_list:
        # text_orig =''.join(texts)
        for text in texts:
            flag = True
            for it in abort_list:
                if it in text:
                    flag = False
                    break
            if flag:
                flag = False
                p_res = get_info_by_pattern(text, pattern_1)
                if len(p_res) > 0 :
                    p_res = p_res[0]
                    if len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                        flag = True
                        result_list1.append(p_res[0])

                else:
                    p_res = get_info_by_pattern(text, pattern_2)
                    if len(p_res) > 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                        flag = True
                        result_list2.append(p_res[0])
                    else:
                        p_res = get_info_by_pattern(text, pattern_3)
                        if len(p_res) > 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                            flag = True
                            result_list3.append(p_res[0])
                if flag:
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])

    if len(pre_result_list)>0:
        pre_result_list.sort(key=len,reverse=True)
        return pre_result_list[0]
    if len(result_list1) > 0:
        result_list1.sort(key=len,reverse=True)
        count = Counter(result_list1).most_common(2)
        return count[0][0]

    if len(result_list2) > 0:
        count = Counter(result_list2).most_common(2)
        return count[0][0]

    if len(result_list3) > 0:
        count = Counter(result_list3).most_common(2)
        return count[0][0]


    return "不分"

#提取适用阶段
def get_age(texts_list):
    result_list = []
    pattern = "(辅食添加)?初期\-(\d+)个?月?"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                result_list.append(p_res[0][1])
                # return "辅食添加初期-%s个月"% (p_res[1])

    if len(result_list)>0:
        count = Counter(result_list).most_common(1)
        result = count[0][0]
        return "辅食添加初期-%s个月" % (result)

    pattern = "(\d{1,2}\-?\d*个?月)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if p_res[0] == '6-36个月':
                    return p_res[0]
                elif p_res[0] == '6-36月':
                    return '6-36个月'


    pattern = "(\d{1,2})个?月龄?(以上|起)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                p_res = p_res[0]
                return p_res[0]+'个月以上'


    pattern = "(\d+)月龄"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                t = int(p_res[0])
                if t > 100:
                    t = str(int(t / 100)) + '-' + str(int(t % 100)) + '个月'
                    return t

    pattern = "\d+[\-至到]\d+个?月"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                if '婴幼儿' in text or '龄' in text or '适用' in text:
                    return p_res[0]

    start_pattern = "(辅食\w*初期\d*|6个?月)"
    start_list = []
    end_pattern = "(36个月)"
    end_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, start_pattern)
            if len(p_res) > 0:
                start_list.append(p_res[0])
            p_res = get_info_by_pattern(text, end_pattern)
            if len(p_res) > 0:
                end_list.append(p_res[0])

    if len(start_list) > 0:
        count = Counter(start_list).most_common(1)
        start_info = count[0][0]
        if len(end_list) == 0:
            return start_info + "以上"
        else:
            start_info = start_info.replace('个月','')
            if len(start_info)>len('辅食添加初期'):
                start_info = start_info.replace('辅食添加初期','')
            return start_info + "-36个月"

    return "不分"

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

def get_package_827(base64strs):
    url_shape = url_classify + ':5029/yourget_opn_classify'
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    result_shape = task_shape.get_result()

    if len(result_shape) > 0:
        shape = Counter(result_shape).most_common(1)[0][0]
        if "袋" in shape:
            shape = "袋"
        elif "桶" in shape or "杯" in shape or "瓶" in shape:
            shape = "桶"
        elif shape in ["托盘","格","盒"]:
            shape = "盒"
        elif "罐" in shape:
            shape = "罐"
        elif "礼包" in shape:
            shape = "礼盒"
        else:
            shape = "罐"
        return shape + "装"
    else:
        return "盒装"

def category_rule_827(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    type_1 = "不分"
    taste = "不分"
    age = "不分"
    package = "不分"
    package_num = "1"
    Subbrand = "不分"
    type_2 = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], [], [])
        brand_1 = re.sub("禾决决", "禾泱泱", brand_1)
    # 测试用，暴露更多的品牌，过滤刷选用
    # brand_1_test, brand_2_test = get_brand_list_test(datasorted)

    # product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)
        product_name = re.sub("药麦", "藜麦", product_name)
        product_name = re.sub("禾决决", "禾泱泱", product_name)
        product_name = re.sub("果乐土", "果乐士", product_name)


    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐", 0)
    if capcity_2 != "不分":
        try:
            pattern = "(\d+\.?\d*)\D+(\d+)[克g]"
            p_res = re.compile(pattern).findall(capcity_2)
            if len(p_res) > 0:
                p_res = p_res[0]
                package_num = str(int(float(p_res[0])/float(p_res[1])))
            else:
                pattern = "\d+\.?\d*\D+(\d+)"
                p_res = re.compile(pattern).findall(capcity_2)
                package_num = p_res[0]
        except:
            pass


    type_1 = get_type(product_name)
    taste = get_taste(datasorted,product_name)
    if taste!='不分'  and taste not in product_name and product_name != "不分":
        product_name = taste+product_name

    # age = get_keyValue(dataprocessed,["宜人"])
    if age == "不分":
        age = get_age(datasorted)


    if age == "不分":
        age = re.sub("不分", "未注明", age)

    # type_2 = get_keyValue(dataprocessed, ["品类"])
    if type_2 == "不分" or len(type_2) > 8:
        type_2 = get_type_2(product_name,type_1)

    package = get_package_827(base64strs)

    #分类
    result_dict['info1'] = type_1
    #口味
    result_dict['info2'] = taste
    #适用阶段
    result_dict['info3'] = age
    # 包装类型
    result_dict['info4'] = package
    # 共有几包
    result_dict['info5'] = package_num
    # Subbrand
    result_dict['info6'] = Subbrand
    # 子类型subtype
    result_dict['info7'] = type_2
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name
    # result_dict['info8'] = brand_1_test
    real_use_num = 7
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\827-婴儿食品'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3087751"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_827(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)