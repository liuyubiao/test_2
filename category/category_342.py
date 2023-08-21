import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

# 通常来看需要20个非通用属性
Brand_list_1 = [i.strip() for i in set(open("Labels/342_brand_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/342_taste_list",encoding="utf-8").readlines())]
# 通常来看需要20个非通用属性
LIMIT_NUM = 20

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

def get_taste(texts_list,product_name):
    pattern = "\w+香[型]"
    result = get_info_list_by_list([[product_name,],], Taste_list)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0:
            result.append(p_res[0])

    if len(result) == 0:
        result = get_info_list_by_list_taste(texts_list,Taste_list)

    if len(result) == 0:
        for texts in texts_list:
            for text in texts:
                p_res = re.compile(pattern).findall(text)
                if len(p_res) > 0:
                    result.append(p_res[0])

    if len(result) == 0:
        return "不分"
    else:
        count = Counter(result).most_common(2)
        return count[0][0]

def get_type(texts_list):
    pattern_1 = "[饵凝]胶|胶饵|气雾剂|水乳剂|[烟粉饵]剂|喷射剂|[蚊蝇]香|驱蚊液|[防驱]蚊喷雾|蚊不叮|防蚊|喷雾|驱蚊香膏|蟑螂屋"
    pattern_2 = "蚊香液|蚊香片"

    result_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        type_tmp = count[0][0]

        if type_tmp in ["防蚊", "蚊不叮", "驱蚊喷雾", "防蚊喷雾"]:
            return "蚊不叮等涂抹类"
        elif type_tmp in ["饵剂","粉剂","饵胶","凝胶","胶饵","蟑螂屋","烟剂"]:
            return "杀虫诱饵"
        elif type_tmp in ["驱蚊香膏"]:
            return "驱蚊香膏"
        elif type_tmp in ["气雾剂","水乳剂","喷射剂","喷雾"]:
            return "气雾剂"
        elif type_tmp in ["驱蚊液"]:
            flag_1 = False
            flag_2 = True
            res_tmp = "蚊不叮等涂抹类"
            for texts in texts_list:
                for text in texts:
                    if "使用方法" in text:
                        flag_2 = False
                    if flag_2 and ("加热器" in text or "套装" in text):
                        flag_1 = True
                    if "电热驱蚊液" in text:
                        res_tmp = "电蚊液"
            if res_tmp == "电蚊液" and flag_1:
                res_tmp = "电蚊液含加热器"

            return res_tmp
        elif type_tmp in ["蚊香","蝇香"]:
            flag_1 = False
            flag_2 = True
            result_list = []
            for texts in texts_list:
                for text in texts:
                    if "使用方法" in text:
                        flag_2 = False
                    p_res = get_info_by_pattern(text, pattern_2)
                    if len(p_res) > 0:
                        result_list.append(p_res[0])
                    if flag_2 and ("加热器" in text or "套装" in text):
                        flag_1 = True

            if len(result_list) > 0:
                count = Counter(result_list).most_common(2)
                type_dian_tmp = count[0][0]
                if type_dian_tmp in ["蚊香液"]:
                    if flag_1:
                        return "电蚊液含加热器"
                    else:
                        return "电蚊液"
                elif type_dian_tmp in ["蚊香片"]:
                    if flag_1:
                        return "电蚊片含加热器"
                    else:
                        return "电蚊片"
            return "盘香"

    return "不分"

def get_holdtime(texts_list):
    result_list = []
    pattern_1 = "\d+晚|\d+夜|\d+天"
    pattern_2 = "\d+小时"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                result_list.append(p_res[0])
    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0 and "每天" not in text:
                result_list.append(p_res[0])
    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return "未注明"

