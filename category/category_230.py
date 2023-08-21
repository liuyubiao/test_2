import os
import re
import json

from util import *
from utilCapacity import get_capacity
from glob import glob

LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/230_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/230_brand_list_2",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/230_taste_list",encoding="utf-8").readlines())]

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")

def get_keyValue(kvs_list,keys):
    result_list = []
    for kvs in kvs_list:
        for kv in kvs:
            for key in keys:
                for k in kv.keys():
                    if len(key) == 1:
                        if key == k:
                            result_list.append(kv[k])
                    else:
                        if key in k and  len(k) < 6 and len(kv[k]) > 1:
                            result_list.append(kv[k])

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) >1 and count[0][1] == count[1][1] and len(count[0][0]) < len(count[1][0]) and len(re.compile("[0-9,，、]").findall(count[1][0])) == 0:
        return count[1][0]
    else:
        return count[0][0]

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    Taste_list_PLUS = Taste_list.copy()
    for taste in Taste_list:
        if "味" not in taste:
            Taste_list_PLUS.append(taste + "味")
    result = get_info_list_by_list_taste([[product_name, ], ], Taste_list_PLUS)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0 and p_res[0] not in ["口味", "新口味", "老广州风味","乳味","左旋肉碱风味","含汽风味","风味"]:
            Flag = True
            for i in Taste_Abort_List:
                if i in p_res[0]:
                    Flag = False
                    break
            if Flag:
                result.append(p_res[0])

    if len(result) == 0:
        return get_taste_normal(texts_list, Taste_list)
    else:
        result = list(set(result))
        dejoy = ","
        return dejoy.join(result)

#碳水化合物
def get_carbon(kvs_list,texts_list):
    protein_key = "营养成分表-碳水化合物"
    p = re.compile(r'(\d+\.?\d*)\s?(G|g|克)')
    for kvs in kvs_list:
        for kv in kvs:
            if protein_key in kv.keys():
                if len(p.findall(kv[protein_key])) > 0:
                    if float(p.findall(kv[protein_key])[0][0]) == 0.0:
                        return "无"
                    else:
                        return "有"

    return "不分"

def get_suger(texts_list):
    '''
    1）不含蔗糖：包装上有“0蔗糖”、“不含蔗糖”、“无蔗糖”、“蔗糖为零”字样；
    2）不含糖：包装上有“0糖”、“零糖”、“不含糖”、“糖分是0”、“无糖”、“Zero sugar”、“No sugar”、“Free of sugar”、“Sugar free”、“Unsweetened”字样；
    3）不添加糖：包装上有“0添加糖”、“0添加蔗糖”、“不或无(添)加食糖”、“不或无(添)加糖”、“不或无(添)加白(砂)糖”、“不或无(添)加蔗糖”、“无加糖”、“No Added Sugar”字样
    4）低糖：产品名称或包装上注明描述低糖的字样，或名称中有描述含糖量低的字样，如“少甜”、“微糖”、“超微糖”；
    5）木糖醇：产品名称或包装上注明描述木糖醇的字样；
    6）低聚糖：产品名称或包装上注明描述低聚糖的字样；
    7）不含蔗糖，木糖醇：包装上有“木糖醇”字样且不含蔗糖
    8）不含糖，木糖醇：包装上有“木糖醇”字样且不含糖
    9）不添加糖，木糖醇：包装上有“木糖醇”字样且不添加糖
    10）其他：包装上有“不添加糖精”、“冰糖”、“白砂糖”字样，或者是未注明
    :param texts_list:
    :return:
    '''
    result_zhesugar = []
    result_nosugar = []
    result_addsugar = []
    result_merge = []

    pattern = "0蔗糖|不含蔗糖|无蔗糖|蔗糖为零|零蔗糖"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "不含蔗糖"
                result_zhesugar.append("不含蔗糖")

    pattern = "[0O口零无]糖|不含糖|糖分是0|Zero sugar|No sugar|Free of sugar|ugar free|Unsweetened|OSUGAR|ZEROSUGAR"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "不含糖"
                result_nosugar.append("不含糖")

    pattern = "0添加糖|0添加蔗糖|不或无(添)加食糖|不或无(添)加糖|不或无(添)加白(砂)糖|不或无(添)加蔗糖|无加糖|No Added Sugar"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "不添加糖"
                result_addsugar.append("不添加糖")

    pattern = "木糖醇"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "木糖醇"
                result_merge.append("木糖醇")

    """
    规则【根据规则表顺序进行判断，但组合内容的判断优先级最高：
    1.优先处理组合内容：“不含蔗糖，木糖醇”、“不含糖，木糖醇”、“不添加糖，木糖醇”---------将不含蔗糖、不含糖、不添加糖的结果放在不同的list表中，分别与木糖醇搭配，如两者均有结果-返回
    2.其次处理单个内容：“不含蔗糖”、“不含糖”、“不添加糖”--------分别判断不同的list表中是否有值，如有值-返回
    3.其他内容顺序依次往下
    """
    #【不含蔗糖,木糖醇】组合判断规则
    if len(result_zhesugar) > 0 and len(result_merge) > 0:
        count = Counter(result_zhesugar).most_common(2)
        zhesugar = count[0][0]
        count = Counter(result_merge).most_common(2)
        mumerge = count[0][0]
        if zhesugar == "不含蔗糖" and mumerge == "木糖醇":
            return zhesugar + "," + mumerge

    #【不含糖,木糖醇】组合判断规则
    if len(result_nosugar) > 0 and len(result_merge) > 0:
        count = Counter(result_nosugar).most_common(2)
        nosugar = count[0][0]
        count = Counter(result_merge).most_common(2)
        mumerge = count[0][0]
        if nosugar == "不含糖" and mumerge == "木糖醇":
            return nosugar + "," + mumerge

    #【不添加糖,木糖醇】组合判断规则
    if len(result_addsugar) > 0 and len(result_merge) > 0:
        count =Counter(result_addsugar).most_common(2)
        addsugar = count[0][0]
        count = Counter(result_merge).most_common(2)
        mumerge = count[0][0]
        if addsugar == "不添加糖" and mumerge == "木糖醇":
            return addsugar + "," + mumerge

    #【不含蔗糖】单个内容判断
    if len(result_zhesugar) > 0:
        count = Counter(result_zhesugar).most_common(2)
        zhesugar = count[0][0]
        return zhesugar

    #【不含糖】单个内容判断
    if len(result_nosugar) > 0:
        count = Counter(result_nosugar).most_common(2)
        nosugar = count[0][0]
        return nosugar

    # 【不添加糖】单个内容判断
    if len(result_addsugar) > 0:
        count = Counter(result_addsugar).most_common(2)
        addsugar = count[0][0]
        return addsugar

    ##【木糖醇】单个内容判断
    if len(result_merge) > 0:
        count = Counter(result_merge).most_common(2)
        mumerge = count[0][0]
        return mumerge

    pattern = "少甜|微糖|超微糖|低糖|低[蔗燕]糖"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "低糖"


    pattern = "低聚糖"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "不添加糖精|冰糖|白砂糖"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "其他"

    return "其他"

