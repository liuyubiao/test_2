import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity
LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/191_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/191_brand_list_2",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/191_type_list",encoding="utf-8").readlines())]
Place_list = [i.strip() for i in set(open("Labels/191_place_list",encoding="utf-8").readlines())]
#商品名称全称正则表达式关键词列表
suffix_name_list = [i.strip() for i in set(open("Labels/191_suffix_name_list",encoding="utf-8").readlines())]
#主要配料成分正则表达式关键词列表
mixture_list = [i.strip() for i in set(open("Labels/191_mixture_list",encoding="utf-8").readlines())]

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")

#提取面粉等级
def get_level(texts_list,kvs_list):
    '''提取面粉等级
    提取依据：191定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、包装上明确有特制一等，一级，精制，一等，标准粉，普通粉
    1、特制一等/一级/精制/一等/标准粉/普通粉/其它（未注明）/其它
    :param texts_list: 有序文本列表
    :param kvs_list: 键值对
    :return:
    '''
    abort_list =['研磨','加工','合伙']
    result_list = []
    # pattern = "[特精]?制?[一二三四特][级等]"
    pattern = "[特精]?制?一[级等]"
    result = ''
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result_list.append(p_res[0])

    if len(result_list) > 0:
        result_list.sort(key=len,reverse=True)
        count = Counter(result_list).most_common(2)
        result = count[0][0]
    if len(result) == 0:
        pattern = "普通|精制"
        for texts in texts_list:
            for text in texts:
                flag = True
                for it in abort_list:
                    if it in text:
                        flag = False
                        break
                if flag:
                    p_res = get_info_by_pattern(text, pattern)
                    if len(p_res) > 0 and '加工' not in text:
                        result = p_res[0]
    if len(result) == 0:
        for kvs in kvs_list:
            for kv in kvs:
                for k in kv.keys():
                    if "等级" in k or '质量等纸' in k:
                        if len(kv[k]) > 1:
                            flag = True
                            for it in abort_list:
                                if it in kv[k]:
                                    flag = False
                                    break
                            if flag:
                                result = kv[k]
    if len(result)>0:
        if result in ['特制一等','一等','精制','普通','一级'] :
            return result
        elif result == '特制一' or result == '制一等' or result == '特一等':
            result = '特制一等'
        elif result == '1级':
            result = '一级'
        elif result == '精刷级' or result == '精制级':
            result = '精制'
        elif result == '标准粉':
            level = '标准粉'
        elif result == '合格品' or result == '合格':
            result = '其它（未注明）'
        else:
            result = '其它'
        return result
    return "其它（未注明）"

#提取面粉原料产地
def get_place(texts_list,placeOrigin):
    '''
    提取面粉原料产地
        提取依据：191定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：根据
    1、抄录原料产地信息如“加大拿小麦”“美国小麦”“黑龙江麦”等，正面全称或大字会有原料产地信息，或包装侧面或背面有相关的原料产地信息
    2、加麦/美麦/澳麦/黑龙江麦/山东麦/河南麦/江苏麦/河北麦/山西麦/安徽麦/湖北麦/四川麦/陕西麦/未注明/其它
    3、外国麦，用外国名第一个字加“麦”，例如：加大拿小麦 ：加麦；美国小麦：美麦
    4、国内小麦，用省名加“麦”，例如：山东麦、新疆麦、内蒙古麦等
    :param texts_list:
    :return:
    '''
    pattern_foreign_country = "俄罗斯|韩国|比利时|日本|哈萨克斯坦|巴西|美国|加拿大|澳大利亚"

    pattern_china = "("
    for i in Place_list:
        pattern_china += i + "|"
    pattern_china = pattern_china[:-1] + ")"

    # 优先外国
    if placeOrigin!='不分':
        p_res = get_info_by_pattern(placeOrigin, pattern_foreign_country)
        if len(p_res) > 0:
            # 取国家名第一个字+麦
            return p_res[0][0] + '麦'
        else:
            p_res = get_info_by_pattern(placeOrigin, pattern_china)
            if len(p_res) > 0:
                return p_res[0] + '麦'

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_foreign_country)
            if len(p_res) > 0:
                # 取国家名第一个字+麦
                p = p_res[0][0]+'麦'
                return p


    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_china)
            if len(p_res) > 0:
                return p_res[0]+'麦'
    return "不分"

