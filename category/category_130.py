import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/130_brand_list",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/130_type_list",encoding="utf-8").readlines())]
Type_list.sort(key=len,reverse=True)
Series_list = [i.strip() for i in set(open("Labels/130_series_list",encoding="utf-8").readlines())]


# 通常来看需要20个非通用属性
LIMIT_NUM = 20

PRELIST = ["陈佳","糯米","糯米精酿","纯粮","金标","典藏","精酿","纯酿"]

def productNameFormat(texts_list,product_name,name_list):
    for texts in texts_list:
        total_len = len(texts)
        for index, text in enumerate(texts):
            if text == product_name:
                for i in [-1,-2,1,2]:
                    if index + i >= 0 and index + i < total_len:
                        if texts[index + i] in name_list and texts[index + i] not in product_name:
                            return texts[index + i] + product_name
    return product_name

def get_type(texts_list,product_name):
    type_1 = "不分"
    type_2 = "不分"
    type_0 = "不分"
    for t in Type_list:
        if t in product_name:
            type_0 = t
            break
    if type_0 == "不分":
        for t in Type_list:
            t = t.replace("醋","酿")
            if t in product_name:
                type_0 = t
                break
        type_0 = type_0.replace("酿","醋")

    if type_0 in ["保健醋","益肠醋","核苷酸醋","康乐醋"]:
        type_1 = "其它醋"
        type_2 = "保健醋"
    elif type_0 in ["海鲜醋","蒸鱼醋","烹鱼醋","蟹醋","蛰头醋"]:
        type_1 = "其它醋"
        type_2 = "海鲜醋"
    elif type_0 in ["陈醋"] and "小米" in product_name:
        type_1 = "陈醋"
        type_2 = "小米陈醋"
    elif type_0 in ["陈酿"]:
        type_1 = "陈醋"
        type_2 = "陈酿醋"
    elif type_0 in ["老陈醋","老醋"]:
        type_1 = "陈醋"
        type_2 = type_0
    elif type_0 in ["陈醋"]:
        type_1 = "陈醋"
        type_2 = "普通陈醋"
    elif type_0 in ["大红浙醋","大红浙酿","红醋","浙醋","玫瑰米醋","玫瑰醋"]:
        type_1 = "米醋"
        type_2 = "大红浙醋"
    elif type_0 == "白醋":
        type_1 = "白醋"
        type_2 = "普通白醋"
    elif type_0 == "黑醋":
        type_1 = "米醋"
        type_2 = "黑米醋"
    elif type_0 in ["白米醋","黑米醋","高梁醋","糯米醋","小米醋"]:
        type_1 = "米醋"
        type_2 = type_0
    elif type_0 == "米醋":
        type_1 = "米醋"
        type_2 = "普通米醋"
    elif type_0 in ["甜醋","蜜醋"]:
        type_1 = "甜醋"
        type_2 = "普通甜醋"
    elif type_0 == "香醋" or "宴会" in product_name:
        type_1 = "香醋"
        type_2 = "普通香醋"
    elif type_0 in ["果醋","苹果醋", "柿子醋", "葡萄醋", "柠檬醋", "梨醋","香脂醋","摩德纳醋","沙棘醋","柚子醋"]:
        type_1 = "非饮料果醋"
        type_2 = type_0
    elif type_0 in ["饺子醋", "面条醋", "拌面醋", "寿司醋"]:
        type_1 = "其它醋"
        type_2 = type_0

    if type_0 == "不分":
        if "食醋" in product_name or product_name == "醋":
            type_1 = "普通醋"
            type_2 = "普通醋"
        elif "晒醋" in product_name or "二醋" in product_name:
            type_1 = "普通醋"
            type_2 = "晒醋"
        elif "醋" in product_name or "酿" in product_name:
            type_1 = "其它醋"
            type_2 = "其它醋"
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

def get_productName_voting(kvs_list,texts_list):
    pattern_text = "[、，,]|干燥|产品类型|工艺|专研|精选"
    pattern_pres = "^半固态|^美味|香辣$"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w*[白陈陳米红黑香老甜蟹晒]醋|\w*大红浙[醋酿]|\w*高梁醋|\w+饺子醋|\w+醋汁|\w+[^年\W][陳陈]酿|\w+醋王)($|\()"
    pattern_2 = "\w*大红浙[醋酿]|\w*高梁醋|\w+饺子醋|\w+醋汁"
    pattern_3 = "(\w+[^好\W]醋|^醋|\w+调味汁)($|\()"
    pattern_4 = "\w+[^好\W]醋"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("[醋]").findall(kv[k])) > 0:
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
                if "的" not in p_res[0] and len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 and p_res[0] != "酿造食醋":
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
                if "的" not in p_res[0] and len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 and p_res[0] != "酿造食醋":
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
                if "的" not in p_res[0] and len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 and p_res[0] != "酿造食醋":
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
                if "的" not in p_res[0] and len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0] and count[0][1] == 1:
        return count[1][0]
    return count[0][0]