def get_type(texts_list):
    '''
    1.无汽(气)苏打水：包装上同时出现“无汽(气)”和“苏打”字样，或者配料里不含“二氧化碳”
    2.有汽(气)苏打水：包装上有“苏打”字样，且配料表里出现“二氧化碳”字样
    3.格瓦斯/Kvass：包装上出现“格瓦”、“格瓦斯”字样
    4.汤力水：包装上出现“汤力水”字样
    5.干姜水：包装上出现“干姜水”字样
    6.可乐/Cola：包装上出现“可乐”字样
    7.其他/Others：包装上没有出现以上描述
    :param texts_list:
    :return:
    '''
    result_hava = []
    result_nohava = []
    result_suda = []
    result_co2 = []

    #查找所有结果中是否包含“有气|有汽”字段内容，存入list中
    pattern = "有气|有汽"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "有汽(气)苏打水"
                result_hava.append("有汽(气)苏打水")

    # 查找所有结果中是否包含"无汽|无气"字段内容，存入list中
    pattern = "无汽|无气"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "无汽(气)苏打水"
                result_nohava.append("无汽(气)苏打水")

    # 查找所有结果中是否包含"苏打"字段内容，存入list中
    pattern = "苏打"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "有汽(气)气泡水"
                result_suda.append("苏打")

    # 查找所有结果中是否包含"二氧化碳"字段内容，存入list中
    pattern = "二氧化[碳酸酰校碱]?|氧化[碳酸酰校碱]"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "有汽(气)气泡水"
                result_co2.append("二氧化碳")

    #字段内容包含“无气”and“苏打"，返回结果
    if len(result_nohava) > 0 and len(result_suda) > 0 :
        return "无汽(气)苏打水"
    #字段内容有“二氧化碳”，返回结果
    if len(result_co2) == 0 and len(result_suda) > 0:
        return "无汽(气)苏打水"

    #字段内容有“苏打”and“二氧化碳”，返回结果
    if len(result_suda) > 0 and len(result_co2) > 0:
        return "有汽(气)苏打水"

    pattern = "格瓦|格瓦斯|Kvass"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "格瓦斯"

    pattern = "汤力水"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "干姜水|姜汁"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "干姜水"

    return "其他"