#提取面粉用途
def get_usage(texts_list,product_name):
    '''
    提取面粉用途
    提取依据：191定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：首先根据全称判断是否为馒头用小麦粉、
    1、从全称正面大字判断是否有“面包、面条、饺子、馒头、饼干、蛋糕”用粉和“自发粉”信息
    2、通用小麦粉/传统面食用粉（面条、饺子、馒头、油饼等多种用途）/面包用小麦粉/面条用小麦粉/饺子用小麦粉/馒头用小麦粉/
    饼干用小麦粉/蛋糕用小麦粉/糕点用小麦粉/自发用小麦粉/西点用小麦粉（面包、蛋糕、饼干、曲奇、蛋挞等多种用途）/其它
    3、通用小麦粉：全称中没有用途关键字的，在产品正面，背面的产品说明处找相关描述。哪里都没有说明的
    4、传统面食用粉：面条、饺子、馒头、花卷、、包子、烙饼、油饼等多种用途
    5、全称与产品描述冲突时以正面全称为准
    :param texts_list: 有序文本
    :param product_name: 商品全称
    '''
    #首先根据全称判断是否包含馒头、面条、面包、蛋糕、糕点等用小麦粉，如果包含馒头，那么为：馒头用小麦粉，其他类似
    usage_list = ['馒头','饺子','面包','蛋糕','糕点']
    for it in usage_list:
        if it in product_name:
            return it + '用小麦粉'
    #其次根据全称判断是否包含自发，如果包含，那么为：自发用小麦粉
    if '自发' in product_name:
        return "自发用小麦粉"

    # 然后根据整体描述文本判断，是否为传统面食用粉（面条、饺子，馒头，花卷，包子，烙饼，油饼）或者 西点用小麦粉(面包、蛋糕、糕点、饼干、曲奇、蛋挞、奶酪、泡芙)
    usage_list_chuantong = ['面条','饺子','馒头','花卷','包子','烙饼','油饼']
    usage_list_xidian = ['面包','蛋糕','糕点','饼干','曲奇','蛋挞','奶酪','泡芙']
    chuantong_show = "传统面食用粉（面条、饺子、馒头、油饼等多种用途）"
    xidian_show = "西点用小麦粉（面包、蛋糕、饼干、曲奇、蛋挞等多种用途）"
    result_list_chuantong = []
    result_list_xidian = []
    for texts in texts_list:
        for text in texts:
            for it in usage_list_chuantong:
                if it in text:
                    if it not in result_list_chuantong:
                        result_list_chuantong.append(it)
            for it in usage_list_xidian:
                if it in text:
                    if it not in result_list_xidian:
                        result_list_xidian.append(it)
    if len(result_list_chuantong)>0:
        if len(result_list_chuantong)>1:
            # result = '传统面食用粉（'+ '、'.join(result_list_chuantong)+'等多种用途）'
            result = chuantong_show
        else:
            if result_list_chuantong[0]=='馒头' or result_list_chuantong[0]=='饺子':
                result = result_list_chuantong[0]+'用小麦粉'
            else:
                # result = '传统面食用粉（'+ result_list_chuantong[0]+'等多种用途）'
                result = chuantong_show
        return result

    if len(result_list_xidian)>0:
        if len(result_list_xidian)>1:
            result = xidian_show
            # result = '西点用小麦粉（'+ '、'.join(result_list_xidian)+'等多种用途））'
        else:
            if result_list_xidian[0]=='蛋糕' or result_list_xidian[0]=='糕点' or result_list_xidian[0]=='面包':
                result = result_list_xidian[0]+'用小麦粉'
            else:
                result = xidian_show
                # result = '西点用小麦粉（'+ result_list_xidian[0]+'等多种用途）'
        return result


    usage_list = ["自发"]
    result_type = get_info_item_by_list(texts_list, usage_list)
    if result_type != "不分":
        return "自发用小麦粉"

    # 哪里都没有说明的
    return "通用小麦粉"

