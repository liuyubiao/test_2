import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/131_brand_list",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/131_type_list",encoding="utf-8").readlines())]
Type_list.sort(key=len,reverse=True)
Taste_list = [i.strip() for i in set(open("Labels/131_taste_list",encoding="utf-8").readlines())]


# 通常来看需要20个非通用属性
LIMIT_NUM = 20

PRELIST = ["陈佳","糯米","糯米精酿","纯粮","金标","典藏","精酿","纯酿"]

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    result = get_info_list_by_list([[product_name,],], Taste_list)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0:
            Flag = True
            if p_res[0] in Taste_Abort_List_pres:
                Flag = False
            if Flag:
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
        return "".join(result)

def get_type(texts_list,product_name):
    type_1 = "不分"
    type_2 = "不分"
    for t in Type_list:
        if t in product_name:
            type_1 = t
            break

    if type_1 == "不分":
        if "牛肉" in product_name:
            type_1 = "牛肉酱"
        elif "鸡肉" in product_name:
            type_1 = "鸡肉酱"
        elif "海鲜" in product_name:
            type_1 = "海鲜酱"
        elif "虾" in product_name:
            type_1 = "虾酱"
        elif "朝天椒" in product_name or "指天椒" in product_name:
            type_1 = "指天，朝天椒辣酱"
        elif "郫县" in product_name:
            type_1 = "郫县豆酱"
        elif "豉" in product_name:
            type_1 = "豆瓣酱"
            type_2 = "豆豉"
        elif "豆瓣" in product_name:
            type_1 = "豆瓣酱"
            type_2 = "豆酱"
        elif "味噌" in product_name:
            type_2 = "味噌"
        elif "甜酱" in product_name:
            type_1 = "甜面酱"
        elif "辣" in product_name and "辣白菜" not in product_name:
            type_1 = "辣椒酱，辣酱"

    if type_1 == "不分":
        res_list = get_info_list_by_list_taste(texts_list,Type_list)
        if len(res_list) > 0:
            count = Counter(res_list).most_common(2)
            type_1 =  count[0][0]

    if "辣" in type_1 and "辣白菜" not in product_name:
        type_2 = "辣椒酱"
    elif "豆" in type_1:
        type_2 = "豆酱"
    elif "面" in type_1:
        type_2 = "面酱"
    elif "汁" in product_name:
        type_2 = "其他酱"

    if type_2 == "不分":
        type_2 = "复合调味酱"

    if type_1 in ["辣椒酱","辣酱"]:
        type_1 = "辣椒酱，辣酱"
    elif type_1 in ["指天椒辣酱","朝天椒辣酱"]:
        type_1 = "指天，朝天椒辣酱"
    elif type_1 in ["黄酱","大豆酱"]:
        type_1 = "大豆酱"
    elif type_1 in ["拌饭酱","拌面酱"]:
        type_1 = "拌饭，面酱"
    elif type_1 in ["油泼辣"]:
        type_1 = "油辣椒"
    elif type_1 in ["豆豉"]:
        type_1 = "豆瓣酱"
    elif type_1 in ["虾仁酱"]:
        type_1 = "虾酱"
    elif type_1 in ["韭花酱"]:
        type_1 = "韭菜花酱"

    if type_1 == "不分" or type_1 in ["蟹黄酱"]:
        type_1 = "其它复合酱"

    return type_1,type_2


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

def get_productName_bak(texts_list):
    for texts in texts_list:
        if "酱" in texts:
            for index, text in enumerate(texts):
                if index > 6 :
                    break
                if text == "酱":
                    str_list = ["酱"]
                    for i in [-1, -2 , -3 ]:
                        if index + i >= 0:
                            if len(texts[index + i]) == 1:
                                str_list.append(texts[index + i])

                    if len(str_list) > 1:
                        str_list.reverse()
                        return "".join(str_list)
                    else:
                        if index -1 >= 0 and len(texts[index-1]) < 6:
                            return texts[index-1] + "酱"
    return "不分"

