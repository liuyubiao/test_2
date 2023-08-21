import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/128_brand_list",encoding="utf-8").readlines())]
Tianjia_list = [i.strip() for i in set(open("Labels/128_tianjia_list",encoding="utf-8").readlines())]

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

PRELIST = ["六月鲜","一品鲜","味极鲜","美味鲜","金标","红烧","纯生","老式"]

def productNameFormat(texts_list,product_name,name_list):
    for texts in texts_list:
        if product_name in texts:
            pre_str = ""
            for text in texts:
                if text == product_name:
                    continue
                if text in name_list and text not in product_name:
                    pre_str += text
            if pre_str != "":
                return pre_str + product_name
    return product_name

def get_type(texts_list):
    pattern_1 = "蚝油|老抽|味极鲜|生抽|鱼露|虾油"
    pattern_2 = "[汁液露汤]"
    pattern_3 = "酱油"
    pattern_4 = "红烧|调味料"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                return p_res[0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if "鲜" in text and "海鲜" not in text and "鲜花" in text:
                    return "鲜味汁、液、露"
                else:
                    return "其它汁、液、露"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if "鲜" in text:
                    return "鲜酱油"
                else:
                    return "酱油"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                return "其它汁、液、露"

    return "酱油"

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
    pattern_text = "[、，,]|干燥|产品类型|工艺|鲜[艳红虾]|酱油厂"
    pattern_pres = "的|^比|较"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+蚝油|\w+老抽王?|\w*味极鲜|\w+生抽王?|\w*鱼露|\w*虾油|\w*白[勺灼]汁|\w+[生老]抽酱油|\w*红烧王)($|\()"
    pattern_2 = "(\w*蚝油|\w*老抽王?|\w*味极鲜|\w*生抽王?|\w*鱼露|\w*虾油|\w*白[勺灼]汁|\w*[生老]抽酱油)"
    pattern_3 = "(\w*酱油|\w+[汁汤]|\w+调味料)($|\()"
    pattern_4 = "\w+酱油"

    #\w+[^海朝\W]鲜

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if "品名" in k :
                    if len(kv[k]) > 1 and len(re.compile("[汁鲜抽露油]").findall(kv[k])) > 0:
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
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0] and count[0][1] == 1:
        return count[1][0]
    return count[0][0]

def TextFormat(texts_list):
    full_text = []
    for texts in texts_list:
        tmp_str = ""
        l = len(texts)
        for index, txt in enumerate(texts):
            if len(txt) > 2 or index > 8:
                split_flag = "&"
                if tmp_str != "" and tmp_str[-1] != "&":
                    tmp_str += "&"
            else:
                split_flag = ""
                if "酒" in txt:
                    if tmp_str != "" and tmp_str[-1] == "&":
                        tmp_str = tmp_str[:-1]
            tmp_str += txt
            if index != l - 1:
                tmp_str += split_flag
        full_text.append(tmp_str.split("&"))
    return full_text

def get_inside(texts_list):
    key_list_1 = ["非转基因脱脂大豆","脱脂大豆","黑豆","草菇","海参","蘑菇","黄豆","沙棘","枸杞","纳豆","菌菇"]

    res = get_info_list_by_list_taste(texts_list,key_list_1)
    if len(res) > 0:
        return ",".join(res)

    return "不分"

def get_type_2(texts_list):
    key_list_1 = ["头道","头一道","第一道","头抽","头遍","头油"]
    key_list_2 = ["淡盐","薄盐","低盐","淡口","减盐","限盐","少盐","简盐","轻盐","无盐","少咸"]
    res_list_1 = []
    res_list_2 = []
    res = get_info_list_by_list_taste(texts_list,key_list_1)
    if len(res) > 0:
        count = Counter(res).most_common(2)
        res_list_1.append(count[0][0])

    res = get_info_list_by_list_taste(texts_list, key_list_2)
    if len(res) > 0:
        count = Counter(res).most_common(2)
        res_list_2.append(count[0][0])

    if len(res_list_1) > 0 and len(res_list_2) >0:
        type_2 = "头道，低盐"
        type_3 = res_list_2[0]
        type_4 = res_list_1[0]
    elif len(res_list_1) > 0:
        type_2 = "头道"
        type_3 = "不分"
        type_4 = res_list_1[0]
    elif len(res_list_2) >0:
        type_2 = "低盐"
        type_3 = res_list_2[0]
        type_4 = "不分"
    else:
        type_2 = "不分"
        type_3 = "不分"
        type_4 = "不分"

    return type_2,type_3,type_4

def get_youji(texts_list):
    for texts in texts_list:
        for text in texts:
            if "有机" in text:
                return "有机"
    return "非有机"

def get_tianjia(texts_list):
    for texts in texts_list:
        for text in texts:
            if "有机" in text or "无添加" in text:
                return "无添加"
    res = get_info_list_by_list(texts_list,Tianjia_list)
    if len(res) > 0:
        return "有添加"
    else:
        return "无添加"

def get_people(texts_list):
    res = get_info_by_RE(texts_list, ["儿童","宝宝"])
    res = res if res == "不分" else "儿童"
    return res

def category_rule_128(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    type_1 = "不分"
    type_2 = "不分"
    inside = "不分"
    package = "不分"
    youji = "不分"
    tianjia = "不分"
    people = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    datasorted = [[re.sub("生拍", "生抽", str) for str in strs] for strs in datasorted]

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,[],["黑龙","味王","四海"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    capcity_1 ,capcity_2= get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤|升|毫[开元升]|ML|ml|mL|L", "瓶包袋罐", 2)

    capcity_2 = re.sub("毫[开元]", "毫升", capcity_2)
    capcity_1 = re.sub("毫[开元]", "毫升", capcity_1)

    # datasorted = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed,datasorted)

    product_name = re.sub("邂", "㶍", product_name)
    product_name = re.sub("棘汁", "蒜汁", product_name)
    product_name = re.sub("松其", "松茸", product_name)
    product_name = re.sub("鉴汁", "酱汁", product_name)

    product_name = re.sub("[产食]品名[称种]", "", product_name)
    product_name = re.sub("^品名", "", product_name)
    product_name = re.sub("^小时", "", product_name)

    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    type_1  = get_type([[product_name,],])

    type_2,type_3,type_4 = get_type_2(datasorted)
    inside = get_inside(datasorted)


    if len(product_name) <= 4 and product_name != "不分":
        product_name = productNameFormat(datasorted,product_name,PRELIST)
    if product_name != "不分" :
        if type_3 != "不分" or type_4 != "不分":
            tmp_pre = ""
            if type_3 != "不分" and type_3 not in product_name:
                tmp_pre += type_3
            if type_4 != "不分" and type_4 not in product_name:
                tmp_pre += type_4
            product_name = tmp_pre + product_name

    if product_name == "酱油":
        product_name = productNameFormat(datasorted, product_name, ["白","蟹","米","香","陈","陳"])

    youji = get_youji(datasorted)
    tianjia = get_tianjia(datasorted)
    people = get_people(datasorted)

    # package = get_package(base64strs)
    package = get_package_128(base64strs)

    result_dict['info1'] = package
    result_dict['info2'] = type_1
    result_dict['info3'] = inside
    result_dict['info4'] = type_2
    result_dict['info5'] = youji
    result_dict['info6'] = tianjia
    result_dict['info7'] = people
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
        result_dict = category_rule_128(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)