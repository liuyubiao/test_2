import os
import re
from util import *
from utilCapacity import get_capacity

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

Brand_list_1 = [i.strip() for i in set(open("Labels/316_brand_list",encoding="utf-8").readlines())]
Brand_list_3 = [i.strip() for i in set(open("Labels/316_brand_list_3",encoding="utf-8").readlines())]
Effect_list = [i.strip() for i in set(open("Labels/316_effect_list",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/316_type_list",encoding="utf-8").readlines())]

def get_type(texts_list,product_name):
    pattern = "("
    for i in Type_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"

    p_res = get_info_by_pattern(product_name,pattern)
    if len(p_res) > 0:
        return p_res[-1]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "护发素"

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
    pattern_0 = "(\w{2,}护发[素乳霜]|\w+[^护\W]护?发膜)$"
    pattern_1 = "(\w{2,}精油|\w{2,}[顺健焕靓养润浸]发[素乳霜液]{1,2}|\w{2,}精华[液乳素霜]|\w{2,}修[饰护养][液乳素蜜霜]|\w{2,}蛋白[素霜乳]|\w{2,}调理乳?[液霜]|\w{2,}营养姜?[水液泥]|\w{2,}修护精华|\w{2,}喷雾|"
    for t in Type_list:
        if "[" in t or "?" in t or t == "发膜":
            continue
        pattern_1 += "\w{2,}" + t + "|"
    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_0[:-2] + "|" + pattern_1[1:-1]
    pattern_3 = "^("
    for t in Type_list:
        if t == "发膜":
            continue
        pattern_3 += t + "|"
    pattern_3 = pattern_3[:-1] + ")$"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("[液露乳膏膜泥油雾]").findall(kv[k])) > 0:
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
            p_res = get_info_by_pattern(text, pattern_0)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0] and count[0][1] == 1:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
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

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0] and count[0][1] == 1:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0] and count[0][1] == 1:
        return count[1][0]
    return count[0][0]

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
        count = Counter(brand_1_list).most_common(10)
        brand_1 = ",".join([i[0] for i in count])
    return brand_1,brand_2

def get_effect(texts_list,product_name):
    Effect_list_product_name = Effect_list.copy()
    Effect_list_product_name.extend(["香氛","养发","护理","润发"])
    res = get_info_list_by_list([[product_name,],], Effect_list)
    if "养发膜" in product_name and "养发" in res:
        res.pop("养发")
    if "润发膜" in product_name and "润发" in res:
        res.pop("润发")

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
    problem_list = ["干枯","干涩","毛糙","毛躁","枯黄","粗糙","分叉","受损","脆弱","暗哑","无光泽","打结","易断","干燥发质","多种发质","各种发质","任何发质"]
    res = get_info_list_by_list(texts_list, problem_list)

    if "多种发质" in res:
        res = ["多种发质"]
    elif "各种发质" in res:
        res = ["各种发质"]
    elif "任何发质" in res:
        res = ["任何发质"]
    res = [re.sub("发质","",i) for i in res]

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

def get_heat(texts_list):
    key_list = ["加热"]
    for texts in texts_list:
        for text in texts:
            for k in key_list:
                if k in text and "无" not in text and "不" not in text and "更" not in text:
                    return "需加热"

    return "免蒸"

def get_wash(texts_list,type):
    key_list = ["不需冲洗","免冲洗","免洗"]
    for texts in texts_list:
        for text in texts:
            for k in key_list:
                if k in text :
                    return "免洗"

    if type in ["精油","还原霜","修复丝油","精华液","按摩油"]:
        return "免洗"

    return "冲洗"

def category_rule_316(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    heat = "不分"
    wash = "不分"
    effect = "不分"
    hairquality = "不分"
    type = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,[],Brand_list_3,[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("峨山龍归","岷山龍归",brand_1)
    brand_1 = re.sub("Davines", "大卫尼斯", brand_1,re.IGNORECASE)
    brand_1 = re.sub("Quin[co]oll", "轻欧Quincoll", brand_1, re.IGNORECASE)
    brand_1 = re.sub("HINMEISHI", "馫魅诗", brand_1, re.IGNORECASE)
    brand_1 = re.sub("一生花","三生花",brand_1)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "g|克|ml|毫[升开元]|mL|L|[升开元]|ML", "瓶包袋罐", 1)

    capcity_2 = re.sub("毫[开元]", "毫升", capcity_2)
    capcity_1 = re.sub("毫[开元]", "毫升", capcity_1)

    # datasorted = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("香氰", "香氛", product_name)
    product_name = re.sub("莱莉", "茉莉", product_name)
    product_name = re.sub("香藻", "香薰", product_name)

    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    type = get_type(datasorted, product_name)
    heat = get_heat(datasorted)
    wash = get_wash(datasorted,type)
    effect = get_effect(datasorted,product_name)
    hairquality = get_hairquality(datasorted)

    result_dict['info1'] = heat
    result_dict['info2'] = wash
    result_dict['info3'] = effect
    result_dict['info4'] = hairquality
    result_dict['info5'] = type
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 5
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    pass