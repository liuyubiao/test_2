import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/510_brand_list",encoding="utf-8").readlines())]


# 通常来看需要20个非通用属性
LIMIT_NUM = 20
def get_materiel_type(texts_list,product_name):
    if "水果" in product_name or "鲜果" in product_name:
        return "混合", "水果"
    if "果蔬" in product_name or "蔬果" in product_name:
        return "混合", "果蔬"

    res = get_info_list_by_list([[product_name,],],FRUIT_LIST)
    if "黑加仑" in res:
        if "葡萄" in res:
            res.remove("黑加仑")
        else:
            res.remove("黑加仑")
            res.append("葡萄")

    if len(res) == 1:
        return res[0],"水果"
    elif len(res) > 1:
        return "混合", "水果"
    else:
        if "梅" in product_name:
            return "梅子","水果"
        if "椰" in product_name:
            return "椰子","水果"
        if "莓" in product_name:
            return "莓","水果"

    res = get_info_list_by_list(texts_list,FRUIT_LIST)
    if "柠檬" in res and len(get_info_list_by_list(texts_list,["柠檬酸"])) > 0:
        res.remove("柠檬")
    if "葡萄" in res and len(get_info_list_by_list(texts_list,["葡萄糖"])) > 0:
        res.remove("葡萄")
    if "梨" in res and len(get_info_list_by_list(texts_list,["山梨酸"])) > 0:
        res.remove("梨")
    if len(res) > 1:
        return "混合","水果"
    elif len(res) == 1:
        return res[0],"水果"
    return "不分","水果"

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
    pattern_absort = "^美味|干燥|[图照]片|[凉晾]干|产品类型|工艺|^\w?冻干片$|^果蔬脆$|酥脆$"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+[干片脆]+|\w*冻干\w+|\w+干杏|\w+提子|\w+枣|\w+桂圆|\w+凉果|[^\W果肉]{2,}[果肉]?肉|\w+红薯条|\w{2,}果果|\w+果肉糖果|\w*柿饼)($|\()"
    pattern_3 = "(\w+[干片脆]+|\w*冻干\w+|\w*干杏|\w*提子|\w*桂圆|\w+凉果|\w+红薯条|\w+果肉糖果)"

    pattern_tmp = "[干片脆果条]|冻干|干杏|提子|桂圆"
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile(pattern_tmp).findall(kv[k])) > 0:
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
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(text)) ==0 and len(re.compile(pattern_absort).findall(text)) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(text)) ==0 and len(re.compile(pattern_absort).findall(text)) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
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

def category_rule_510(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    type = "不分"
    materiel = "不分"
    package = "不分"
    bags = "无"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    datasorted = [[re.sub("[冻东][于干]", "冻干", str) for str in strs] for strs in datasorted]

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,["梅美动人",],["十足","南国","OCOCO","清美","RDD","塔里木","AOA","新一代"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("尚品梅亭","尚品梅亨",brand_1)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐", 0)

    datasorted_formated = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed,datasorted_formated)

    # if (brand_1 == "不分" or product_name == "不分") and uie_obj is not None:
    #     uie_brand,uie_productname = uie_obj.get_info_UIE(datasorted)
    #     brand_1 = brand_1 if brand_1 != "不分" else uie_brand
    #     product_name = product_name if product_name != "不分" else uie_productname

    product_name = re.split("[原配]料|品牌",product_name)[0]
    product_name = re.sub("桑[甚]", "桑葚", product_name)
    product_name = re.sub("桑[棋糕甚档]", "桑椹", product_name)
    product_name = re.sub("桑[干千]$", "桑葚干", product_name)
    product_name = re.sub("杂[甚葚]", "桑葚", product_name)
    product_name = re.sub("[脂脱]片", "脆片", product_name)
    product_name = re.sub("果于", "果干", product_name)
    product_name = re.sub("[痧孙]猴桃", "猕猴桃", product_name)
    product_name = re.sub("刺架", "刺梨", product_name)
    product_name = re.sub("葡莓", "葡萄", product_name)
    product_name = re.sub("老节节", "老爷爷", product_name)
    product_name = re.sub("果蔬[脂脱]", "果蔬脆", product_name)
    product_name = re.sub("蓝蓉", "蓝莓", product_name)
    product_name = re.sub("陈干", "冻干", product_name)

    product_name = re.sub("^\W", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    materiel,type  = get_materiel_type(datasorted,product_name)

    if "薯" in product_name:
        if materiel != "不分":
            materiel = "混合"
        else:
            if "红薯" in product_name:
                materiel = "红薯"
            else:
                materiel = "薯"
        type = "果蔬"

    if materiel == "黑加仑":
        materiel = "葡萄"

    if capcity_2 != "不分":
        bags = "有"

    gsc = get_info_item_by_list(datasorted, ["果蔬脆"])
    if gsc != "不分" and product_name == "不分":
        product_name = gsc
    elif gsc != "不分" and  gsc not in product_name:
        product_name = gsc + product_name

    # package = get_package(base64strs)
    package = get_package_510(base64strs)
    if package == "玻璃罐(瓶)":
        package = "塑料罐(瓶)"

    result_dict['info1'] = bags
    result_dict['info2'] = materiel
    result_dict['info3'] = type
    result_dict['info4'] = package
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 4
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = ""
    return result_dict

if __name__ == '__main__':
    pass