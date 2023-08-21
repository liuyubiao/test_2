import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity
from utilInside import *

LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/196_brand_list_1",encoding="utf-8").readlines())]
suffix_name_list = [i.strip() for i in open("Labels/196_suffix_name_list",encoding="utf-8").readlines()]
content_list = [i.strip() for i in open("Labels/196_content_list",encoding="utf-8").readlines()]

Ingredients_list_ori = [i.strip() for i in open("Labels/196_ingredients_list",encoding="utf-8").readlines()]

Ingredients_list = []
for line in Ingredients_list_ori:
    Ingredients_list.extend(re.split("[^\-0-9a-zA-Z\u4e00-\u9fa5]",line))
Ingredients_list = set(Ingredients_list)
Ingredients_list.remove("")
Ingredients_list = list(Ingredients_list)
Ingredients_list.sort(key=len,reverse=True)


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
    pattern_abort = '产品类型|含'
    pre_result_list = []
    pattern_1 = "("
    for i in suffix_name_list:
        pattern_1 += "\w+" + i + "|"

    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1.replace("+", "*")[:-1]


    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_abort)
            if len(p_res) == 0:
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
            p_res = get_info_by_pattern(text, pattern_abort)
            if len(p_res) == 0:
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


def get_key_Value(kvs_list,keys):
    result_list = []
    for kvs in kvs_list:
        for kv in kvs:
            for key in keys:
                for k in kv.keys():
                    if len(key) == 1:
                        if key == k:
                            result_list.append(kv[k])
                    else:
                        if key == k and  len(k) < 6 and len(kv[k]) > 2:
                            result_list.append(kv[k])

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) >1 and count[0][1] == count[1][1] and len(count[0][0]) < len(count[1][0]) and len(re.compile("[0-9,，、]").findall(count[1][0])) == 0:
        return count[1][0]
    else:
        return count[0][0]

#提取适用人群
def get_suitpeople(product_name,kvs_list,texts_list):
    '''
    提取适用人群
    提取依据：196定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：注意包装特色对特殊人群的辨别，像儿童、男士、孕产妇、婴幼儿
    :param product_name: 商品全称
    :param kvs_list: 文本键值对
    :param texts_list: 有序文本列表
    :return:
    '''


    result = get_key_Value(kvs_list, ["适用人群",'适宜人群','建议人群','适合人群',"遵定人群","适室人群"])
    if result!='不分':
        return result

    pattern1 ='适宜人群:?(.+等人群)'
    pattern2 = '(适用人群|适室人群|遵定人群|适合人群|适宜人群|建议人群):?[\(\)]?(.+)[\(\)]?不\w{0,3}人'
    pattern3 = '(适用人群|适室人群|遵定人群|适合人群|适宜人群|建议人群):?[\(\)]?(.+)[\(\)]?(食用方法|量含|存储方法)'

    for texts in texts_list:
        text_origi = ''.join(texts)
        p_res = get_info_by_pattern(text_origi, pattern1)
        if len(p_res) > 0:
            if '不推荐' in p_res[0]:
                continue
            return p_res[0]
        else:
            p_res = get_info_by_pattern(text_origi, pattern2)
            if len(p_res) > 0:
                p_res = p_res[0]
                if text_origi.find(p_res[0]) == (text_origi.find('不' + p_res[0]) + 1) or '不推荐' in p_res[1] :
                    continue
                return p_res[1]
            else:
                p_res = get_info_by_pattern(text_origi, pattern3)
                if len(p_res) > 0:
                    p_res = p_res[0]
                    if text_origi.find(p_res[0])==(text_origi.find('不'+p_res[0])+1) or '不推荐' in p_res[1]:
                        continue
                    return p_res[1]

    pattern ='儿童|中老年|男士'
    p_res = get_info_by_pattern(product_name, pattern)
    if len(p_res) > 0:
        return p_res[0]
    return '不分'

# 提取功能信息
def get_function(kvs_list,texts_list):
    '''
    提取功能信息
    提取依据：196定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    :param kvs_list: 文本键值对
    :param texts_list: 有序文本列表
    '''
    result = get_keyValue(kvs_list, ["保健功能","功能与主治","功能","功效"])
    if result!='不分':
        result = result.replace('、','，').replace('本品经动物实验评价,','').replace(',','，')
        if len(result)>0:
            return result

    for texts in texts_list:
        text = ''.join(texts)
        if '保健功能' in text or '功能与主治' in text:
            if '改善睡眠' in text:
                return '改善睡眠'
            elif '增强免疫力' in text:
                return '增强免疫力'
            elif '补气养阴,清热生津' in text:
                return '补气养阴，清热生津'

    # if '维生素' in product_name:
    #     return '补充维生素'
    return '不分'

