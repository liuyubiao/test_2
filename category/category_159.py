import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity


Brand_list_1 = [i.strip() for i in set(open("Labels/159_brand_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/159_taste_list",encoding="utf-8").readlines())]
Inside_list = [i.strip() for i in set(open("Labels/159_inside_list",encoding="utf-8").readlines())]
# 通常来看需要20个非通用属性
LIMIT_NUM = 20

PRELIST = ["复合蛋白饮品","全脂灭菌乳","复合蛋白饮料","高温杀菌乳","巴氏杀菌乳","双蛋白饮品"]

def productNameFormat(texts_list,product_name,name_list):
    for texts in texts_list:
        total_len = len(texts)
        for index, text in enumerate(texts):
            if text == product_name:
                for i in [-1,-2,1,2]:
                    if index + i >= 0 and index + i < total_len:
                        if texts[index + i] in name_list and texts[index + i] not in product_name:
                            return product_name + "，" + texts[index + i]
    return product_name

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    result = []
    if len(product_name) > 4:
        result = get_info_list_by_list([[product_name,],], Taste_list)
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
        # result = list(set(result))
        return "".join(result)

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
    pattern_text = "[、，,]|干燥|产品类型|工艺"
    pattern_pres = "^复合蛋白饮[品料]$|的|^[每]|[好姑]牛?奶|^[^牛]奶$|优于|^菊乐牛奶$|[只做]"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+奶饮[品料]|\w+奶|\w{2,}牛乳)($|\()"
    pattern_2 = "(\w{2,}饮[品料]|\w{2,}乳)($|\()"
    pattern_3 = "\w+奶|\w{2,}牛乳|\w{2,}调制乳"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("[奶乳饮]").findall(kv[k])) > 0:
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

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0]:
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
        count = Counter(brand_1_list).most_common(6)
        brand_1 = ",".join([i[0] for i in count])
    return brand_1,brand_2

def get_EXP_store(texts_list):
    pattern = r'(冷藏)'
    for texts in texts_list:
        total_len = len(texts)
        for index,text in enumerate(texts):
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                flag = True
                for i in [-1,0,1,2]:
                    if index + i >= 0 and index + i < total_len:
                        if len(re.compile("开袋|更佳").findall(texts[index + i])) > 0:
                            flag = False
                            break
                if flag:
                    return "冷藏"

    pattern = r'常温'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "常温"

def get_EXP(kvs_list,texts_list):
    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    p_1 = re.compile(r'.*[0-9一-十]+个?[年天月]')
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    p_res_1 = p_1.findall(kv[k])
                    if len(p_res_1) > 0:
                        if len(re.compile(r'20[12]\d年[01]?\d月[0123]?\d日?').findall(kv[k])) > 0:
                            continue
                        return p_res_1[0]

    pattern = "-?\d{0,2}[-至]\d+[度Cc]?以?下?\d+个?[月天]|零下\d+以?下?\d+个?[月天]|-\d+以?下?\d+个?[月天]"
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                tmp_list.append(p_res[0])
        if len(tmp_list) > 0:
            return ",".join(tmp_list)

    pattern = r'(\d+\D+[-到至]\D*\d+\D+[\d一-十]+个?[月天]\W?\D*\d+\D+[-到至]\D*\d+\D+[\d一-十]+个?[月天])'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "无理由" not in text and "退" not in text:
                return p_res[0]

    pattern = r'(^|.*\D+)([12]年|\d+个月|[一-十]+个月|\d+天)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "无理由" not in text and "退" not in text and "天内" not in text:
                p_res = p_res[0]
                if len(re.compile("以下|[-至]|\d[度C]").findall(p_res[0])) > 0:
                    return p_res[0] + p_res[1]
                else:
                    return p_res[1]

    pattern = r'20[12]\d[-\\/\s\.]?[01]\d[-\\/\s\.]?[0123][\d]'
    date_list = []
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                p_res[0] = re.sub("\D","",p_res[0])
                try:
                    d0 = datetime.datetime.strptime(p_res[0], "%Y%m%d")
                    tmp_list.append(p_res[0])
                    date_list.append(p_res[0])
                except:
                    pass
        if len(tmp_list) >= 2:
            tmp_list = list(set(tmp_list))
            tmp_list.sort(reverse=True)
            d0 = datetime.datetime.strptime(tmp_list[0], "%Y%m%d")
            df = datetime.datetime.strptime(tmp_list[-1], "%Y%m%d")
            d_res = (d0 - df).days
            if d_res > 1:
                return str(d_res) + "天"

    date_list = list(set(date_list))
    date_list.sort(reverse=True)
    if len(date_list) >=2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y%m%d")
        df = datetime.datetime.strptime(date_list[-1], "%Y%m%d")
        d_res = (d0 - df).days
        if d_res > 1:
            return str(d_res) + "天"

    pattern = r'20[12]\d年[01]?\d月[0123]?\d日?'
    date_list = []
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "日" not in p_res[0]:
                    p_res[0] = p_res[0] + "日"
                try:
                    d0 = datetime.datetime.strptime(p_res[0], "%Y年%m月%d日")
                    tmp_list.append(p_res[0])
                    date_list.append(p_res[0])
                except:
                    pass
        if len(tmp_list) >= 2:
            tmp_list = list(set(tmp_list))
            tmp_list.sort(reverse=True)
            d0 = datetime.datetime.strptime(tmp_list[0], "%Y年%m月%d日")
            df = datetime.datetime.strptime(tmp_list[-1], "%Y年%m月%d日")
            d_res = (d0 - df).days
            if d_res > 1:
                return str(d_res) + "天"

    date_list = list(set(date_list))
    date_list.sort(reverse=True)
    if len(date_list) >= 2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y年%m月%d日")
        df = datetime.datetime.strptime(date_list[-1], "%Y年%m月%d日")
        d_res = (d0 - df).days
        if d_res > 1:
            return str(d_res) + "天"

    return "不分"