def get_people(texts_list):
    pattern_1 = "哺乳期"
    pattern_2 = "适[用宜合]|均可"
    result_list = []
    for texts in texts_list:
        if "儿童" in texts or "儿童型" in texts:
            result_list.append("儿童")
        for index,text in enumerate(texts):
            p_res_1 = get_info_by_pattern(text, pattern_1)
            total_len = len(texts)
            if len(p_res_1) > 0:
                for i in [1,0,-1]:
                    if index + i >= 0 and index + i < total_len:
                        p_res_2 = get_info_by_pattern(texts[index + i],pattern_2)
                        if len(p_res_2) > 0:
                            result_list.extend(p_res_1)

    res = get_info_list_by_list(texts_list,["母婴","婴儿","宝宝","婴幼儿","儿宝"])
    result_list.extend(res)
    if "母婴" in result_list:
        return "婴儿、孕妇"
    res = []
    if "婴儿" in result_list or "婴幼儿" in result_list:
        res.append("婴儿")
    if "儿童" in result_list or "宝宝" in result_list or "儿宝" in result_list:
        res.append("儿童")
    if "哺乳期" in result_list:
        res.append("孕妇")

    if len(res) > 0:
        return "、".join(res)
    else:
        return "不分"

def get_target(texts_list):
    result_list = []
    for texts in texts_list:
        for text in texts:
            if "多种害虫" in text:
                result_list.append("多种害虫")
            # if "飞虫" in text or "蚊" in text or "蝇" in text:
            if "杀飞虫" in text:
                result_list.append("杀飞虫")
            # if "杀爬虫" in text or "蟑螂" in text or "蚁" in text:
            if "杀爬虫" in text:
                result_list.append("杀爬虫")

    if len(result_list) > 0 :
        if "多种害虫" in result_list or ("杀飞虫" in result_list and "杀爬虫" in result_list):
            return "多种害虫"
        else:
            count = Counter(result_list).most_common(2)
            return count[0][0]
    else:
        return "不分"

def get_smoke(texts_list):
    result_list = []
    for texts in texts_list:
        for text in texts:
            if "微烟" in text:
                result_list.append("微烟")
            if "无烟" in text:
                result_list.append("无烟")

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]
    else:
        return "未注明"

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
    pattern_pres = "[的是用市留以]|本品|^\d+套装|^悬浮剂|适量|^\w?菌剂|\d+秒\w*喷雾"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w{2,}[蚊蝇熏]香[液片膏]?|\w{2,}气雾剂|\w{2,}水乳剂|\w{2,}驱蚊液|\w+套装|\w+魔盒|\w{2,}除菌剂|\w+敷料|\w{2,}喷雾剂?|\w{2,}喷射剂|\w+胶饵|\w{2,}[饵粉]剂|\w+[凝饵]胶|\w*捕蟑屋|[\w·]+吡虫啉|\w*灭蚤灵|\w*蚊蝇香)($|\()"
    pattern_2 = "(\w{2,}[蚊蝇熏]香[液片膏]|\w{2,}气雾剂|\w{2,}水乳剂|\w{2,}驱蚊液|\w+套装|\w{2,}除菌剂|\w+敷料|\w{2,}喷雾剂?|\w{2,}喷射剂|\w+胶饵|\w{2,}[饵粉]剂|\w+[凝饵]胶)"
    pattern_3 = "([\u4e00-\u9fa5]+[液膏剂]|^蚊香片?)($|\()"
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("[剂液片香胶饵盒装]").findall(kv[k])) > 0:
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
        if len(count) > 1 and count[0][0] in count[1][0]:
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
        if len(count) > 1 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0]:
        return count[1][0]
    return count[0][0]