#提取容重量
def get_Capacity(texts_list):
    capacity2 = '不分'
    capacity1 = '不分'


    pattern = r'(净含量|净重|NETWT|重量|规格|商品规格)'
    pattern1 = '每盒(\d+)粒,每粒(\d+)(毫克)'
    pattern2 = '规格:?(\d+粒|\d+片)'
    pattern3 = '(\d\.?\d+)[g克]/片[Xx*]?(\d+)片'
    pattern4 ='规格:?(\d\.?\d+)[g克]\*?(\d+)[粒片]?/盒'
    pattern5='规格:?(\d+)[g克]'
    pattern6 = '规格:?(\d\.?\d+)[g克]/片[Xx*](\d+)[片粒]'
    pattern7='净含量:?(\d\.?\d+)[g克]/[粒片](\d+)[粒片]/盒(\d+)盒'

    for texts in texts_list:
        text_orig = ''.join(texts)
        p_res = re.compile(pattern).findall(text_orig)
        if len(p_res) > 0:
            p_res = re.compile(pattern1).findall(text_orig)
            if len(p_res) > 0:
                p_res = p_res[0]
                capacity1 = str(int(int(p_res[0])*int(p_res[1])/1000))+'克'
                capacity2 = str(round(float(p_res[1])/1000,1))+'克*'+p_res[0]
                return capacity1,capacity2
            else:
                p_res = re.compile(pattern2).findall(text_orig)
                if len(p_res) > 0:
                    capacity1 = p_res[0]
                    return capacity1, capacity2
                else:
                    p_res = re.compile(pattern3).findall(text_orig)
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        capacity1 = str(int(float(p_res[0])* int(p_res[1]))) + '克'
                        capacity2 = p_res[0] + '克*' + p_res[1]
                        return capacity1, capacity2
                    else:
                        p_res = re.compile(pattern4).findall(text_orig)
                        if len(p_res) > 0:
                            p_res = p_res[0]
                            capacity1 = str(float(p_res[0]) * int(p_res[1])) + '克'
                            capacity2 = p_res[0] + '克*' + p_res[1]
                            return capacity1, capacity2
                        else:
                            p_res = re.compile(pattern5).findall(text_orig)
                            if len(p_res) > 0:
                                capacity1 = p_res[0]+'克'
                                return capacity1, capacity2
                            else:
                                p_res = re.compile(pattern6).findall(text_orig)
                                if len(p_res) > 0:
                                    p_res = p_res[0]
                                    capacity1 = str(float(p_res[0]) * int(p_res[1])) + '克'
                                    capacity2 = p_res[0] + '克*' + p_res[1]
                                    return capacity1, capacity2
                                else:
                                    p_res = re.compile(pattern7).findall(text_orig)
                                    if len(p_res) > 0:
                                        p_res = p_res[0]
                                        capacity1 = str(float(p_res[0]) * int(p_res[1])* int(p_res[2])) + '克'
                                        capacity2 = p_res[0] + '克*' + p_res[1]+'*'+p_res[2]
                                        return capacity1, capacity2

    return "不分",'不分'