def get_people(product_name):
    people_rule = ["中老年","学生","儿童"]
    people = get_info_by_RE([[product_name, ], ], people_rule)

    return people

def get_inside(texts_list):
    res = get_info_list_by_list(texts_list,Inside_list)

    if len(res) > 0:
        return "，".join(res)
    else:
        return "不分"

def get_fat(texts_list):
    fat_list = ["全脂","脱脂","低脂","部分脱脂"]
    res = []
    for texts in texts_list:
        for text in texts:
            for t in fat_list:
                if t in text:
                    res.append(t)
    if len(res) > 0:
        count = Counter(res).most_common(2)
        return count[0][0]
    else:
        return "不分"

def get_Nutrition(kvs_list,texts_list):
    protein = "不分"
    protein_key = "营养成分表-蛋白质"
    p_1 = re.compile(r'(\d+\.?\d*)\s?(G|g|克)')
    for kvs in kvs_list:
        for kv in kvs:
            if protein_key in kv.keys():
                p_res_1 = p_1.findall(kv[protein_key])
                if len(p_res_1) > 0:
                    if float(p_res_1[0][0]) > 100:
                        protein = str(float(p_res_1[0][0]) / 10.0)
                    else:
                        protein = p_res_1[0][0]

    if protein == "不分":
        pattern = "g/[12]00ml蛋白质"
        for texts in texts_list:
            for text in texts:
                if protein == "不分":
                    p_res = get_info_by_pattern(text,pattern)
                    if len(p_res) > 0:
                        tmp_list = []
                        for t in texts:
                            p_res = get_info_by_pattern(t, "(\d+\.?\d*)g/[12]00ml蛋白质")
                            if len(p_res) > 0:
                                protein = p_res[0]
                                break
                            p_res = get_info_by_pattern(t,"^\d+\.?\d*$")
                            if len(p_res) > 0:
                                tmp_list.append(p_res[0])

                        if len(tmp_list) == 1:
                            protein = tmp_list[0]

    if protein != "不分":
        if float(protein) >= 10:
            protein = "%.1f" %(float(protein) /10.)
        elif float(protein) >= 4.6:
            protein = "%.1f" %(float(protein) /2.)
        else:
            p_res = re.compile("\d+\.\d").findall(protein)
            if len(p_res) > 0:
                protein = p_res[0]
        protein = "每100毫升含蛋白质" + protein + "克"

    return protein

def get_youji(texts_list):
    for texts in texts_list:
        for text in texts:
            if "有机" in text:
                return "有机"
    return "非有机"

def get_barcode(texts_list):
    pattern = "(^|\D)(\d{13})($|\D)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                p_res = p_res[0]
                return p_res[1]

    return "不分"