def get_productName_voting(kvs_list,texts_list):
    pattern_text = "干燥|产品类型|工艺|专研|精选|^配料"
    pattern_pres = "^半固态|^美味|香辣$|炒菜|扫码"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+[^好\W]酱|\w+酱豆|\w+罐头|\w+[剁辣][椒子]|\w+小米辣|\w+朝天椒|\w+指天椒|\w+山椒|\w+豆[豉鼓]|\w+[肉鸡][丁丝]|\w+卤汁|\w*白勺汁|\w*蒸鱼宝|\w+火锅底料|\w+香辣脆|\w+大拌汁|\w+火锅蘸料)($|\()"
    pattern_2 = "\w+\(\复合调味料\)"
    pattern_3 = "(\w+佐料|\w+调味[品料]|\w+调料|\w+芽菜|\w+菜腊肉|\w*辣子鸡|\w*特辣王|\w*蒜香王|\w+干煸肉丝|\w+脆萝卜|\w+豆瓣)($|\()"
    pattern_4 = "\w+[^好\W]酱|\w+菜$"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("酱|罐头|辣|椒|卤汁|豆[豉鼓]|[肉鸡][丁丝]").findall(kv[k])) > 0:
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
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(text)) ==0 and len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
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
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(text)) ==0 and len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
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
                p_res = p_res[0]
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(text)) ==0 and len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0] and count[0][1] == 1:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(text)) ==0 and len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        product_name_bak = get_productName_bak(texts_list)
        if product_name_bak != "不分":
            return product_name_bak
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0] and count[0][1] == 1:
        return count[1][0]
    return count[0][0]

def get_gene(texts_list):
    key = "转基因"
    flag = -1
    for texts in texts_list:
        text = "".join(texts)
        if key in text:
            if "非" not in text and "丰转" not in text :
                flag = "1"
            else:
                return "非转基因"
    if flag == "1":
        return "转基因"

    return "不分"

def get_no_add(texts_list):
    no_add_list = ["无添加","不含防腐剂","不含色素","不含香精","不含甜味剂","不含增味剂","0脂","0添加","零添加"]
    res = get_info_list_by_list(texts_list,no_add_list)
    if len(res) > 0:
        count = Counter(res).most_common(2)
        return count[0][0]
    return "不分"

def get_inside(texts_list):
    inside_list =["香菇","鸭肠","蒜蓉","牛肉","丁香鱼","海鲜","鸡肉","菌菇","野山椒","果蔬","黄豆","五仁","鱼仔","扇贝","番茄","虾肉","鸡丁","猪肉","孜然","竹笋","鱼肉","花生","香蒜","鲜椒","菠萝","茶油","腊肉","笋干","肉丁","萝卜","蔬菜","水果","蟹黄","坚果","燕麦"]
    res = get_info_list_by_list_taste(texts_list, inside_list)
    if len(res) > 0:
        return ",".join(res)
    return "不分"

def category_rule_131(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    type_1 = "不分"
    type_2 = "不分"
    taste = "不分"
    series = "不分"
    package = "不分"
    gene = "不分"
    inside = "不分"
    no_add = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,["至美",],["北大荒","会吃","利民","美味佳"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("么有黔", "辣么有黔", brand_1)
    brand_1 = re.sub("心大缘厨", "心缘大厨", brand_1)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|毫升|ML|ml|mL", "瓶包袋罐", 2)

    # datasorted = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("味噜", "味噌", product_name)
    product_name = re.sub("豆鼓", "豆豉", product_name)
    product_name = re.sub("[刹利刺别]辣[椒假]", "剁辣椒", product_name)
    product_name = re.sub("[刹利刺别]椒", "剁椒", product_name)
    product_name = re.sub("舒黄", "蟹黄", product_name)
    product_name = re.sub("蒜著", "蒜蓉", product_name)
    product_name = re.sub("调味汗", "调味汁", product_name)
    product_name = re.sub("非花", "韭花", product_name)


    product_name = re.sub("[产食]品名[称种]", "", product_name)
    product_name = re.sub("^\w?\W", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    if len(re.compile("菜腊肉$|辣子鸡$|特辣王$|蒜香王$|干煸肉丝$").findall(product_name)) > 0:
        product_name += "复合调味料"

    type_1, type_2 = get_type(datasorted, product_name)

    taste = get_taste(datasorted, product_name)
    gene = get_gene(datasorted)
    no_add = get_no_add(datasorted)
    inside = get_inside(datasorted)

    name_pre = ""
    name_pre_1 = get_info_item_by_list(datasorted, ["无添加", "0添加", "零添加"])
    name_pre_2 = get_info_item_by_list(datasorted, ["微辣", "中辣", "重辣"])

    if name_pre_1 in product_name:
        name_pre_1 = "不分"
    if name_pre_2 in product_name or len(re.compile("[香麻甜]辣").findall(product_name)) > 0:
        name_pre_2 = "不分"
    if name_pre_1 != "不分": name_pre += name_pre_1
    if name_pre_2 != "不分": name_pre += name_pre_2

    product_name = name_pre + product_name

    package = get_package_131(base64strs)

    result_dict['info1'] = series
    result_dict['info2'] = type_2
    result_dict['info3'] = type_1
    result_dict['info4'] = taste
    result_dict['info5'] = package
    result_dict['info6'] = gene
    result_dict['info7'] = inside
    result_dict['info8'] = no_add
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
    root_path = r'D:\Data\商品识别\stage_2\149-速冻食品'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3039104"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_131(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)