#提取容重量
def get_Capacity_2(texts_list):
    pattern = r'(净含量|净重|NETWT|重量|规格|商品规格)'
    pattern1 = '净含量:?.+(\d\.?\d)+(g|克|G|ml|ML|mL|Ml|毫升|毫克|mg|MG|mG|Mg)/?[片支粒包袋]?(\d+)[片支粒包袋]'
    pattern2 = '(\d+)[片支粒包袋][xX](\d+\.?\d+)[克gG]'
    # pattern3 = '(\d+)m?M?l?L?毫?升?/支[xX](\d+\.?\d+)支'
    # pattern3 = '(\d+)m?M?l?L?毫?升?g?G?/?[支粒片]?[xX]?(\d?\.?\d+)[片支粒]?'
    pattern3='(\d+)([mM毫][lLgG])/?[片支粒包袋]?[xX]?(\d?\.?\d+)[片支粒包袋]'
    pattern4 = '(\d?\.?\d+)[g克G][xX]?(\d+)[片支粒包袋]'
    pattern5='(\d+)[mM][lL][xX]?(\d+)[片支粒包袋]'
    pattern6='(\d?\.?\d+)[克gG][xX]?(\d+)[片支粒包袋]'
    pattern7='(\d+)[片支粒包袋][xX]?(\d?\.?\d+)[克gG]'
    pattern8='(\d?\.?\d+)[克gG]/?[片支粒包袋]?[xX*](\d+)/?[片支粒包袋]'
    pattern9='(\d?\.?\d+)[克gG]/?[片支粒包袋]?[xX*]?(\d+)[片支粒包袋]'
    pattern10='净含量:?\d{0,3}?[克gG]?[\(]?(\d?\.?\d+)[克gG]/?[片支粒包袋]?[xX*]?(\d+)[片支粒包袋]?'
    pattern11='净含量:?\d{0,3}?[mM毫]?[lL升]?[\(]?(\d?\.?\d+)[mM毫][lL升]?/?[片支粒包袋]?[xX*]?(\d+)[片支粒包袋]?'
    for texts in texts_list:
        text_orig = ''.join(texts)
        p_res = re.compile(pattern).findall(text_orig)
        if len(p_res) > 0:
            p_res = re.compile(pattern1).findall(text_orig)
            if len(p_res) > 0:
                p_res = p_res[0]
                unit ='克'
                funit = p_res[1].upper()
                if funit=='G' or funit=='克' or funit=='MG' or funit=='毫克':
                    unit = '克'
                elif funit=='ML' or funit=='毫升':
                    unit = '毫升'
                capacity1 = str(float(p_res[0]) * int(p_res[2]))+unit
                capacity2 = p_res[0] + unit+'*'+p_res[2]
                return capacity1,capacity2

        p_res = re.compile(pattern2).findall(text_orig)
        if len(p_res) > 0:
            p_res = p_res[0]
            capacity1 = str(float(p_res[1]) * int(p_res[0])) + '克'
            capacity2 = p_res[1] + '克*' + p_res[0]
            return capacity1, capacity2
        else:
            p_res = re.compile(pattern3).findall(text_orig)
            if len(p_res) > 0:
                p_res = p_res[0]
                unit = '克'
                funit = p_res[1].upper()
                if funit == 'G' or funit == '克' or funit == 'MG' or funit == '毫克':
                    unit = '克'
                    if funit == 'MG':
                        funit = '毫克'
                    elif funit == 'G':
                        funit = '克'
                elif funit == 'ML' or funit == '毫升':
                    unit = '毫升'
                    funit = '毫升'
                if '克' in unit:
                    capacity1 = str(int(float(p_res[0]) * int(p_res[2])) / 1000) + '克'
                else:
                    capacity1 = str(int(float(p_res[0]) * int(p_res[2]))) + unit
                capacity2 = p_res[0] + funit + '*' + p_res[2]
                return capacity1, capacity2
            else:
                p_res = re.compile(pattern4).findall(text_orig)
                if len(p_res) > 0:
                    p_res = p_res[0]
                    capacity1 = str(int(float(p_res[0]) * int(p_res[1]))) + '克'
                    capacity2 = p_res[0] + '克*' + p_res[1]
                    return capacity1, capacity2
                else:
                    p_res = re.compile(pattern5).findall(text_orig)
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        capacity1 = str(int(p_res[0]) * int(p_res[1])) + '毫升'
                        capacity2 = p_res[0] + '毫升*' + p_res[1]
                        return capacity1, capacity2
                    else:
                        p_res = re.compile(pattern6).findall(text_orig)
                        if len(p_res) > 0:
                            p_res = p_res[0]
                            capacity1 = str(int(float(p_res[0]) * int(p_res[1]))) + '克'
                            capacity2 = p_res[0] + '克*' + p_res[1]
                            return capacity1, capacity2
                        else:
                            p_res = re.compile(pattern7).findall(text_orig)
                            if len(p_res) > 0:
                                p_res = p_res[0]
                                capacity1 = str(int(int(p_res[0]) * float(p_res[1]))) + '克'
                                capacity2 = p_res[1] + '克*' + p_res[0]
                                return capacity1, capacity2
                            else:
                                p_res = re.compile(pattern8).findall(text_orig)
                                if len(p_res) > 0:
                                    p_res = p_res[0]
                                    capacity1 = str(int(float(p_res[0]) * int(p_res[1]))) + '克'
                                    capacity2 = p_res[0] + '克*' + p_res[1]
                                    return capacity1, capacity2
                                else:
                                    p_res = re.compile(pattern9).findall(text_orig)
                                    if len(p_res) > 0:
                                        p_res = p_res[0]
                                        capacity1 = str(int(float(p_res[0]) * int(p_res[1]))) + '克'
                                        capacity2 = p_res[0] + '克*' + p_res[1]
                                        return capacity1, capacity2
                                    else:
                                        p_res = re.compile(pattern10).findall(text_orig)
                                        if len(p_res) > 0:
                                            p_res = p_res[0]
                                            if p_res[1]=='0':
                                                continue
                                            capacity1 = str(int(float(p_res[0]) * int(p_res[1]))) + '克'
                                            capacity2 = p_res[0] + '克*' + p_res[1]
                                            return capacity1, capacity2
                                        else:
                                            p_res = re.compile(pattern11).findall(text_orig)
                                            if len(p_res) > 0:
                                                p_res = p_res[0]
                                                if p_res[1] == '0':
                                                    continue
                                                capacity1 = str(int(float(p_res[0]) * int(p_res[1]))) + '毫升'
                                                capacity2 = p_res[0] + '毫升*' + p_res[1]
                                                return capacity1, capacity2

    return "不分","不分"

