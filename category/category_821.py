import os
import re

from util import *
from glob import glob

LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/821_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/821_brand_list_2",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/821_type_list",encoding="utf-8").readlines())]
Charac_list = [i.strip() for i in set(open("Labels/821_charac_list",encoding="utf-8").readlines())]


def get_type(texts_list,productname):
    if len(re.compile("一体|[短内]裤式|拉拉裤|小内裤").findall(productname)) > 0:
        return "拉拉裤"
    if "学" in productname or "训练裤" in productname:
        return "学习裤"

    pattern = "("
    for i in Type_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"

    p_res = get_info_by_pattern(productname, pattern)
    if len(p_res) > 0:
        return p_res[0]

    for texts in texts_list:
        for text in texts:
            if len(re.compile("一体|[短内]裤式").findall(text)) > 0:
                return "拉拉裤"

    return "需粘贴"


def get_charac(texts_list):
    result = get_info_list_by_list(texts_list,Charac_list)
    for key in ["漏","薄","柔"]:
        key_list = []
        for res in result:
            if key in res:
                key_list.append(res)

        if len(key_list) > 1:
            key_list.sort(key=len)
            for k in key_list[:-1]:
                result.remove(k)
    if len(result) > 0:
        return "，".join(result)
    else:
        return "不分"

def get_productName_voting(kvs_list,texts_list):
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+纸[尿康原][裤片裙]|\w+一体裤|\w+学[步习走]裤|\w+小内裤|\w+拉拉裤|\w+成长裤|\w+游泳裤|\w+隔尿垫|\w+护理垫|\w+训练裤|\w+尿片|\w+短裤式|\w+尿不湿|\w+睡睡裤|\w+弹弹裤|\w+安心裤|\w+易拉裤|\w+动动裤)($|NB|[SXLM]+)"
    pattern_2 = "(\w*纸尿[裤片]|\w*一体裤|\w*学[步习走]裤|\w*小内裤|\w*拉拉裤|\w*成长裤|\w*游泳裤|\w*隔尿垫|\w*护理垫|\w*训练裤|\w*尿片|\w*环腰裤|\w+运动裤)($|NB|[XLM]+)"
    pattern_3 = "(\w*纸尿[裤片]|\w*一体裤|\w*学[步习走]裤|\w*小内裤|\w*拉拉裤|\w*成长裤|\w*游泳裤|\w*隔尿垫|\w*护理垫|\w*训练裤|\w*尿片)"
    pattern_4 = "(\w+垫|\w*短裤式)$"

    pattern_text = "[、，,]"
    pattern_pres = "[的将]|更换|\d大标准|污染|^Q[\u4e00-\u9fa5]|必型|^用"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名"]):
                    if len(kv[k]) > 1 and len(re.compile("[片裤垫]\w{0,3}$|尿不湿").findall(kv[k])) > 0:
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
            if len(p_res) > 0 :
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
            p_res = get_info_by_pattern(text, pattern_3)
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
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    return count[0][0]

def productNameFormat(texts_list,product_name):
    res_name = ""
    for texts in texts_list:
        if product_name in texts:
            pre_str = ""
            for index,text in enumerate(texts):
                if index > 8:
                    break
                if text == product_name:
                    res_name = pre_str + product_name
                if len(re.compile("^[\u4e00-\u9fa5·]$").findall(text)) > 0:
                    pre_str = text
    if res_name == "":
        return product_name
    else:
        return res_name