def get_Capacity_texts(texts_list,unit = "[个只条]|[Pp][Cc][Ss]",unit_default = "只",limit_floor = 1,limit_top = 200):
    pattern = r'(\d+)\s?({})装'.format(unit)
    result_list = []
    p = re.compile(pattern)
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                if "加量" in text:
                    continue
                p_res = p_res[0]
                result_list.append(p_res[0] + p_res[1])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0],False

    result_list = []
    pattern = r'(\d+)\s?({})'.format(unit)
    p = re.compile(pattern)
    for texts in texts_list:
        tmp_list = []
        for index, text in enumerate(texts):
            if "片区" in text:
                continue
            p_res = p.findall(text)
            if len(p_res) > 1:
                p_res_double = re.compile("(\d+)(%s)[赠加+送]{0,2}(\d+)(%s)"%(unit,unit)).findall(text)
                if len(p_res_double) > 0 and p_res_double[0][1] == p_res_double[0][3]:
                    p_res_double = p_res_double[0]
                    tmp_list.append(str(int(p_res_double[0]) + int(p_res_double[2])) + p_res_double[1])
                    result_list.append(str(int(p_res_double[0]) + int(p_res_double[2])) + p_res_double[1])
            elif len(p_res) > 0 and float(p_res[0][0]) < limit_top and float(p_res[0][0]) > limit_floor:
                p_res = p_res[0]
                tmp_list.append(p_res[0] + p_res[1])
                result_list.append(p_res[0] + p_res[1])
        if len(tmp_list) == 1:
            return tmp_list[0],False

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0],False

    pattern = r'^(%s)$'%(unit)
    p = re.compile(pattern)
    for texts in texts_list:
        total_len = len(texts)
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                for i in [-2,-1,1]:
                    if index + i >= 0 and index + i < total_len:
                        p_res_num = re.compile("^\d{1,2}$").findall(texts[index + i])
                        if len(p_res_num) > 0:
                            result_list.append(p_res_num[0] + p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0],False

    return "不分",True

def category_rule_342(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    taste = "不分"
    holdtime = "不分"
    target = "不分"
    smoke = "不分"
    type = "不分"
    people = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,[],["阳光","3M","半秒钟","OFF!","Dceo","即速","超减"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("Raid","雷达",brand_1)
    brand_1 = re.sub("bebebebe", "kekebebe", brand_1)
    brand_1 = re.sub("BENOBABY", "比诺贝比BENOBABY", brand_1,re.IGNORECASE)

    capcity_1, _ = get_Capacity_texts(datasorted, unit="[盘片圈张粒枚袋支]|[单双][盘圈]|特大单盘")
    if capcity_1 == "不分":
        capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "g|克|ml|毫[升开元]|mL|L|[升开元]|ML", "片枚瓶粒", 2.5)

        capcity_2 = re.sub("毫[开元]", "毫升", capcity_2)
        capcity_1 = re.sub("毫[开元]", "毫升", capcity_1)

    capcity_1 = re.sub("特大单盘", "单盘", capcity_1)
    capcity_3 = get_info_list_by_list(datasorted, ["1器", "1特惠装", "加热器套装", "器1"])
    if len(capcity_3) > 0:
        if capcity_1 != "不分":
            capcity_1 += "+1器"
        if capcity_2 != "不分":
            capcity_2 += "+1器"
    # datasorted = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("长虫", "杀虫", product_name)
    product_name = re.sub("[仔好][仔好]爽", "仔仔爽", product_name)
    product_name = re.sub("园童", "因童", product_name)

    product_name = re.sub("^\w除菌剂", "除菌剂", product_name)
    product_name = re.sub("^\w?气雾剂", "杀虫气雾剂", product_name)
    product_name = re.sub("^\w?喷射剂", "杀虫喷射剂", product_name)

    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    if len(re.compile("(\D|^)(11|12|21)(\D|$)").findall(product_name)) > 0:
        product_name = re.sub("11", "1+1", product_name)
        product_name = re.sub("21", "2+1", product_name)
        product_name = re.sub("12", "1+2", product_name)

    if product_name in ["蚊香"]:
        product_name = productNameFormat(datasorted, product_name, ["野外艾草", "野外型"])

    type = get_type(datasorted)
    if type == "不分":
        if "液" in product_name:
            type = "电蚊液"
        elif "粉剂" in product_name or "饵" in product_name:
            type = "杀虫诱饵"
        elif "剂" in product_name:
            type = "气雾剂"

    if type in ["盘香", "电蚊液含加热器", "电蚊片含加热器", "电蚊液", "电蚊片"]:
        holdtime = get_holdtime(datasorted)
        people = get_people(datasorted)
    else:
        target = get_target(datasorted)

    if type in ["盘香"]:
        smoke = get_smoke(datasorted)

    taste = get_taste(datasorted, product_name)
    taste = re.sub("^[无五][香味]型?", "无味", taste)

    result_dict['info1'] = taste
    result_dict['info2'] = holdtime
    result_dict['info3'] = target
    result_dict['info4'] = smoke
    result_dict['info5'] = type
    result_dict['info6'] = people
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 6
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    pass