def get_package_159_unit(base64strs):
    url = url_classify + ':5040/yourget_opn_classify'

    task = MyThread(get_url_result, args=(base64strs, url,))
    task.start()
    # 获取执行结果
    result = task.get_result()
    result = package_filter(result,["编织袋","覆膜袋","无纺布袋"])
    result_box = package_filter(result,["纸盒"])
    if len(result_box) > 0:
        result = result_box

    if len(result) == 0:
        return "不分"
    if "玻璃底" in result:
        return "玻璃（瓷）瓶"

    res = Counter(result).most_common(1)[0][0]
    if res in ["塑料底","玻璃瓶"]:
        res = "塑料瓶"
    res = re.sub("保鲜盒|纸盒","保鲜方纸盒",res)
    res = re.sub("塑料袋", "塑料袋（含塑料管、塑料棒、立式塑料袋）", res)

    if "有盖" in "".join(result) and res in ["保鲜方纸盒","保鲜屋","利乐峰","利乐钻"]:
        res = "有盖" + res

    return res

def category_rule_159(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    store = "不分"
    EXP = "不分"
    package = "不分"
    taste = "不分"
    people = "不分"
    inside = "不分"
    fat_type = "不分"
    protein = "不分"
    container = "不分"
    youji = "不分"
    barcode = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,["味可滋"],["光明","a2","养元","花园","维他","极致"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("乳小专","乳小兮",brand_1)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted,"G|g|克|千克|kg|KG|ml|毫[升元开]|mL|L|[升元开]|ML","包袋盒桶罐瓶",2.5)

    capcity_2 = re.sub("[元开]", "升", capcity_2)
    capcity_1 = re.sub("[元开]", "升", capcity_1)

    # datasorted = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("^克力奶", "巧克力奶", product_name)
    product_name = re.sub("^\w高钙奶", "高钙奶", product_name)
    product_name = re.sub("生奶", "牛奶", product_name)
    product_name = re.sub("肥氏", "巴氏", product_name)
    product_name = re.sub("乳小专", "乳小兮", product_name)
    product_name = re.sub("香[蒸]","香蕉",product_name)
    product_name = re.sub("^\d+(月|毫升|[Mm][lL])", "", product_name)
    product_name = re.sub("任糖", "低糖", product_name)

    product_name = re.sub("配[料科]\w*", "", product_name)
    product_name = re.sub("^\w*品名称?", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    taste = get_taste(datasorted, product_name)

    if len(product_name) <= 12 and product_name != "不分":
        product_name = productNameFormat(datasorted, product_name, PRELIST)

    if capcity_2 != "不分":
        container = "整箱"
    else:
        container = "非整箱"

    youji = get_youji(datasorted)
    # barcode = get_barcode(datasorted)
    EXP = get_EXP(dataprocessed, datasorted)
    exp_res = re.compile("(\d)\-(\d)(\d+)").findall(EXP)
    if len(exp_res) > 0:
        exp_res = exp_res[0]
        EXP = re.sub(exp_res[0] + "-" + exp_res[1] + exp_res[2], exp_res[0] + "-" + exp_res[1] + "度" + exp_res[2], EXP)

    exp_res = re.compile("(\d+).*([天月年])").findall(EXP)
    if len(exp_res) > 0:
        exp_res = exp_res[0]
        if exp_res[1] in ["年", "月"]:
            store = "常温"
        elif exp_res[1] in ["天"]:
            if int(exp_res[0]) >= 25:
                store = "常温"
            else:
                store = "冷藏"
    if "纯牛奶" in product_name:
        store = "常温"
    if "鲜牛" in product_name:
        store = "冷藏"
    if store == "不分":
        store = get_EXP_store(datasorted)
    people = get_people(product_name)
    inside = get_inside(datasorted)
    fat_type = get_fat(datasorted)
    protein = get_Nutrition(dataprocessed, datasorted)

    package = get_package_159_unit(base64strs)

    result_dict['info1'] = store
    result_dict['info2'] = EXP
    result_dict['info3'] = package
    result_dict['info4'] = taste
    result_dict['info5'] = people
    result_dict['info6'] = inside
    result_dict['info7'] = fat_type
    result_dict['info8'] = protein
    result_dict['info9'] = container
    result_dict['info10'] = youji
    result_dict['info11'] = barcode
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 11
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    pass