def get_size_voting(texts_list):
    # pattern = "\d+[xX*]\d+[CcMm][Mm]"
    # for texts in texts_list:
    #     for text in texts:
    #         p_res = get_info_by_pattern(text, pattern)
    #         if len(p_res) > 0:
    #             return p_res[0]

    result_list = []
    pattern_0 = "[\u4e00-\u9fa5]+(NB|M|S|[Xx]*L)\W?\d{1,2}(片|枚|Pcs|PCS)?$"
    pattern_1 = "^I?(NB|M|S|[Xx]*L)\W?\d{1,2}(片|枚|Pcs|PCS)?$"
    pattern_2 = "[\u4e00-\u9fa5]+(NB|M|S|[Xx]*L)\d{1,2}[片枚]?"
    pattern_3 = "^I?(NB|M|S|[Xx]*L)\d{1,2}[片枚]?"
    pattern_4 = "^I?(NB|M|S|[Xx]*L)$"
    pattern_5 = "[^a-zA-Z\W](NB|M|S|[Xx]*L)[^a-zA-Z]"
    pattern_6 = "^I?(NB|M|S|[Xx]*L)[^a-zA-Z]"
    pattern_7 = "[\u4e00-\u9fa5\-0-9]+([LMS])[\u4e00-\u9fa5\-0-9]+"
    pattern_8 = "(NB|[Xx]+L)"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_0)
            if len(p_res) > 0:
                result_list.append(p_res[0][0])
                continue
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                result_list.append(p_res[0][0])
                continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 1 or int(count[0][1]) > int(count[1][1]):
            return count[0][0]
        else:
            result_list = []

    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = get_info_by_pattern(text, pattern_4)
            total_len = len(texts)
            if len(p_res) > 0:
                for i in [-2, -1,0, 1, 2]:
                    if index + i >= 0 and index + i < total_len:
                        p_res_tmp = re.compile("^\d{1,2}(片|枚|Pcs|PCS)$").findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                result_list.append(p_res[0])
                continue
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                result_list.append(p_res[0])
                continue
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                result_list.append(p_res[0])
                continue
            p_res = get_info_by_pattern(text, pattern_5)
            if len(p_res) > 0:
                result_list.append(p_res[0])
                continue
            p_res = get_info_by_pattern(text, pattern_6)
            if len(p_res) > 0:
                result_list.append(p_res[0])
                continue
            p_res = get_info_by_pattern(text, pattern_7)
            if len(p_res) > 0:
                result_list.append(p_res[0])
                continue
            p_res = get_info_by_pattern(text, pattern_8)
            if len(p_res) > 0:
                result_list.append(p_res[0])
                continue

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)

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
        count = Counter(brand_1_list).most_common(15)
        brand_1 = ",".join([i[0] for i in count])
    return brand_1,brand_2

def get_Capacity_821(texts_list):
    result_list = []
    result_list_tmp = []
    p_1 = re.compile(r'(\d+)\s?(P[Ce]S?|枚|片)',re.IGNORECASE)
    p_2 = re.compile(r'(\d+)\s?(P[Ce]S?|枚|片)',re.IGNORECASE)
    p_3 = re.compile("([\u4e00-\u9fa5]|^|\-)(NB|M|S|[Xx]*L)[\W\u4e00-\u9fa5]*(\d{1,2})([\u4e00-\u9fa5Pp]|$)")
    p_4 = re.compile(r'^(\d+)$')
    for texts in texts_list:
        total_len = len(texts)
        for index,text in enumerate(texts):
            p_res = get_info_by_pattern(text, r'^(\d+)$')
            if len(p_res) > 0:
                if int(p_res[0]) > 100 or p_res[0][0] == "0":
                    continue
                for i in [-2, -1, 1, 2]:
                    if index + i >= 0 and index + i < total_len:
                        p_res_tmp = re.compile("^(P[Ce]S?|枚|片)$|^(P[Ce]S?|枚|片)\W(P[Ce]S|枚|片)$|^1(P[Ce]S?|枚|片)$",re.IGNORECASE).findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            result_list.append(p_res[0] + "片")

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = p_1.findall(text)
            if len(p_res) > 0:
                for p_r in p_res:
                    if float(p_r[0]) <= 96 and p_r[0][0] != "0":
                        tmp_list.append(p_r[0] + "片")
        if len(tmp_list) < 3 and len(tmp_list) > 0:
            result_list.extend(tmp_list)
        elif len(tmp_list) >= 3:
            result_list_tmp.extend(tmp_list)

    if len(result_list_tmp) == 0:
        capacity_tmp = "不分"
    else:
        count = Counter(result_list_tmp).most_common(2)
        capacity_tmp = count[0][0]

    for texts in texts_list:
        text_str = ""
        for text in texts:
            if len(re.compile("\d$").findall(text_str)) > 0 and len(re.compile("^\d").findall(text)) > 0:
                text_str += "," + text
            else:
                text_str += text
        p_res = p_2.findall(text_str)
        if len(p_res) > 0:
            for p_r in p_res:
                if float(p_r[0]) <= 96 and p_r[0][0] != "0":
                    if p_r[0] + "片" not in result_list and p_r[0] + "片" not in result_list_tmp:
                        result_list.append(p_r[0] + "片")

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 1 or int(count[0][1]) > int(count[1][1]):
            return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = p_3.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if float(p_res[2]) <= 84 and p_res[2][0] != "0":
                    result_list.append(p_res[2] + "片")

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) == 1 or int(count[0][1]) > int(count[1][1]):
            return count[0][0]

    pattern = r'(^[xX]*L$|^M$|^S$|片|枚|[Pp][Cce][Ss])'
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res_1 = get_info_by_pattern(text, pattern)
            total_len = len(texts)
            if len(p_res_1) > 0:
                for i in [-2, -1, 0, 1, 2]:
                    if index + i >= 0 and index + i < total_len:
                        p_res_tmp = re.compile("^\d{1,2}$").findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            result_list.append(p_res_tmp[0] + "片")

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = p_4.findall(text)
            if len(p_res) > 0:
                if float(p_res[0]) <= 84 and p_res[0][0] != "0":
                    result_list.append(p_res[0] + "片")

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if int(count[0][1]) > 1 or len(count) == 1:
            return count[0][0]

    return capacity_tmp