def get_productName(kvs_list,texts_list):
    pattern_absort = "的|^[儿盐升子型天味的酸应产]|^果汁|^\d|^\d+[毫mM][升lL]|[胜碳肤品虹乐]饮料|[和为倍十真]果汁|[彩L深北塑热]汽水|名$"
    pattern_text = "委托单位|生产|企业|公司|集团|[、·，,]"
    pattern0 = "(\w*果然有气|\w*有橙意|\w*虎气满满|\w*苏打の清爽|\w*有橙意|\w*大窑开卫|\w*北冷|\w*青金橘味|\w*满分|\w*舒达源|\w*有汽派|\w*荔枝珍品|\w*大白梨?|\w*风梨|\w*柠檬苏打|\w*超有范|\w*乐亨可乐|\w*酵素" \
               "|\w*气士|\w*轻透小[檬桃]|\w*橙诺|\w*原味苏打|\w*水肌泉|\w*1906|\w*摩登罐|\w*水晶葡萄|\w*益生菌|\w*美年达|\w*蜜莓苏打|\w*野刺梨|\w*左旋肉碱|\w*此奶有汽|\w*大室开卫|\w*迷你罐|\w*老长沙|\w*气元)$"
    pattern1 = "(\w+饮料|\w+汽水|\w+气泡水|\w*苏打水|\w+气泡饮品?|\w+格瓦斯|\w+果汁|\w+碳酸水|\w+葡萄汁|\w*香槟|\w+饮品|\w*菠萝啤)$"
    pattern2 = "\w+饮料|\w+汽水|\w+气泡水|\w+苏打水|\w+气泡饮品?|\w+格瓦斯|\w+果汁|\w+碳酸水"
    pattern3 = "(\w*冰棍|\w*菠萝啤?味|\w*乳酸菌味|\w*女士嘉槟|\w*[百事|盒马]可乐)$"

    result_list = []
    result_list_front = []
    result_list_tmp = []

    pattern_tmp = "汽水|饮料|苏打水|气泡水|冰棍|气泡饮品|果汁|葡萄汁"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern0)
            if len(p_res) > 0 and p_res[0] not in result_list and len(p_res[0]) > 1:
                result_list_front.append(p_res[0])
            # if len(p_res) > 0:
            #
            #     p_res = p_res[0]
            #     if "的" not in p_res[0] and len(re.compile("[、，,]").findall(text)) == 0 and len(
            #             re.compile(pattern_absort).findall(text)) == 0:
            #         result_list.append(p_res[0])

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in [ "名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile(pattern_text).findall(kv[k])) ==0 and len(re.compile(pattern_tmp).findall(kv[k])) > 0:
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
            p_res = get_info_by_pattern(text, pattern1)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list_front) > 0:
        count_front = Counter(result_list_front).most_common(2)
        if len(result_list) > 0:
            count = Counter(result_list).most_common(2)
            if count_front[0][0] in count[0][0] :
                return count[0][0]
            else:
                return count_front[0][0] + count[0][0]

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern2)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list_front) > 0:
        count_front = Counter(result_list_front).most_common(2)
        if len(result_list) > 0:
            count = Counter(result_list).most_common(2)
            if count_front[0][0] in count[0][0]:
                return count[0][0]
            else:
                return count_front[0][0] + count[0][0]

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern3)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list_front) > 0:
        count_front = Counter(result_list_front).most_common(2)
        if len(result_list) > 0:
            count = Counter(result_list).most_common(2)
            if count_front[0][0] in count[0][0]:
                return count[0][0] + "汽水"
            else:
                return count_front[0][0] + count[0][0]+ "汽水"

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0] + "汽水"

    return product_name_tmp