#提取面粉的蛋白质信息
def get_Nutrition(kvs_list):
    '''
    提取面粉的蛋白质信息
    提取依据：191定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、抄录包装中“营养成分表”中的蛋白质含量（每100克含量），只填写数字。如果不是每100克含量要注明多少单位的含量
    2、蛋白质的写法：统一保留小数点后一位，如9写为9.0
    :param kvs_list: 文本键值对
    :return:
    '''
    protein = "不分"
    protein_key = "营养成分表-蛋白质"
    p_1 = re.compile(r'(\d+\.?\d*)\s?(G|g|克)')
    result_list = []
    for kvs in kvs_list:
        for kv in kvs:
            if protein_key in kv.keys():
                p_res_1 = p_1.findall(kv[protein_key])
                if len(p_res_1) > 0:
                    if float(p_res_1[0][0]) > 1000:
                        protein = str(float(p_res_1[0][0]) / 100.0)
                        result_list.append(protein)
                    elif float(p_res_1[0][0]) > 100:
                        protein = str(float(p_res_1[0][0]) / 10.0)
                        result_list.append(protein)
                    else:
                        protein = p_res_1[0][0]
                        result_list.append(protein)
    if len(result_list)>0:
        count = Counter(result_list).most_common(2)
        if len(count)==1:
            protein = count[0][0]
        elif len(count)==2:
            # 如果存在两个，取数值小的
            if float(count[0][0])<float(count[1][0]):
                protein = count[0][0]
        if '.' in protein:
            protein = protein[0:protein.find('.') + 2]
    else:
        protein = '不分'
    return protein

def get_organic(texts_list):
    key = "有机"
    flag = -1
    for texts in texts_list:
        for text in texts:
            if key in text:
                if "非" not in text:
                    flag = 1
                else:
                    return "非有机"
    if flag == 1:
        return "有机"
    return "非有机"

def get_mill(texts_list):
    key = "石磨"
    flag = -1
    for texts in texts_list:
        for text in texts:
            if key in text:
                if "非" not in text:
                    flag = 1
                else:
                    return "非石磨"
    if flag == 1:
        return "石磨"
    return "非石磨"

