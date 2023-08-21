import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/161_brand_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/161_taste_list",encoding="utf-8").readlines())]

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

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

def get_productName_voting(kvs_list,texts_list):
    pattern_absort = "^[越低酥稀标友海M蓝]|^美味|干燥|[图照]片|[凉晾]干|产品类型|工艺|^\w?冻干片$"
    result_list = []
    result_list_tmp = []

    pattern_1 = "(\w+肉[干脯丝条棒粒脆纸卷片]+|\w+肉乾|\w+干[肉巴]|\w+鸡丁|\w*香酥肉|\w+牛肉粒?|\w+薯片|\w*辣子鸡|\w*爆五花|\w+鲜香牛肉)($|\()"
    pattern_2 = "\w+\(\w+味\)$"
    pattern_3 = "(\w+肉[干脯丝条棒粒脆纸卷片]+|\w+肉乾|\w+干[肉巴]|\w+鸡丁|\w*香酥肉|\w*辣子鸡|\w+鲜香牛肉)"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("[肉干脯丝条棒粒牛猪鸡脆]").findall(kv[k])) > 0:
                        result_list.append(kv[k])
                    elif len(kv[k]) > 1:
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
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(p_res[0])) ==0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(p_res[0])) ==0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(p_res[0])) ==0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    return count[0][0]

def get_series(texts_list):
    pattern = "^\w{2,4}系列"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                return p_res[0]
    return "不分"

def get_type(texts_list,product_name):
    '''
    种类规则：
    1.肉脆：脆、肉纸、纸肉、薯片
    2.肉脯：肉脯
    3.肉干：肉干、肉乾、风干、肉棒、肉条、肉粒、粒粒、肉丝、肉片
    '''
    type_cui = ["脆","肉纸","纸肉","薯片"]
    type_pu = ["肉脯"]
    type_gan = ["肉干","肉乾","风干","肉棒","肉条","肉粒","粒粒","肉丝","肉片"]

    if "脆" in product_name or "薯片" in product_name:
        return "肉脆"

    pattern = "肉[干棒条粒丝脯纸片]|风干|粒粒|纸肉|肉乾|脆"
    p_res = get_info_by_pattern(product_name,pattern)
    if len(p_res) > 0:
        if p_res[0] in type_pu:
            return "肉脯"
        elif p_res[0] in type_gan:
            return "肉干"
        elif p_res[0] in type_cui:
            return "肉脆"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                if p_res[0] in type_pu:
                    return "肉脯"
                elif p_res[0] in type_gan:
                    return "肉干"
                elif p_res[0] in type_cui:
                    return "肉脆"

    return "不分"

def get_inside(texts_list):
    '''
    配料规则：只抄肉类的描述，若配料里有含肉量百分比，也要抄一下
    '''
    pattern_absort = "^[香种选含]"
    pattern = "[猪牛羊鸡鸭]\w?肉糜?|\w*猪里脊肉|\w*小?黄鱼|\w*龙头鱼干?|\w*鲳鱼"
    result = []
    for texts in texts_list:
        for text in texts:
            if "温馨提示" in text or "肉末粉" in text or "肉味粉" in text or "也加工" in text or "鸡肉粉" in text or "车间" in text or "小茴香" in text or "猪肉粉" in text or "食用葡萄糖" in text or "内味粉" in text or "肉抽提物" in text\
                    or "闪抽" in text or "鸡肉、海藻糖" in text or "辣猪肉鸡肉" in text or "食品用者" in text or "麦美粉" in text or "海蒸糖" in text:
                break
            index = 0
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                for p_r in p_res:
                    if "羊牛肉" in p_r or "鸡腿肉" in p_r or "牛黄鱼" in p_r or "鸡肉提取物" in p_r:
                        break
                    if p_r not in result:
                        result.append(p_r)
                    index += 1
            if index > 1:
                result = mySorted(result, text)
    result_sorted = sorted(result, key=len)
    res = []
    if len(result_sorted) > 0:
        for index, i in enumerate(result_sorted):
            flag = True
            for j in result_sorted[index + 1:]:
                if i in j:
                    flag = False
            if flag:
                res.append(i)
    res = sorted(res, key=result.index)
    if len(res) > 0 :
        return "，".join(res)
    return "不分"

def get_shape(texts_list, product_name):
    '''
    形状规则：
    1.棒/条：包装上有”棒”、”条”字样，或者形状是棒和条状的
    2.粒/块：包装上有”粒”、”丁”字样，或者形状是粒状或块状
    3.片：包装上有”片”字样，或者形状是扁片的
    4.卷：全称有“卷”字，或形状是卷状
    5.丝：全称有”丝”字样，或者形状是丝状的
    6.其它：请注明。比如不规则形状或几种形状组合

    7.※：当前规则无其它，如不符合上述规则，给出“片”
    '''
    pattern_1 = "肉脯|肉纸|肉片|肉脆"
    pattern_2 = "肉棒|肉条"
    pattern_3 = "肉丁|肉块|肉粒|粒粒"

    pattern = "肉[脯纸片脆]|肉[棒条]|肉[丁块粒]|粒粒"
    if "丝" in product_name or "干巴" in product_name:
        return "丝"
    elif "卷" in product_name:
        return "卷"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if p_res[0] in pattern_1:
                    return "片"
                elif p_res[0] in pattern_3:
                    return "粒、块"
                elif p_res[0] in pattern_2:
                    return "棒、条"
    return "片"

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    Taste_list_PLUS = Taste_list.copy()
    result = get_info_list_by_list([[product_name,],], Taste_list)
    for taste in Taste_list:
        if "味" not in taste:
            Taste_list_PLUS.append(taste + "味")
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0 and p_res[0] not in ["口味","新口味"]:
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
        return "".join(result)