def get_brand_list(texts_list: object,Brand_list_1,Brand_list_2,keyWords,abortWords,num = 2) -> object:
    brand_1_tmp_list = []
    brand_1_txt_list = []
    brand_1_merge_tmp_list = []
    brand_1_merge_list = []
    brand_1_merge_absort_list = []
    brand_2 = []
    for texts in texts_list:
        # text_str = TextFormatNormal(texts)
        text_str = "".join(texts)
        text_str_ori = ",".join(texts)
        for bb in Brand_list_1:
            if bb in text_str:
                if len(bb) > 1:
                    brand_1_merge_tmp_list.append(bb)
                elif len(re.compile("(,|^)%s($|,)" % (",".join(list(bb)))).findall(text_str_ori)) > 0:
                    brand_1_merge_tmp_list.append(bb)
        for text in texts:
            if text in keyWords:
                brand_1_txt_list.append(text)
            for b1 in Brand_list_1:
                if b1.upper() in text.upper() or b1 in text:
                    if b1 == text and b1 not in abortWords:
                        brand_1_txt_list.append(text)
                    if len(b1) > num or (len(re.compile("[市省镇区村县请勿]|大道|街道").findall(text)) == 0 and "地址" not in text):
                        brand_1_tmp_list.append(b1)
                    else:
                        brand_1_merge_absort_list.append(b1)

        for b2 in Brand_list_2:
            if b2 in texts:
                brand_2.append(b2)

    if len(brand_2) > 0:
        brand_2 = ",".join(list(set(brand_2)))
    else:
        brand_2 = "不分"

    for bm in brand_1_merge_tmp_list:
        if bm not in brand_1_tmp_list:
            brand_1_merge_list.append(bm)

    # wll修改位置：2023-3-28 17:21:33
    if len(brand_1_merge_tmp_list) > 0:
        count = Counter(brand_1_merge_tmp_list).most_common(1)
        brand_1 = count[0][0]
        if brand_1 not in brand_1_merge_absort_list:
            return brand_1, brand_2

    # if len(brand_1_tmp_list) > 0:
    #     count = Counter(brand_1_tmp_list).most_common(1)
    #     brand_1 = count[0][0]
    #     if brand_1 not in brand_1_merge_absort_list:
    #         return brand_1, brand_2

    if len(brand_1_txt_list) > 0:
        brand_1_tmp_list.sort(key=len, reverse=True)
        count = Counter(brand_1_txt_list).most_common(1)
        brand_1 = count[0][0]
    else:
        brand_1_list = []
        for i in brand_1_tmp_list:
            flag = True
            for j in brand_1_tmp_list:
                if j != i and i in j:
                    flag = False
                    break
            if flag:
                brand_1_list.append(i)

        if len(brand_1_list) == 0:
            brand_1 = "不分"
        else:
            brand_1_list.sort(key=len, reverse=True)
            count = Counter(brand_1_list).most_common(1)
            brand_1 = count[0][0]
    return brand_1, brand_2

def get_package_230(base64strs):
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

    if "玻璃底" in result_material:
        return "玻璃瓶"
    elif "塑料底" in result_material:
        return "塑料瓶"

    if material == "玻璃":
        return "玻璃瓶"
    elif "塑料" in material:
        return "塑料瓶"
    elif material == "金属":
        if shape == "瓶":
            return "铝瓶"
        elif shape == "细长罐":
            return "细长听"

        return "听装"

    return "塑料瓶"

def category_rule_230(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    taste = "不分"
    package = "不分"
    suger = "不分"
    carbon = "不分"
    type = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,[],["INM","AHA","ZER","ZERO","BOT","丰之源","RIO","握握手","AJI","ASIA","科维","ALCA"],[])

    brand_1 = re.sub("园范小汽","范小汽",brand_1)
    brand_1 = re.sub("起嘿吧|一起黑吧", "一起嘿吧", brand_1)
    brand_1 = re.sub("热着", "执着", brand_1)
    brand_1 = re.sub("EDOrack", "EDOPACK", brand_1)
    brand_1 = re.sub("梨水", "黎水", brand_1)
    brand_1 = re.sub("FAINXIAUDI", "FANXIAOQI", brand_1)

    #商品全称
    if product_name == "不分":
        product_name = get_productName(dataprocessed,datasorted)

    product_name = re.sub("老水冰棍","老冰棍",product_name)
    product_name = re.sub("风梨","凤梨",product_name)
    product_name = re.sub("苞萄","葡萄",product_name)
    product_name = re.sub("大室开卫","大窑开卫",product_name)
    product_name = re.sub("柠[樽榨]","柠檬",product_name)
    product_name = re.sub("腰味", "橙味", product_name)
    product_name = re.sub("[磁炭]酸饮料", "碳酸饮料", product_name)
    product_name = re.sub("气元", "气π", product_name)
    product_name = re.sub("鲜橙蘸露", "鲜橙囍露", product_name)
    product_name = re.sub("[^\)\w]$","",product_name)

    #重容量
    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "ml|毫[升元开]|mL|L|[升元开]|ML", "袋盒桶罐瓶", 1)

    capcity_2 = re.sub("[元开]", "升", capcity_2)
    capcity_1 = re.sub("[元开]", "升", capcity_1)

    #子类型
    if "可乐" in product_name : type = "可乐"
    if "格瓦斯" in product_name : type = "格瓦斯"
    if type == "不分" :
        type = get_type(datasorted)

    suger = get_suger(datasorted)

    if carbon == "不分" :
        if suger == "不含糖" or suger == "不含蔗糖":
            carbon = "无"
        else:
            carbon = "有"

    #口味
    taste = get_taste(datasorted,product_name)

    taste = re.sub("风梨","凤梨",taste)
    taste = re.sub("美汁","姜汁",taste)

    package = get_package_230(base64strs)

    result_dict['info1'] = taste
    result_dict['info2'] = package
    result_dict['info3'] = suger
    result_dict['info4'] = carbon
    result_dict['info5'] = type
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\230-碳酸饮料_格瓦斯'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3054812"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_230(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)