# 提取面粉的配料成分
def get_ingredients(kvs_list,texts_list):
    '''
    提取面粉的配料成分
    提取依据：191定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、抄录配料表中的信息，只抄录主要配料成分和酵母，如小麦，玉米，燕麦，大豆，紫薯，玉米淀粉，酵母等。食品添加剂不抄录。例如：小麦粉/玉米面粉/荞麦面粉/南瓜面粉/添加多种杂粮
    2、把测试数据中主要配料成分数据汇总到列表（去重），作为查询的依据
    3、首先在文本键值对列表，查询料表信息，如果存在，则获取配料信息，同时同配料关键词列表进行匹配
    4、其次，如果在文本键值对列表没有获取相关信息，则在有序文本列表中和配料关键词列表进行匹配
    :param kvs_list: 文本键值对
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern = r'\w*料表?$'
    result = "不分"

    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    if result == "不分":
                        result = kv[k]

    if result == "不分" or len(result) <= 1:
        tmp_result = ['小麦粉']
        for texts in texts_list:
            for text in texts:
                for t in mixture_list:
                    if t in text and t not in tmp_result:
                        tmp_result.append(t)

        if len(tmp_result) > 0:
            result = "，".join(tmp_result)
    else:
        tmp_result = ['小麦粉']
        if '、' in result:
            ts = result.split('、')
            for t in ts:
                if t in mixture_list and t not in tmp_result:
                    tmp_result.append(t)
            result ="，".join(tmp_result)
        elif result not in mixture_list:
            result = ''
    if len(result)>0:
        result = re.sub('、', "，", result)
        result = re.sub('饮用水', "", result)
        result = re.sub('水', "", result)
        result = re.sub('小麦雪', "小麦粉", result)
        result = re.sub('小麦名称', "小麦粉", result)
        result = re.sub('优质冬小麦', "小麦粉", result)

        result = re.sub('优质小麦', "小麦粉", result)
        result = re.sub('小麦，', "小麦粉", result)
        result = re.sub('强筋小麦', "小麦粉", result)
        result = re.sub('黑小麦', "小麦粉", result)
        if result == '小麦':
            result = '小麦粉'
    else:
        result = '小麦粉'

    return result

#提取面粉筋度
def get_type(texts_list):
    '''
    提取依据：191定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、从全称和正面大字判断:高筋面粉/中筋面粉/低筋面粉/其它
    2、产品名称没有明确说明“高、中、低筋”字样为“其它”
    :param texts_list:
    :return:
    '''
    pattern = "("
    for i in Type_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if len(p_res[0]) == 2:
                    p_res[0] = p_res[0] + '面粉'
                # if p_res[0]=='高筋':
                #     p_res[0] = '高筋面粉'
                # elif p_res[0]=='中筋':
                #     p_res[0] = '中筋面粉'
                # elif p_res[0]=='低筋':
                #     p_res[0] = '低筋面粉'
                return p_res[0]
    return "其它"

#提取商品全称
def get_productName_voting(texts_list):
    result_list = []
    abort_list = ['类型','美型','类别','加','大米粉','做好','公司','地区','配料','从','研','必备']
    pre_result_list = []
    pattern_1 = "("
    for i in suffix_name_list:
        pattern_1 += "\w+" + i + "|"
        # 麦芯粉(小麦粉预拌粉)
        # pattern_1 += "\w *\(?\w+" + i + "\)?|"

    # \w *\(\w+预拌粉\)
    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1.replace("+", "*")[:-1]

    pattern_3 = "\w+[粉|面]$"
    pattern_4 = "\w+粉"


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
        if len(pre_result_list)>0:
            return pre_result_list[0]
        result_list.sort(key=len,reverse=True)
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
        if len(pre_result_list)>0:
            return pre_result_list[0]
        result_list.sort(key=len,reverse=True)
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
                if len(p_res) > 0 and '的' not in p_res[0]:
                    result_list.append(p_res[0])
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        if len(pre_result_list)>0:
            return pre_result_list[0]
        result_list.sort(key=len,reverse=True)
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
                p_res = get_info_by_pattern(text, pattern_4)
                if len(p_res) > 0 and '的' not in p_res[0]:
                    result_list.append(p_res[0])
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])
                    continue

    if len(result_list) == 0:
        return "不分"
    if len(pre_result_list) > 0:
        return pre_result_list[0]
    count = Counter(result_list).most_common(2)
    return count[0][0]

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

def get_package_191_unit(base64strs):
    url = url_classify + ':5040/yourget_opn_classify'

    task = MyThread(get_url_result, args=(base64strs, url,))
    task.start()
    # 获取执行结果
    result = task.get_result()

    if len(result) == 0:
        return "覆膜袋"

    res = Counter(result).most_common(1)[0][0]
    if res in ["纸袋","塑料袋","编织袋","无纺布袋","纸盒"]:
        pass
    else:
        res = "覆膜袋"

    return res

def category_rule_191(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    type = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    level = "不分"
    usage = "不分"
    ingredients = "不分"
    protein = "不分"
    package = "不分"
    organic = "不分"
    mill = "不分"
    placeOrigin = "不分"
    jindu = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], [], [])
    #测试用，暴露更多的品牌，过滤刷选用
    # brand_1_test, brand_2_test = get_brand_list_test(datasorted)

    # product_name = get_keyValue(dataprocessed, ["品名"])
    # if "粉" not in product_name and "面" not in product_name:
    #     product_name = "不分"
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)
        if product_name!='不分' and brand_1!='不分' and brand_1.title() in product_name.title():
            product_name = product_name.title().replace(brand_1.title(),'')
        product_name = re.sub('\W', "", product_name)

    # 原料产地
    placeOrigin = get_keyValue(dataprocessed, ["产地"])
    placeOrigin = get_place(datasorted,placeOrigin)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒", 0)

    #筋度
    if type == "不分":
        type= get_type(datasorted)

    #等级
    if level == "不分":
        level = get_level(datasorted,dataprocessed)
    #用途
    if usage =="不分":
        usage = get_usage(datasorted,product_name)


    # 主要配料成分（包括酵母）
    ingredients = get_ingredients(dataprocessed,datasorted)

    # 蛋白质
    if protein == "不分":
        protein = get_Nutrition(dataprocessed)

    # 有机/非有机
    if organic == "不分":
        organic = get_organic(datasorted)
    # 石磨/非石磨
    if mill == "不分":
        mill = get_mill(datasorted)

    # 外包装形式
    package = get_package_191_unit(base64strs)

    result_dict['info1'] = level
    result_dict['info2'] = type
    result_dict['info3'] = usage
    result_dict['info4'] = ingredients
    result_dict['info5'] = protein
    result_dict['info6'] = package
    result_dict['info7'] = organic
    result_dict['info8'] = mill
    result_dict['info9'] = placeOrigin
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])
    result_dict["info9"] = re.sub("[、,，：:：·]", "", result_dict["info9"])
    result_dict["info4"] = re.sub("^[、，：:：·]", "", result_dict["info4"])
    real_use_num = 9
    #测试用
    # result_dict['info10'] = brand_1_test
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    # for k in result_dict.keys():
    #     if k == "info9":
    #         continue
    #     result_dict[k] = re.sub("[,，：:]", "", result_dict[k])

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_2\191-面粉'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3063528"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_191(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)