def get_method(texts_list):
    key_list_1 = ["酿造","发酵"]
    key_list_2 = ["配制","调味食醋","风味","冰乙酸","复合调味料"]
    # res = get_info_list_by_list_taste(texts_list,key_list_1)
    # if len(res) > 0:
    #     return "酿造醋"

    res = get_info_list_by_list(texts_list, key_list_2)
    if len(res) > 0:
        return "配制醋"

    return "酿造醋"

def get_series(texts_list,product_name):
    key_list_1 = ["黑糯米","糯米精酿","特制纯粮","宴会","金标","添丁","纯酿","头道","精酿","典藏","原浆","糯米","特曲","典藏","窖酿"]
    key_list_2 = ["陈酿","纯粮"]

    for texts in texts_list:
        if product_name in texts:
            for text in texts:
                if text == product_name:
                    continue
                if text in Series_list and text not in product_name:
                    return text

    res = get_info_list_by_list([[product_name, ], ], Series_list)
    if len(res) > 0:
        return "".join(res)

    res = get_info_list_by_list_taste(texts_list,key_list_1)
    if len(res) > 0:
        count = Counter(res).most_common(2)
        return count[0][0]

    res = get_info_list_by_list([[product_name,],],key_list_2)
    if len(res) > 0:
        return "".join(res)
    return "不分"

def get_degree(kvs_list,texts_list):
    pattern = "(\d[度C])($|\w+醋)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and len(re.compile("\dC$").findall(text)) == 0:
                p_res = p_res[0]
                return p_res[0]

    result = get_keyValue(kvs_list, ["酸度"])
    try:
        result = re.compile("\d+").findall(result)[0]
    except:
        result = "不分"

    return result

def get_year(texts_list):
    pattern = "([一二三四五六七八九十]|十[一二三四五六七八九]|\d+)年[陈酿造]+"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if len(p_res[0]) < 3:
                    return p_res[0] + "年"
    return "不分"

def category_rule_130(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    type_1 = "不分"
    type_2 = "不分"
    year = "不分"
    package = "不分"
    method = "不分"
    degree = "不分"
    series = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,["镇江陈醋",],["美味佳","CUCU","家调","华夏","清泉","太源井"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "g|克|ml|毫[升开元]|mL|L|[升开元]|ML", "瓶包袋罐", 1)

    # datasorted = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("邂", "㶍", product_name)
    product_name = re.sub("棘汁", "蒜汁", product_name)
    product_name = re.sub("日醋", "白醋", product_name)
    product_name = re.sub("酸造", "酿造", product_name)
    product_name = re.sub("[酸酿]造食\)", "酿造食醋)", product_name)

    product_name = re.sub("[产食]品名[称种]", "", product_name)
    product_name = re.sub("^品?名?一", "", product_name)

    product_name = re.sub("^\w?\W", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    degree_tmp = re.compile("\D*(\d)\D+").findall(product_name)
    if len(degree_tmp) > 0:
        product_name = re.sub(degree_tmp[0] + "[度C]?", degree_tmp[0] + "度", product_name)
        degree = degree_tmp[0] + "度"

    type_1, type_2 = get_type(datasorted, product_name)

    year = get_year(datasorted)
    method = get_method(datasorted)
    series = get_series(datasorted, product_name)
    if degree == "不分":
        degree = get_degree(dataprocessed, datasorted)

    if product_name == "醋":
        product_name = productNameFormat(datasorted, product_name, ["白", "蟹", "米", "香", "陈", "陳"])
    if len(product_name) <= 3 and product_name != "不分":
        product_name = productNameFormat(datasorted, product_name, PRELIST)
    if len(product_name) <= 3 and product_name != "不分" and series != "不分" and series not in product_name:
        product_name = series + product_name

    # package = get_package(base64strs)
    package = get_package_130(base64strs)

    result_dict['info1'] = series
    result_dict['info2'] = method
    result_dict['info3'] = type_1
    result_dict['info4'] = type_2
    result_dict['info5'] = package
    result_dict['info6'] = degree
    result_dict['info7'] = year
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 7
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
        result_dict = category_rule_130(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)