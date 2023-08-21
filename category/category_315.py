import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/315_brand_list",encoding="utf-8").readlines())]
Brand_list_3 = [i.strip() for i in set(open("Labels/315_brand_list_3",encoding="utf-8").readlines())]
Inside_list = [i.strip() for i in set(open("Labels/315_inside_list",encoding="utf-8").readlines())]
Effect_list = [i.strip() for i in set(open("Labels/315_effect_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/315_taste_list",encoding="utf-8").readlines())]
# 通常来看需要20个非通用属性
LIMIT_NUM = 20

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
    pattern_text = "[、，,]"
    pattern_pres = "的"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w{2,}[洗丽][发髪]香?[水露乳液泡膏]|\w{2,}洗护液|\w{2,}沐浴[露乳液])($|\()"
    pattern_2 = "(\w+[洗丽][发髪][水露乳液泡膏]|\w+洗护液|\w+沐浴[露乳液]|\w+喷雾$|\w+洗头水$)"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("[水露乳液泡雾]").findall(kv[k])) > 0:
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
        if len(count) > 1 and count[0][0] in count[1][0] and count[0][1] == 1:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0] and count[0][1] == 1:
        return count[1][0]
    return count[0][0]

def get_siliconeoil(texts_list):
    key_list_1 = ["无硅油","不添加硅油","零添加硅油"]

    res = get_info_list_by_list(texts_list,key_list_1)
    if len(res) > 0:
        return "无硅油"
    return "不分"

def get_touxie(texts_list):
    for texts in texts_list:
        for text in texts:
            if "去屑" in text or "去头屑" in text or "祛屑" in text or "祛头屑" in text:
                return "去头屑"

    return "非去头屑"

def get_union(texts_list):
    for texts in texts_list:
        for text in texts:
            if "二合一" in text:
                return "二合一"
            elif "三合一" in text:
                return "三合一"

    return "非二合一"

def get_inside(texts_list):
    res = get_info_list_by_list(texts_list,Inside_list)
    # pattern = "蕴含(.+精华|.+萃取成分)($|\W)"
    # res_list = []
    # for texts in texts_list:
    #     for text in texts:
    #         p_res = get_info_by_pattern(text,pattern)
    #         if len(p_res) > 0:
    #             p_res = p_res[0]
    #             res_list.append(p_res[0])

    res_pattern = "不分"
    # if len(res_list) > 0:
    #     count = Counter(res_list).most_common(2)
    #     res_pattern = count[0][0]

    if len(res) > 0:
        if res_pattern != "不分":
            tmp_res = []
            for r in res:
                if r not in res_pattern:
                    tmp_res.append(r)
            tmp_res.append(res_pattern)
            return "，".join(tmp_res)
        else:
            return "，".join(res)
    else:
        return "不分"

def get_effect(texts_list,product_name):
    res = get_info_list_by_list([[product_name,],], Effect_list)
    if len(res) == 0:
        res = get_info_list_by_list(texts_list, Effect_list)
        for key in ["清","洁","净","润","养","滋","顺","爽"]:
            key_list = []
            for r in res:
                if key in r:
                    key_list.append(r)

            if len(key_list) > 1:
                key_list.sort(key=len)
                for k in key_list[:-1]:
                    res.remove(k)
    if len(res) > 0:
        return "，".join(res)
    else:
        return "不分"

def get_hairquality(texts_list):
    problem_list = ["干枯","毛糙","毛躁","粗糙","分叉","受损","脆弱","暗哑","易断","多种发质","各种发质"]
    res = get_info_list_by_list(texts_list, problem_list)

    pattern = "针对([\w,，、]{2,}发质)"
    if len(res) == 0:
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text,pattern)
                if len(p_res) >0:
                    return p_res[0]

        return "不分"
    else:
        return "，".join(res) + "发质"


def get_people(texts_list,product_name):
    people_list = ["男士","儿童","婴儿"]
    for p in people_list:
        if p in product_name:
            return p

    pattern_pres = "可能|极少|[合用]人群$"
    pattern = "[\w,，、]+人群|适合\w+者|[\w,，、]+人士[适適]用"
    res_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                res_list.append(p_res[0])

    if len(res_list) > 0:
        count = Counter(res_list).most_common(2)
        return count[0][0]
    else:
        return "不分"

def get_taste(texts_list,product_name):
    result = get_info_list_by_list([[product_name,],], Taste_list)
    if len(result) == 0:
        result = get_info_list_by_list(texts_list,Taste_list)

    if len(result) == 0:
        return "不分"
    else:
        return "".join(result)

def category_rule_315(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    touxie = "不分"
    union = "不分"
    inside = "不分"
    effect = "不分"
    hairquality = "不分"
    people = "不分"
    taste = "不分"
    siliconeoil = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, ["玖耀壹琉"], Brand_list_3, [])

    brand_1 = re.sub("Rejoice","飘柔Rejoice",brand_1)
    brand_1 = re.sub("海偏仙度丝", "海伦仙度丝", brand_1)
    brand_1 = re.sub("Davines", "大卫尼斯", brand_1, re.IGNORECASE)

    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "g|克|ml|毫[升开元]|mL|L|[升开元]|ML", "瓶包袋罐", 1)

    capcity_2 = re.sub("毫[开元]", "毫升", capcity_2)
    capcity_1 = re.sub("毫[开元]", "毫升", capcity_1)

    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("^\w洗发水", "洗发水", product_name)
    product_name = re.sub("^\w洗发乳", "洗发乳", product_name)

    product_name = re.sub("祛[展网]", "祛屑", product_name)
    product_name = re.sub("去[展网]", "去屑", product_name)
    product_name = re.sub("头[展网]", "头屑", product_name)

    product_name = re.sub("亮迁", "亮莊", product_name)

    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    touxie = get_touxie(datasorted)
    union = get_union(datasorted)
    inside = get_inside(datasorted)
    effect = get_effect(datasorted, product_name)
    hairquality = get_hairquality(datasorted)
    people = get_people(datasorted, product_name)
    taste = get_taste(datasorted, product_name)
    siliconeoil = get_siliconeoil(datasorted)

    result_dict['info1'] = touxie
    result_dict['info2'] = union
    result_dict['info3'] = inside
    result_dict['info4'] = effect
    result_dict['info5'] = hairquality
    result_dict['info6'] = people
    result_dict['info7'] = taste
    result_dict['info8'] = siliconeoil
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 8
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    pass