# 提取含有物
def get_content(product_name,texts_list):
    '''
    提取含有物
    :param product_name: 商品全称
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern_1 = "("
    for i in content_list:
        pattern_1 += i + "|"
    pattern_1 = pattern_1[:-1] + ")"

    p_res = get_info_by_pattern(product_name, pattern_1)
    if len(p_res):
        return p_res[0]


    for texts in texts_list:
        txt_orig = ''.join(texts)
        p_res = get_info_by_pattern(txt_orig, pattern_1)
        if len(p_res):
            return p_res[0]
    return '不分'

#提取剂型
def get_dosage(product_name,texts_list):
    '''
    提取剂型
    1、胶囊 产品名称或包装上注明有胶囊字样
    2、丸：产品名称或包装上注明有胶丸、丸字样
    3、水送服片剂   产品名称或包装上注明有片、片剂字样，并且服用方法有水送服字样
    4、含片   产品名称或包装上注明有含片的字样的或服用方法为含服字样的。如有即可水送服也可含服则统一归为含片
    5、咀嚼片 产品名称或包装上注明有咀嚼片的字样的或服用方法为咀嚼字样的。如有即可水送服也可咀嚼则统一归为咀嚼片
    6、口服液  产品名称或包装上注明有口服液字样的或服用方法为口服的
    7、原物形状/原物切片/原物其它状   产品名称或包装上注明多为原物产品的保健品，如此类产品有多种服用方法时以归为此剂型为原物形状/原物切片/原物其它状，花旗参、人参、珍珠、西洋参等多出现此剂型
    8、冲泡类  产品名称或包装上注明有颗粒，或服用法为冲泡字样。如，补血颗粒 ，粉,维D钙冲剂。
    9、泡腾片  产品名称或包装上注明有泡腾片。如，左旋肉碱泡腾片。

    :param product_name: 商品全称
    :param texts_list: 有序文本列表
    :return:
    '''
    if '胶囊' in product_name:
        return '胶囊'
    elif '咀嚼片' in product_name:
        return '咀嚼片'

    elif '泡腾片' in product_name:
        return '泡腾片'
    elif '丸' in product_name:
        return '丸'
    elif '含片' in product_name:
        return '含片'
    elif '人参' in product_name:
        return '原物其它状'
    elif '西洋参' in product_name:
        return '原物切片'
    elif '颗粒' in product_name or '固体饮料' in product_name:
        return '冲泡类'
    elif '口服液' in product_name or '口服溶液' in product_name or '饮' in product_name :
        return '口服液'

    for texts in texts_list:
        text = ''.join(texts)

        if '咀嚼' in text or (('方法' in text or '食用建议' in text) and ('咀' in text or '嚼' in text)):
            return '咀嚼片'
        elif '片' in product_name and  ('方法' in text and ('水送' in text or '口服' in text) or '吞服' in text):
            return '水送服片剂'
        elif '颗粒' in text or '固体饮料' in text or ('方法' in text and '冲' in text):
            return '冲泡类'
        elif ('口服液' in text or '口服溶液' in text) and '片' not in product_name:
            return '口服液'
        elif '泡腾片' in text:
            return '泡腾片'


    for texts in texts_list:
        text = ''.join(texts)
        if '胶囊' in text or '粒' in text and ('规格' in text or '净含量' in text or '每次' in text or '每盒' in text or '方法' in text):
            if '糖果' not in product_name and '片' not in product_name:
                return '胶囊'


        elif '丸' in text and '片' not in product_name:
            return '丸'
        elif '含片' in text or '片'  in product_name and ('方法' in text and '水送服' in text):
            return '含片'

    if '片' in product_name:
        return '咀嚼片'
    return '冲泡类'

#提取主要成份或原料(弃用)
def get_materials_bak(product_name,kvs_list,texts_list):
    '''
    提取主要成份或原料
    :param kvs_list: 文本键值对
    :param texts_list: 有序文本
    :return:
    '''


    result = get_key_Value(kvs_list, ["有效成分","产品成分","主要成分","主要原料","配料表","配科表","配料","配科","料表","原料","原科","料表","成分","成份","装料","辅料","配构"])
    if result!='不分':
        result = re.sub("、|,", "，", result)
        result = re.sub("(|)", "", result)
        if '发明专利' in result or len(result)<=2:
            return '不分'
        if ':' in result:
            result = result.split(':')[1]
        return result

    pattern = '(原料|主要成分|产品成分|主要原料|配料|料表|配料表|原料表|配科|原科|有效成分|料表|成分|成份|辅料|装料|配构)(.+)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res)>0:
                result = p_res[0][1]
                result = re.sub("、|,", "，", result)
                result = re.sub("(|)", "", result)
                if '发明专利' in result or len(result) <= 2:
                    return '不分'
                if ':' in result:
                    result = result.split(':')[1]
                return result
    list1 =['灵芝孢子粉','天然卵磷脂','DHA藻油','枸杞原汁','灵芝孢子','蜂王浆','乳酸菌','西洋参','人参','鱼油']
    for it in list1:
        if it in product_name:
            return it
    return '不分'

#提取产品标识
def get_product_identi(texts_list):
    '''
    提取产品标识
    :param texts_list:有序文本列表
    :return:
    '''
    # 保健食品不是药物
    list1 =[]
    pattern = '保健食品|OTC'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res)>0 :
                if 'OTC' == text:
                    return 'OTC'
                if text=='保健食品':
                    list1.append(text)
    if len(list1)>0:
        return '小蓝帽小蓝帽+国食健字'
    return '无标识'


def category_rule_196(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    content = '不分'
    dosage = '不分'
    function ='不分'
    #适用人群
    suitpeople = '不分'
    materials ='不分'
    product_identi = '不分'


    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], [], [])
        brand_1 = re.sub("全组健愿", "全组健康", brand_1)
        brand_1 = re.sub("维果品", "维果命", brand_1)
        brand_1 = re.sub("南板人", "南极人", brand_1)
        brand_1 = re.sub("无阻熊", "无限能", brand_1)
        brand_1 = re.sub("峰之屋", "蜂之屋", brand_1)
        brand_1 = re.sub("·", "", brand_1)

    # # product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)

    if product_name != '不分' and brand_1 != '不分' and brand_1.title() in product_name.title():
        product_name = product_name.title().replace(brand_1.title(), '')
    product_name = re.sub("^牌", "", product_name)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "ml|毫升|mL|L|kg|ML|升|g|克", "包袋盒瓶", 0)
    if capcity_1=='不分':
        capcity_1, capcity_2 = get_Capacity(datasorted)
    if capcity_2 == '不分':
        capcity_0,capcity_2 = get_Capacity_2(datasorted)
        if capcity_1 =='不分':
            capcity_1 = capcity_0
    content = get_content(product_name, datasorted)
    dosage = get_dosage(product_name, datasorted)
    function = get_function(dataprocessed, datasorted)
    suitpeople = get_suitpeople(product_name,dataprocessed, datasorted)
    suitpeople = suitpeople.replace('、', '，').replace(',', '，').replace('。', '')
    # materials = get_materials(product_name,dataprocessed,datasorted)
    # print(materials)
    # print('\n')
    materials = get_ingredients(dataprocessed, datasorted, Ingredients_list)
    materials = re.sub("配料表:|配料:|保持了原:|配科:|,\d+|\d+克", "", materials)
    if materials == '0' or len(materials) < 2:
        materials = '不分'

    # print(materials)
    product_identi = get_product_identi(datasorted)
    # 含有物
    result_dict['info1'] = content
    # 剂型
    result_dict['info2'] = dosage
    # 功能c
    result_dict['info3'] = function
    # 适合人群
    result_dict['info4'] = suitpeople
    # 主要成份或原料
    result_dict['info5'] = materials
    # 产品标识
    result_dict['info6'] = product_identi
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])
    real_use_num = 6
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\196-包装饮用水'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3124131"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_196(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)