def get_Capacity_2(texts_list):
    pattern = r'\d+\W?[片枚P][CS]{0,2}[*xX]\d+?'
    pattern_2 = r'(\d+)\W?(片|枚|PCS)[*xX](\d+)?'
    p = re.compile(pattern,re.IGNORECASE)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2,re.IGNORECASE).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if p_res_2[2] != "0" and p_res_2[2] != "" and float(p_res_2[2]) < 10:
                        return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), "片")), re.sub(u"\)", "",p_res[0]) ,p_res_2[2] ,[p_res_2[0] + "片", ]
                    else:
                        return "不分", "不分" ,"不分" ,"不分"

    pattern_1 = "日用?(\d+)[P片枚]"
    pattern_2 = "夜用?(\d+)[P片枚]"
    tmp_1 = "不分"
    tmp_2 = "不分"
    for text_list in texts_list:
        for text in text_list:
            p_res = re.compile(pattern_1).findall(text)
            if len(p_res) > 0:
                if p_res[0] != "0":
                    tmp_1 = p_res[0]

    for text_list in texts_list:
        for text in text_list:
            p_res = re.compile(pattern_2).findall(text)
            if len(p_res) > 0:
                if p_res[0] != "0":
                    tmp_2 = p_res[0]

    if tmp_2 != "不分" and tmp_1 != "不分":
        return ("%d%s" % (float(tmp_1) + float(tmp_2), "片")), "日用%s片 + 夜用%s片"%(tmp_1,tmp_2),"不分" , "不分"

    unit = "PCS|枚|片"
    unit_default = "片"
    num_limit = 120
    pattern = "(\d{1,2})(%s)/?[装包]?[*xX]?(\d{1,2})[包]" % (unit)
    pattern_compile = re.compile(pattern,re.IGNORECASE)
    for texts in texts_list:
        for text in texts:
            p_res = pattern_compile.findall(text)
            if len(p_res) > 0:
                for p_r in p_res:
                    num_tmp = int(p_r[0]) * int(p_r[2])
                    if num_tmp < num_limit:
                        return str(num_tmp) + unit_default, p_r[0] + unit_default + "*" + p_r[2],p_r[2], [p_r[0] + unit_default, ]

    return "不分","不分","不分","不分"

def get_gender(texts_list):
    pattern = "男女"
    for text_list in texts_list:
        for text in text_list:
            p_res = re.compile(pattern).findall(text)
            if len(p_res) > 0:
                return "男女共用"

    return "未注明"

def get_dayornight(texts_list):
    pattern_1 = "日用"
    pattern_2 = "夜用"
    flag_1 = False
    flag_2 = False
    for text_list in texts_list:
        for text in text_list:
            p_res_1 = re.compile(pattern_1).findall(text)
            if len(p_res_1) > 0:
                flag_1 = True
            p_res_2 = re.compile(pattern_2).findall(text)
            if len(p_res_2) > 0:
                flag_2 = True

    if flag_1 and flag_2:
        return "日用+夜用"
    else:
        return "不分"

def get_Capacity_bak(texts_list,size):
    result_list = []
    pattern = size + "\W?(\d{1,2})(\D|$)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) == 1:
                p_res = p_res[0]
                result_list.append(p_res[0] + "片")

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]
    return "不分"

