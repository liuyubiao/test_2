import os
import re

from util import *
from glob import glob
# from utilCapacity import get_capacity
LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/148_brand_list_1", encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/148_brand_list_2", encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/148_taste_list", encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/148_type_list", encoding="utf-8").readlines())]

absor_taste = [i for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")


#提取口味信息
def get_taste(texts_list,product_name):
    '''
    提取口味信息，
    提取依据：148定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、形状包含：粒状、砖状、球状、短厚片状、长薄片状、块状、卷状、圆环状、其它（请注明)
    2、一个产品如果有多种口味，用中文“，”隔开

    口味可以是：巧克力/咖啡/香草/红豆/绿豆/桔子/其它（请注明）
    :param texts_list: 有序文本列表
    :param product_name: 商品全称
    :return:
    '''
    pattern = "(\w+味)"
    result = get_info_list_by_list([[product_name, ], ], Taste_list)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0 and p_res[0] not in ["口味", "新口味"]:
            Flag = True
            for i in Taste_Abort_List:
                if i in p_res[0]:
                    Flag = False
                    break
            if Flag:
                result.append(p_res[0])

    if len(result) == 0:
        result= get_taste_normal(texts_list, Taste_list)
        return result
    else:
        # result = list(set(result))
        return "，".join(result)
        # return result[0]

def get_package(texts_list):
    pattern = "[两\d]+支装?$"
    num = "不分"
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res_1 = get_info_by_pattern(text, pattern)
            if len(p_res_1) > 0 and "1支" not in text:
                num = re.compile("[两\d]+支").findall(text)[0]
                return "多包装", num

    pattern = "^支装?$"
    num = "不分"
    for texts in texts_list:
        for index,text in enumerate(texts):
            p_res_1 = get_info_by_pattern(text, pattern)
            total_len = len(texts)
            if len(p_res_1) > 0:
                for i in [-2,-1,1,2]:
                    if index + i >=0 and index + i <total_len:
                        p_res_tmp = re.compile("^\d{1,2}$").findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            num = int(p_res_tmp[0])
                            break
                return "多包装",num
    return "单包装",num


def get_package_size(texts_list):
    pattern = "\w*家庭装$"
    for texts in texts_list:
        for text in texts:
            p_res_1 = get_info_by_pattern(text, pattern)
            if len(p_res_1) > 0:
                return "家庭装"
    return "不分"


def get_type_bak(texts_list):
    pattern_1 = "(饮用水|纯净水|\W*水\W+|冰棍|冰棒)"
    pattern_2 = "(牛奶|乳清?粉|奶粉|牛乳|奶$)"
    flag_1 = False
    flag_2 = False
    for texts in texts_list:
        for text in texts:
            if not flag_1:
                p_res_1 = get_info_by_pattern(text, pattern_1)
                if len(p_res_1) > 0:
                    flag_1 = True
            if not flag_2:
                p_res_2 = get_info_by_pattern(text, pattern_2)
                if len(p_res_2) > 0:
                    flag_2 = True

    if flag_1 and not flag_2:
        return "纯冰"
    elif flag_2 and not flag_1:
        return "纯牛奶"
    elif flag_1 and flag_2:
        return "混合"
    else:
        return "混合"

#提取类型
def get_type(texts_list):
    '''
    提取类型，
    提取依据：148定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
      纯冰：  配料中含水，不含奶的
      纯牛奶：配料中含奶，不含水的
      混合：  配料中又含水又含奶的
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern_1 = "(饮用水|纯净水|\W*水\W+|冰棍|冰棒|配料水$)"
    pattern_2 = "(牛奶|乳清?粉|奶粉|牛乳|奶$|乳固体|乳制品)"
    flag_1 = False
    flag_2 = False
    for texts in texts_list:
        for text in texts:
            if not flag_1:
                p_res_1 = get_info_by_pattern(text, pattern_1)
                if len(p_res_1) > 0:
                    flag_1 = True
            if not flag_2:
                p_res_2 = get_info_by_pattern(text, pattern_2)
                if len(p_res_2) > 0:
                    flag_2 = True

    if flag_1 and not flag_2:
        return "纯冰"
    elif flag_2 and not flag_1:
        return "纯牛奶"
    elif flag_1 and flag_2:
        return "混合"
    else:
        return "混合"
#提取商品全称
def get_productName_voting(texts_list,kvs_list):
    pattern_pres = "容量|包含|[的是]"
    product_name=''
    result_list = []
    pre_result_list = []
    abort_list =['容量','包含','的','是']
    pattern_1 = "("
    for i in Type_list:
        pattern_1 += "\w+" + i + "|"
    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1.replace("+","*")[:-1]


    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0 and '类型' not in text:
                if len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        product_name = count[0][0]

    if len(product_name)==0:
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern_2)
                if len(p_res) > 0 and '类型' not in text:
                    if len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                        result_list.append(p_res[0])


        if len(result_list) > 0:
            result_list.sort(key=len, reverse=True)
            count = Counter(result_list).most_common(2)
            product_name = count[0][0]


    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if "品名" in k:
                    if len(kv[k]) > 1 :
                        flag = True
                        for it in abort_list:
                            if it in kv[k]:
                                flag = False
                                break
                        if flag:
                            pre_result_list.append(kv[k])

    if len(pre_result_list) > 0 :
        pre_result_list.sort(key=len, reverse=True)
        if len(pre_result_list[0])>=len(product_name):
            product_name = pre_result_list[0]

    if len(product_name) >0:
        return product_name
    return "不分"


#取出所有品牌，目的是为了刷选品牌用
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
        count = Counter(brand_1_list).most_common(6)
        brand_1 = ",".join([i[0] for i in count])
    return brand_1,brand_2

def get_Capacity(kvs_list,texts_list):
    pattern = r'(净含量?|净重|^[\u4e00-\u9fa5]?含量$|[Nn][Ee][Tt][Ww]|重量)'
    # pattern = r'(\d+\.?\d*)\s?(G|g|克|千克|kg|KG|毫升|升|L|ml|ML|mL)'
    pattern2 = r'(\d+\.?\d*|I\.?\d*)\s?(G|g|克|千克|kg|KG|毫升|升|L|ml|ML|mL)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    kvp = kv[k].replace('I', '1')
                    p_res = re.compile(pattern2).findall(kvp)
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克", "kg", "KG"]:
                                if float(p_res[0]) <= 10:
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
                    # pattern = r'(\d+\.?\d*)\s?(G|g|克|千克|kg|KG|毫升|升|ml|L|ML|mL)'
                    kvp = kv[k].replace('I','1')
                    p_res = re.compile(pattern2).findall(kvp)
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克", "kg", "KG"]:
                                if float(p_res[0]) <= 10:
                                    return p_res[0] + p_res[1]
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= 1:
                                    return p_res[0] + p_res[1]


    return "不分"

def get_Capacity_bak(texts_list):
    p = re.compile(r'(\d+\.?\d*)\s?(G|g|千克|克|kg|KG|Kg|ml|ML|mL|毫升)')
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
    p = re.compile(r'(\d+\.?\d*)\s?(G|g|千克|克|kg|KG|Kg|ml|ML|mL|毫升)')
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

def get_Capacity_bak_2(texts_list):
    pattern = r'(净含量?|净重|^[\u4e00-\u9fa5]?含量$|[Nn][Ee][Tt][Ww]|重量)'
    num = "不分"
    for texts in texts_list:
        for index,text in enumerate(texts):
            p_res_1 = get_info_by_pattern(text, pattern)
            total_len = len(texts)
            if len(p_res_1) > 0:
                for i in [-2,-1,1,2]:
                    if index + i >=0 and index + i <total_len:
                        p_res_tmp = re.compile("^\d{1,2}$").findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            num = p_res_tmp[0] + "克"
                            break
                return num
    return num

def get_Capacity_2(texts_list):
    pattern = r'\d+\.?\d*\D*[Gg克lL升]\D{0,3}\d+\D?[包袋盒支杯个]装?\)?'
    pattern_2 = r'(\d+\.?\d*)\W*(G|g|克|kg|KG|Kg|ml|ML|mL|毫升)\D{0,3}(\d+)\D?[包袋盒支杯个]装?\)?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            if len(re.split("[*xX]\d", text)) > 2:
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
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0] or float(p_res_2[0]) < 100:
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[Gg克lL升][*xX]\d+[包袋盒支杯个\)]?'
    pattern_2 = r'(\d+\.?\d*)\W*(G|g|克|kg|KG|Kg|ml|ML|mL|毫升)[*xX](\d+)[包袋盒支杯个\)]?'
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
                    unit = p_res_2[1]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if float(p_res_2[0]) >= 1 and float(p_res_2[0]) <= 5000:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "",
                                                                                                              p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+[包袋盒支杯个][*xX]\d+\.?\d*\D*[Gg克lL升]'
    pattern_2 = r'(\d+)[包袋盒支杯个][*xX](\d+\.?\d*)\W*(G|g|克|kg|KG|Kg|ml|ML|mL|毫升)'
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
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[1]), unit)), re.sub(u"\)", "",
                                                                                                              p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[Gg克lL升]\D{0,3}\d+\D*\)$'
    pattern_2 = r'(\d+\.?\d*)\W*(G|g|克|kg|KG|Kg|ml|ML|mL|毫升)\D{0,3}(\d+)\D*'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                if len(re.compile("\d+\.\d+克\([\dg]\)").findall(text)) > 0:
                    continue
                if "(9)" in text:
                    continue
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    return "不分", re.sub(u"\)", "", p_res[0])

    return "不分", "不分"

def get_Capacity_2_bak(texts_list):
    p_bak = re.compile(r'(\d+)(\s?[包袋盒支杯个]装)')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1]

    p_bak = re.compile(r'(\d+)([包袋盒支杯个])\w*(装)$')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1] + p_res[2]

    p_bak = re.compile(r'内[装含](\d+)(小?[包袋盒支杯个])')
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return "内装"+ p_res[0] + p_res[1]
    return "不分"

#提取冰激凌形状
def get_icecream_shape(texts_list,capcity_1,product_name):
    '''
    提取冰激凌形状，
    提取依据：148定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：共有：条/棍/棒/杯/桶/盒/筒/砖/袋/其他等形状
    1、杯、桶装通常以克重来判断，如遇内部有多个的，例如带棍的需给“条/棍/棒”，内部为小块儿状的需给砖
    2、杯：雪糕存放在纸杯/胶杯中，通常要用匙来进食的，重量≤200克
    3、桶：雪糕存放在纸杯/胶杯中，通常要用匙来进食的，重量＞200克
    4、条/棍/棒定义：产品附在一根木或塑料的小棒上，用作把手（包括放在杯里带条/棍/棒的小支
    5、筒：定义：独立包装的威化筒，内藏雪糕，通常在雪糕面上加上果仁或朱古力酱等大是
    6、盒。定义：雪糕存放在盒中，盒子通常有盖或塑料纸覆盖，通常要用匙来进食的。（不区分克重，只要是四方形的就给盒）
    7、砖。定义：根据产品描述是砖形（四方形）的冰淇淋，不用任何器具就可以直接吃的(豆腐、方糕、冰淇淋派、千层雪)
    8、其他。定义：除了以上描述的形态的， 包括雪糕糯米糍，卷状等的产品
    :param texts_list: 有序文本列表
    :param capcity_1: 重容量
    :param product_name: 商品全称
    :return:
    '''

    pattern_gun = '棍'
    pattern1='\d+'
    pattern_bei = '杯'
    # 如果是碗，当成杯
    pattern_wan = '碗'
    pattern_tong1 ='桶盖'
    pattern_he = '盒'
    pattern_tong2 = '筒'
    pattern_dai = '袋'
    pattern_bang = '棒'
    pattern_zuan = '砖'

    p_res1 = get_info_by_pattern(capcity_1, pattern1)
    weight = 0
    if len(p_res1) > 0:
        weight = int(p_res1[0])

    # if ('豆腐' in product_name or '方糕' in product_name or '冰淇淋派' in product_name or '千层雪' in product_name or '充电宝' in product_name):
    # if ('豆腐' in product_name or '方糕' in product_name or '冰淇淋派' in product_name or '千层雪' in product_name):
    #     shape = pattern_zuan
    #     return shape

    if (pattern_bei in product_name or pattern_wan in product_name):
        shape = pattern_bei
        return shape
    if pattern_tong1 in product_name :
        shape = pattern_tong1.replace('盖','')
        return shape

    if  pattern_he in product_name:
        shape = pattern_he
        return shape
    if  pattern_tong2 in product_name:
        shape = pattern_tong2
        return shape
    if  pattern_dai in product_name:
        shape = pattern_dai
        return shape
    if  pattern_bang in product_name:
        shape = pattern_bang
        return shape
    if  '冰棍' in product_name:
        shape = pattern_gun
        return shape

    for texts in texts_list:
        for text in texts:
            # if ('豆腐' in text or '方糕' in text or '冰淇淋派' in text or '千层雪' in text or '充电宝' in text):
            if ('豆腐' in text or '方糕' in text or '冰淇淋派' in text or '千层雪' in text):
                shape = pattern_zuan
                return shape
            if  (pattern_bei in text or pattern_wan in text):
                shape = pattern_bei
                return shape

            if pattern_tong1 in text :
                shape = pattern_tong1.replace('盖','')
                return shape
            if  pattern_he in text and '元/盒' not in text:
                shape = pattern_he
                return shape
    if  '升' in capcity_1 or 'L' in capcity_1:
        shape = pattern_tong1.replace('盖','')
        return shape
    return pattern_gun


#提取产品形态
def get_product_shape(shape,type,product_name,texts_list):
    '''
    提取产品形态
    提取依据：148定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、形状为条/棍/棒: （作为判断种类字段“是否有巧克力包裹”的依据）该类型的产品形态没有不分！！！
       1.1、 有巧克力包裹的：冰淇淋表面有巧克力脆皮的，白巧克力也可以（配料表、网搜图）
       1.2、 类型为纯冰的：有巧克力包裹的优先给巧克力包裹，否则给：纯水/纯冰：
    2、除‘条/棍/棒’外的其它形状，如杯、桶、盒、筒、砖、其他的：只要类型是“混合”或“纯牛奶”都给：以奶成分为主；
       只要类型是“纯冰”的，都给“纯水/纯冰”。
       否则 给‘不分’
    :param shape: 冰激凌形状
    :param type: 类型（混合、纯冰、纯牛奶）
    :param product_name: 商品全称
    :param texts_list: 有序文本
    :return:
    '''

    if '条' in shape or '棍' in shape or '棒' in shape:
        if '巧克力脆皮' in product_name:
            return '有巧克力包裹'
        count1 = 0
        count2 = 0
        for texts in texts_list:
            for text in texts:
                if '巧克力脆皮' in text:
                    return '有巧克力包裹'
                if '巧克力' in text or '生巧' in text or '克力' '生巧' in text:
                    count1+=1
                if  '脆皮' in text or '脆' in text:
                    count2+=1
            if count1 >= 1 and count2 >= 0:
                return '有巧克力包裹'

        return '无巧克力包裹'
        # if type=='纯冰':
        #     return '纯水/纯冰'
        # else:
        #     return '无巧克力包裹'
    else:
        return '不分'
        # # if '杯' in shape or '桶' in shape or '盒' in shape or '筒' in shape:
        # if type=='混合' or type=='纯牛奶':
        #     return '以奶成分为主'
        # elif type=='纯冰':
        #     return '纯水/纯冰'
        # else:
        #     return '不分'

#提取包装类型
def get_package_148_unit(base64strs):
    url = url_classify + ':5040/yourget_opn_classify'

    task = MyThread(get_url_result, args=(base64strs, url,))
    task.start()
    # 获取执行结果
    result = task.get_result()
    result_list =[]
    for it in result:
        #只选出塑料杯、塑料盒、冰淇淋筒三种类型的，其他数据过滤掉
        if  '塑料杯' in it or  '塑料盒' in it or  '冰淇淋筒' in it:
            it = re.sub("塑料杯", "杯", it)
            it = re.sub("塑料盒", "盒", it)
            it = re.sub("冰淇淋筒", "筒", it)
            result_list.append(it)

    if len(result_list) == 0:
        return "不分"
    #塑料杯、塑料盒、冰淇淋筒
    res = Counter(result_list).most_common(1)[0]
    if len(result)>5 and int(res[1])>1 or len(result)<5:
        return res[0]
    else:
        return '不分'

#规则提取总函数
def category_rule_148(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    brand_3 = "不分"
    type = "不分"
    taste = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    package_size = "不分"
    package = "不分"
    num_package = "不分"

    shape = "不分"
    shape_type = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    brand_1_test=''
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["NOC","FSC"], [])

    brand_1 = re.sub("MAGNUM","梦龙",brand_1)

    # product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(datasorted,dataprocessed)
        product_name = re.sub('\W', "", product_name)
        if brand_1.title() in product_name.title():
            product_name = product_name.title().replace(brand_1.title(),'')
        # product_name = re.sub('\W', "", product_name)
        product_name = re.sub('榴连', "榴莲", product_name)
        product_name = re.sub('^系列', "", product_name)
    if len(product_name) < 2:
        product_name = "不分"


    capcity_1 = get_Capacity(dataprocessed, datasorted)
    capcity_1_bak, capcity_2 = get_Capacity_2(datasorted)
    if capcity_1_bak != "不分":
        if capcity_1 == "不分":
            capcity_1 = capcity_1_bak
        elif re.compile("\d+\.?\d*").findall(capcity_1)[0] in capcity_2:
            capcity_1 = capcity_1_bak
    if capcity_1 == "不分":
        capcity_1 = get_Capacity_bak_2(datasorted)
    if capcity_1 == "不分":
        capcity_1 = get_Capacity_bak(datasorted)
    if capcity_2 != "不分":
        try:
            num_0 = float(re.compile("\d+\.?\d*").findall(capcity_1)[0])
            num_1, num_2 = re.compile("\d+\.?\d*").findall(capcity_2)
            if float(num_1) * float(num_2) != num_0 and num_0 != float(num_1) and num_0 != float(num_2):
                capcity_2 = "不分"
        except:
            pass
    if capcity_2 == "不分":
        capcity_2 = get_Capacity_2_bak(datasorted)

    # # 包袋盒罐支杯粒瓶片
    # capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒支杯个", 0)
    if type == "不分":
        type = get_type(datasorted)

    if taste == "不分":
        taste = get_taste(datasorted,product_name)
        if len(product_name) == 2 and product_name != "不分" and taste != "不分":
            product_name=taste+product_name

    if package == "不分":
        package, num_package = get_package(datasorted)
        package = package if capcity_2 == "不分" else "多包装"

    if capcity_2 == "不分" and num_package != "不分":
        capcity_2 = "%s装" % str(num_package)

    if package_size == "不分":
        package_size = get_package_size(datasorted)

    if package_size == "不分" and capcity_1 != "不分":
        num_res = re.compile("\d+").findall(capcity_1)
        if len(num_res) > 0:
            num = num_res[0]
            if int(num) > 200 or "千克" in capcity_1:
                package_size = "家庭装"

    if package_size == "不分":
        package_size = "即食"

    if len(re.compile("^味").findall(product_name)) > 0 or len(re.compile("^[口风]味").findall(product_name)) > 0:
        product_name = taste.split("味")[0] + product_name.split("味")[-1]

    if type == "纯冰" and "雪糕" in product_name:
        type = "混合"

    # base64strs = ["/data/zhangxuan/images/43-product-images" + i.split("格式化数据-43")[-1].replace("\\", "/") for i in image_list]
    # 测试用，需要把路径转一下，正式的时候不用修改路径
    # image_list = ["/data/zhangxuan/images/43-product-images" + i.split("ocr_test")[-1].replace("\\", "/") for i in base64strs]
    shape = '棍'
    if  '可爱多' in product_name or '火炬' in product_name:
        shape='桶'
    elif ('豆腐' in product_name or '方糕' in product_name or '冰淇淋派' in product_name or '千层雪' in product_name or '充电宝' in product_name):
        shape = '砖'
    else:
        shape = get_package_148_unit(base64strs)
        if shape == '不分':
            shape = get_icecream_shape(datasorted, capcity_1, product_name)
        else:
            if shape == '杯':
                #如果是杯子，通过质量来判断杯子和桶，一般杯子：重量≤200克 桶：重量>200克
                if '千克' in capcity_1 or 'L' in capcity_1 or '升' in capcity_1 or 'KG' in str(capcity_1).upper():
                    shape = '桶'
                else:
                    pattern1 = '\d+'
                    p_res1 = get_info_by_pattern(capcity_1, pattern1)
                    if len(p_res1) > 0 and int(p_res1[0]) >= 500:
                        shape = '桶'
    shape_type = get_product_shape(shape,type,product_name,datasorted)

    # 品牌3
    result_dict['info1'] = brand_3
    # 口味
    result_dict['info2'] = taste
    # 类型
    result_dict['info3'] = type
    # 单包装/多包装
    result_dict['info4'] = package
    # 包装大小
    result_dict['info5'] = package_size
    # 形状
    result_dict['info6'] = shape
    # 产品形态
    result_dict['info7'] = shape_type


    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    for k in result_dict.keys():
        result_dict[k] = re.sub("[,，：:]", "", result_dict[k])

    #测试用
    # result_dict['info8'] = shape2
    real_use_num = 7
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict


if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_2\148-冰淇淋'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        product = "3072938"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_148(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)