def get_type_2(kvs_list):
    result_list = []
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品类" in k or k in ["类型","严晶美型","类别"]):
                    if len(kv[k]) > 1 :
                        result_list.append(kv[k])
    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return "不分"

def get_health(texts_list):
    res = get_info_list_by_list(texts_list,["低脂","零脂","高蛋白"])
    if len(res) > 0:
        return "，".join(res)

    return "不分"


def get_package_161(base64strs):
    '''
    调用服务提取包装信息
    规则：自封袋、袋装、塑料瓶/桶、铁盒/桶、纸盒/礼盒、其它(请注明)
    :param base64strs:图片列表
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

    if "自封袋" in result_shape:
        return "自封袋装"

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if material == "纸":
        material = "纸"
    elif material == "铁":
        material = "铁"
    else:
        material = "塑料"

    if shape in ["盒", "托盘"]:
        shape = "盒"

    result = material + shape
    if '袋' in result:
        return '袋装'
    elif '塑料瓶' in result:
        return '塑料瓶、桶'
    elif '铁盒' in result:
        return '铁盒、桶'
    elif '纸盒' in result:
        return '纸盒、礼盒'
    return result

def category_rule_161(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    series = "不分"
    type_1 = "不分"
    inside = "不分"
    shape = "不分"
    taste = "不分"
    package = "不分"
    package_type = "不分"
    health = "不分"
    type_2 = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    #品牌
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,[],["a1","A1","OLE","牛先生","好味来","回味","KEEP","酥小","爱鸭","无穷"],[])

    brand_1 = re.sub("肉味小贝","肉球小贝",brand_1)
    brand_1 = re.sub("多滋子味","多滋多味",brand_1)
    brand_1 = re.sub("富甲方","富甲一方",brand_1)
    brand_1 = re.sub("包日香","包日查",brand_1)
    brand_1 = re.sub("体闲列车","休闲列车",brand_1)
    brand_1 = re.sub("生家岭","牛家岭",brand_1)
    brand_1 = re.sub("川公味","川幺妹",brand_1)
    brand_1 = re.sub("小Q思","小Q崽",brand_1)
    brand_1 = re.sub("达克松鼎","达克松鼠",brand_1)
    brand_1 = re.sub("迪克松鼠","达克松鼠",brand_1)
    brand_1 = re.sub("人人芯","人人艾",brand_1)
    brand_1 = re.sub("三阳可具","三阳可其",brand_1)
    brand_1 = re.sub("休麻列车","休闲列车",brand_1)
    brand_1 = re.sub("鲜力美","鲜亦美",brand_1)
    brand_1 = re.sub("酥小", "酥小槑", brand_1)


    #商品全称
    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("丰撕","手撕",product_name)
    product_name = re.sub("肉[脑腹]","肉脯",product_name)
    product_name = re.sub("五誉味","五香味",product_name)
    product_name = re.sub("沙[嗜咚爹]味","沙嗲味",product_name)
    product_name = re.sub("托牛肉","牦牛肉",product_name)
    product_name = re.sub("食辣", "香辣", product_name)
    product_name = re.sub("肉素", "肉条", product_name)

    product_name = re.sub("质量等级\W?\w级$", "", product_name)
    product_name = re.sub("^\w*名称", "", product_name)
    product_name = re.sub("^\w*品名", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    #重容量
    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐", 0)

    #系列
    series = get_series(datasorted)
    #种类
    type_1 = get_type(datasorted, product_name)
    #配料
    inside = get_inside(datasorted)
    if inside == "猪肉，猪瘦肉": inside = "猪肉"
    if inside == "鸡肉，鸡胸肉": inside = "鸡肉"

    inside = re.sub("猪疼肉","猪瘦肉",inside)

    #形状
    shape = get_shape(datasorted, product_name)

    #口味
    taste = get_taste(datasorted, product_name)

    taste = re.sub("沙[修哮]味","沙嗲味",taste)

    # 包装
    package = get_package_161(base64strs)

    #独立装
    if capcity_2 != "不分":
        package_type = "独立装"
    else:
        package_type = "非独立装"
    #健康概念
    health = get_health(datasorted)
    #类型
    type_2 = get_type_2(dataprocessed)

    type_2 = re.sub("热肉","熟肉",type_2)
    type_2 = re.sub("牛肉[桌魔]干","牛肉糜干",type_2)

    result_dict['info1'] = series
    result_dict['info2'] = type_1
    result_dict['info3'] = inside
    result_dict['info4'] = shape
    result_dict['info5'] = taste
    result_dict['info6'] = package
    result_dict['info7'] = package_type
    result_dict['info8'] = health
    result_dict['info9'] = type_2
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    real_use_num = 9
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    pass