def category_rule_821(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    type = "不分"
    size = "不分"
    characteristic = "不分"
    gender = "不分"
    package_num = "1"
    dayornight = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, ["ANYONE"], ["家宝","本护","ddoAu","乐透","MQD"], [])
        # brand_1,brand_2 = get_brand_list_test(datasorted)

    brand_1 = re.sub("AIKUUBEAR", "爱酷熊", brand_1, re.IGNORECASE)
    brand_1 = re.sub("免头妈妈", "兔头妈妈", brand_1)
    brand_1 = re.sub("可立乐", "百立乐", brand_1)
    brand_1 = re.sub("ddoAu", "Atopp", brand_1, re.IGNORECASE)
    brand_1 = re.sub("妙然宝具", "妙然宝贝", brand_1)
    brand_1 = re.sub("思得宝", "恩得宝", brand_1)
    brand_1 = re.sub("丛林假学", "丛林假日", brand_1)
    brand_1 = re.sub("Lelch", "Lelch露安适", brand_1, re.IGNORECASE)
    brand_1 = re.sub("QinBaoBao", "QinBaoBao亲宝宝", brand_1, re.IGNORECASE)
    brand_1 = re.sub("柔Y", "柔丫", brand_1, re.IGNORECASE)

    if product_name == "不分":
        product_name = get_productName_voting(dataprocessed, datasorted)

    if product_name in ["纸尿裤", "短裤式", "学步裤"]:
        product_name = productNameFormat(datasorted, product_name)
        if product_name == "短裤式":
            product_name = "短裤式婴儿纸尿裤"

    product_name = re.sub("各扣", "搭扣", product_name)
    product_name = re.sub("天求", "天才", product_name)
    product_name = re.sub("环指", "环抱", product_name)
    product_name = re.sub("装件", "装仔", product_name)
    product_name = re.sub("桃子集", "桃子果", product_name)
    product_name = re.sub("纸[康尿原][裤裙]", "纸尿裤", product_name)
    product_name = re.sub("思得宝", "恩得宝", product_name)
    product_name = re.sub("暖贴型", "腰贴型", product_name)
    product_name = re.sub("要芭", "碧芭", product_name)
    product_name = re.sub("量空", "星空", product_name)
    product_name = re.sub("要儿", "婴儿", product_name)

    product_name = re.sub("^[a-zA-Z\d]{1,2}婴儿纸尿裤", "婴儿纸尿裤", product_name)
    if len(re.compile("^儿\w{2}裤").findall(product_name)) > 0:
        product_name = re.sub("^儿", "婴儿", product_name)
    product_name = re.sub("^[a-zA-Z\d]{1,2}纸尿裤", "纸尿裤", product_name)

    product_name = re.sub("^\d+片", "", product_name)
    product_name = re.sub("^\d+片", "", product_name)
    product_name = re.sub("[XLM号码\d片]+装?$", "", product_name)
    product_name = re.sub("[a-zA-Z]+$", "", product_name)
    product_name = re.sub("(货号|品牌|主要成分)[^片裤]*$", "", product_name)
    product_name = re.sub("^品?名?称", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    capcity_1 = get_Capacity_821(datasorted)
    capcity_1_mul, capcity_2_tmp, capcity_package_num, flag_list_mul = get_Capacity_2(datasorted)
    if capcity_1 == "不分" or capcity_1 in flag_list_mul or "日用" in capcity_2_tmp:
        capcity_1 = capcity_1_mul
        capcity_2 = capcity_2_tmp
    if capcity_package_num != "不分":
        package_num = capcity_package_num

    type = get_type(datasorted, product_name)
    if "学" in type: type = "学习裤"
    if "垫" in type: type = "垫巾"

    size = get_size_voting(datasorted)
    if capcity_1 == "不分" and size != "不分":
        capcity_1 = get_Capacity_bak(datasorted, size)
    characteristic = get_charac(datasorted)
    gender = get_gender(datasorted)
    dayornight = get_dayornight(datasorted)

    # if product_name == "不分":
    #     product_name = "婴儿纸尿裤"

    result_dict['info1'] = type
    result_dict['info2'] = size
    result_dict['info3'] = characteristic
    result_dict['info4'] = gender
    result_dict['info5'] = package_num
    result_dict['info6'] = dayornight
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\821-婴儿纸尿裤(垫片)'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        product = "3959622"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_821(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)