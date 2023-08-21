import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/134_brand_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/134_taste_list",encoding="utf-8").readlines())]
Ingredients_list_ori = [i.strip() for i in open("Labels/134_ingredients_list",encoding="utf-8").readlines()]
Ingredients_list = []
for line in Ingredients_list_ori:
    Ingredients_list.extend(re.split("[^\-0-9a-zA-Z\u4e00-\u9fa5]",line))
Ingredients_list = set(Ingredients_list)
if "" in Ingredients_list: Ingredients_list.remove("")
Ingredients_list = list(Ingredients_list)
Ingredients_list.sort(key=len,reverse=True)

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    result = get_info_list_by_list([[product_name,],], Taste_list)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0:
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

def get_type(texts_list,product_name):
    sorted_list = mySorted(["派","蛋糕"],product_name)
    if "派" in sorted_list and sorted_list[-1] == "派":
        return "派"
    return "蛋糕"

def get_brand(kvs_list):
    pattern = r'(生产商)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    brand_tmp = kv[k].replace("有限公司", "&").replace("有限责任公司", "&").replace("实业", "&")
                    return brand_tmp.split("&")[0]
    return "不分"

def get_productName_voting(kvs_list,texts_list):
    pattern_pres = "发现|用好|常温蛋糕|满格华夫|^烘烤|的"
    pattern_text = "[、，]|类型|其他类"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+蛋糕卷?|\w+瑞士卷|\w+马卡龙|\w+蛋黄酥|\w+玛德琳|\w+提拉米苏|\w+泡芙|\w+雪贝|\w+牛乳卷|\w+双拼卷|\w*巧克力派|\w+肉松球|\w+枣糕王?|\w+铜锣烧|\w+哈斗|\w+华夫饼?|\w+布丁|\w{2,}千层|\w+打糕|\w*布朗尼|\w*舒芙蕾|\w+奶酪包)($|\()"
    pattern_2 = "\w+[糕卷派]\w*\(\w+味\)"
    pattern_3 = "\w*蛋糕卷?|\w*瑞士卷|\w*蛋黄酥|\w*马卡龙|\w*玛德琳|\w*提拉米苏|\w*泡芙|\w*雪贝|\w*牛乳卷|\w*双拼卷|\w*巧克力派|\w*肉松球|\w*枣糕王|\w*铜锣烧|\w+哈斗|\w*榴莲千层|\w{2,}糕点$"
    pattern_4 = "(\w+[糕卷派]|\w+奥利奥|\w+卷卷)($|\()"

    pattern_tmp = "[糕卷派]|铜锣烧|哈斗|肉松球|豆乳|芝士|千层|面包"
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称", "名"]) and len(k) < 6:
                    if len(re.compile(pattern_tmp).findall(kv[k])) == 0:
                        result_list_tmp.append(kv[k])
                    else:
                        result_list.append(kv[k])
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
                if len(re.compile(pattern_pres).findall(p_res[0])) ==0 and len(re.compile(pattern_text).findall(text)) ==0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if len(re.compile(pattern_pres).findall(p_res[0])) ==0 and len(re.compile(pattern_text).findall(text)) ==0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if len(re.compile(pattern_pres).findall(p_res[0])) ==0 and len(re.compile(pattern_text).findall(text)) ==0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_pres).findall(p_res[0])) ==0 and len(re.compile(pattern_text).findall(text)) ==0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    return count[0][0]

def LCS(string1, string2):
    len1 = len(string1)
    len2 = len(string2)
    res = [[0 for i in range(len1 + 1)] for j in range(len2 + 1)]
    for i in range(1, len2 + 1):
        for j in range(1, len1 + 1):
            if string2[i - 1] == string1[j - 1]:
                res[i][j] = res[i - 1][j - 1] + 1
            else:
                res[i][j] = max(res[i - 1][j], res[i][j - 1])
    return res[-1][-1]

def isIngredient(text):
    Ingredient_Abort_List_in = ["省","市","地址","包装","背面","年","月","公司","避免","企业","本品","产地","产国","表","信息","阴凉","光线","生产","号"]
    Ingredient_Abort_List_re = "^[日\d]+$"
    if len(text) <= 1:
        return False
    for i in Ingredient_Abort_List_in:
        if i in text:
            return False
    if len(re.compile(Ingredient_Abort_List_re).findall(text)) > 0:
        return False

    return True

def insertList(result,insertingList):
    result_str = ",".join(result)
    sortedResult = result.copy()
    for r_tmp in insertingList:
        index = len(sortedResult)
        for r in r_tmp[::-1]:
            if r in sortedResult:
                index = sortedResult.index(r)
            elif r in result_str:
                continue
            else:
                flag = True
                for j in sortedResult[:index + 1]:
                    if j not in Ingredients_list:
                        correct_num = LCS(r, j)
                        len_per_1 = float(correct_num / len(r))
                        len_per_2 = float(correct_num / len(j))
                        if len_per_1 > 0.5 or len_per_2 > 0.5:
                            index = sortedResult.index(j)
                            if "(" not in j :
                                sortedResult[index] = r
                            flag = False
                    else:
                        correct_num = LCS(r, j)
                        len_per_1 = float(correct_num / len(j))
                        if len_per_1 > 0.9:
                            index = sortedResult.index(j)
                            flag = False
                if flag:
                    sortedResult.insert(index, r)
                    index = sortedResult.index(r)
    return sortedResult

def insertList_bak(result,insertingList):
    sortedResult = result.copy()
    for r_tmp in insertingList:
        index = len(sortedResult)
        for r in r_tmp[::-1]:
            if r in sortedResult:
                index = sortedResult.index(r)
            else:
                flag = True
                if r not in Ingredients_list:
                    for j in sortedResult[:index+1]:
                        correct_num = LCS(r, j)
                        len_per_1 = float(correct_num / len(r))
                        len_per_2 = float(correct_num / len(j))
                        if len_per_1 > 0.5 or len_per_2 > 0.5:
                            index = sortedResult.index(j)
                            flag = False
                else:
                    for j in sortedResult[:index + 1]:
                        if j not in Ingredients_list and "(" not in j:
                            correct_num = LCS(r, j)
                            len_per_1 = float(correct_num / len(r))
                            len_per_2 = float(correct_num / len(j))
                            if len_per_1 > 0.5 or len_per_2 > 0.5:
                                index = sortedResult.index(j)
                                sortedResult[index] = r
                                flag = False
                        else:
                            correct_num = LCS(r, j)
                            len_per_1 = float(correct_num / len(j))
                            if len_per_1 > 0.9:
                                index = sortedResult.index(j)
                                flag = False
                if flag:
                    sortedResult.insert(index, r)
                    index = sortedResult.index(r)
    return sortedResult

def get_ingredients_list(texts_list):
    result = []
    result_bak = []
    for texts in texts_list:
        tmp = []
        tmp_bak_str = ""
        for text in texts:
            index = 0
            if "无添加" in text or "零添加" in text or "0添加" in text or "适量" in text or "入" in text :
                break
            # if ":" in text and len(re.compile("\w*[料科]表?:").findall(text)) == 0 and len(re.compile("\w*添加剂:").findall(text)) == 0:
            #     continue

            text = re.sub("^配?\W*[料科]表?\W*","",text)

            for ingredient in re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\\/]", text):
                if ingredient in tmp:
                    continue
                if ingredient in Ingredients_list or len(re.compile("沙拉酱|果味?酱|草莓酱|饼干碎|可丝达酱|流心馅").findall(ingredient)) > 0:
                    if len(ingredient) < 8:
                        tmp.append(ingredient)
                    else:
                        for I in Ingredients_list:
                            if I in ingredient and I not in "".join(tmp):
                                tmp.append(I)
                    index += 1

        for ingredient in re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\\/]", "".join(texts)):
            if ingredient in tmp:
                continue
            if ingredient in Ingredients_list or len(re.compile("沙拉酱|果味?[酱泥]|草莓酱|饼干碎|可丝达酱").findall(ingredient)) > 0:
                for t in tmp:
                    if t in ingredient:
                        tmp.remove(t)
                        break
                if len(ingredient) < 8:
                    tmp.append(ingredient)
                else:
                    for I in Ingredients_list:
                        if I in ingredient and I not in "".join(tmp):
                            tmp.append(I)
                index += 1

        if len(tmp) > 0:
            result.append(tmp)
            # result_bak.append([i for i in re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\(\)]", tmp_bak_str) if isIngredient(i)])

    result = [[re.sub("配料表?", "", i) for i in r] for r in result]
    result = [[re.sub("^料表?$", "", i) for i in r] for r in result]
    result = [[re.sub("\w*信息", "", i) for i in r] for r in result]
    result = [[re.sub("\w*编号", "", i) for i in r] for r in result]
    result = [[re.sub("^含有?", "", i) for i in r] for r in result]

    result_bak = [[re.sub("配料表?", "", i) for i in r] for r in result_bak]
    result_bak = [[re.sub("\w*信息", "", i) for i in r] for r in result_bak]
    result_bak = [[re.sub("^料表?$", "", i) for i in r] for r in result_bak]
    result_bak = [[re.sub("\w*编号", "", i) for i in r] for r in result_bak]
    result_bak = [[re.sub("^含有?", "", i) for i in r] for r in result_bak]

    result.sort(key=len, reverse=True)
    result_bak.sort(key=len, reverse=True)

    return result,result_bak

def get_ingredients(kvs_list, texts_list):
    pattern = r'\w*配[料科]表?$|^[料科]表?$'
    ingredients = []
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    ingredients.append(re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\(\)]", kv[k]))

    ingredients = [[i for i in j if isIngredient(i) and i in Ingredients_list] for j in ingredients]
    ingredients.sort(key=len,reverse=True)
    # ingredients_list 认为是顺序可靠的，ingredients_list_bak认为内容是可靠且完整的
    ingredients_list = []
    best_score = 0
    for ingredient in ingredients:
        score = 0
        for i in ingredient:
            if i in Ingredients_list:
                score += 1
            elif not isIngredient(i):
                score -= 1
            else:
                score += 0.55

        if score > best_score:
            ingredients_list = ingredient.copy()
            best_score = score

    ingredients_list_bak,ingredients_list_bak_strs = get_ingredients_list(texts_list)
    if len(ingredients_list) == 0 :
        ingredients_list_tmp = ingredients_list_bak.copy()
        ingredients_list_tmp.extend(ingredients_list_bak_strs)
        ingredients_list_tmp = sorted(ingredients_list_tmp,key=len,reverse=True)

        if len(ingredients_list_tmp) > 0 and ingredients_list_tmp[0] != "":
            ingredients_list = ingredients_list_tmp[0].copy()

    ingredients_list = [i for i in ingredients_list if isIngredient(i)]

    result = insertList(ingredients_list, ingredients_list_bak)
    # result = sorted(list(set(result)), key=result.index)

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

    if len(result) > 0:
        result = ",".join(res)
    else:
        result = "不分"

    return result

def get_EXP(kvs_list,texts_list):
    result_list = []
    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    p_1 = re.compile(r'.*[0-9一二三四五六七八九十]+个?[年天月]')
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    p_res_1 = p_1.findall(kv[k])
                    if len(p_res_1) > 0:
                        if len(re.compile(r'20[12]\d年[01]?\d月[0123]?\d日?').findall(kv[k])) > 0:
                            continue
                        result_list.append(p_res_1[0])

    pattern = "(\d[-到至]{1,2}\d|\d+月?[-一到至]{1,2}\d+月|零下\d+|^-\d+|下18|18[C度])(\D+)(\d+个月|[一二三四五六七八九十]+个月|\d+天)"
    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        exp_tmp = count[0][0]
        p_res = get_info_by_pattern(exp_tmp, pattern)
        if len(p_res) > 0:
            exp_list = []
            store_list = []
            for p_r in p_res:
                if p_r[2] not in exp_list:
                    exp_list.append(p_r[2])
                    if "月" == p_r[1]:
                        p_r_tmp = re.sub("一", "-", p_r[0])
                        p_r_tmp += "月"
                        store_list.append(p_r_tmp)
                    elif "月" in p_r[0]:
                        p_r_tmp = re.sub("一", "-", p_r[0])
                        store_list.append(p_r_tmp)
                    elif len(re.compile("^\d").findall(p_r[0])) > 0:
                        store_list.append(p_r[0] + "度保存")
                    elif len(re.compile("18").findall(p_r[0])) > 0:
                        store_list.append("零下18度冷冻保存")
                    else:
                        p_r_tmp = re.sub("^-", "零下", p_r[0])
                        store_list.append(p_r_tmp + "度保存")
            res_list = []
            for s,e in zip(store_list,exp_list):
                res_list.append(s + e)

            if len(res_list) > 1:
                return ",".join(res_list[:2])
            elif len(res_list) == 1:
                return result_list[0]
        else:
            p_res = re.compile("\d+个月|[一二三四五六七八九十]+个月|\d+天").findall(exp_tmp)
            if len(p_res) > 0:
                return p_res[0]
            return exp_tmp

    # pattern = "-?\d{0,2}[-至]\d+[度Cc]?以?下?\d+个?[月天]|零下\d+以?下?\d+个?[月天]|-\d+以?下?\d+个?[月天]"
    for texts in texts_list:
        exp_list = []
        store_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                for p_r in p_res:
                    if p_r[2] not in exp_list:
                        exp_list.append(p_r[2])
                        if "月" == p_r[1]:
                            p_r_tmp = re.sub("一", "-", p_r[0])
                            p_r_tmp += "月"
                            store_list.append(p_r_tmp)
                        elif "月" in p_r[0]:
                            p_r_tmp = re.sub("一", "-", p_r[0])
                            store_list.append(p_r_tmp)
                        elif len(re.compile("18").findall(p_r[0])) > 0:
                            store_list.append("零下18度冷冻保存")
                        elif len(re.compile("^\d").findall(p_r[0])) > 0:
                            store_list.append(p_r[0] + "度保存")
                        else:
                            p_r_tmp = re.sub("^-","零下",p_r[0])
                            store_list.append(p_r_tmp + "度保存")
        if len(exp_list) > 1:
            res_list = []
            for s,e in zip(store_list,exp_list):
                res_list.append(s + e)
                if len(res_list) > 1:
                    return ",".join(res_list)
        else:
            for s,e in zip(store_list,exp_list):
                result_list.append(s + e)

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    # pattern = r'(\d+\D+[-到至]\D*\d+\D+[\d一-十]+个?[月天]\W?\D*\d+\D+[-到至]\D*\d+\D+[\d一-十]+个?[月天])'
    # for texts in texts_list:
    #     for text in texts:
    #         p_res = get_info_by_pattern(text, pattern)
    #         if len(p_res) > 0 and "无理由" not in text and "退" not in text:
    #             return p_res[0]

    pattern = "[质保]期\W?(\d+个?[天月年])"
    for texts in texts_list:
        text_str = "".join(texts)
        p_res = re.compile(pattern).findall(text_str)
        if len(p_res) > 0:
            if len(re.compile(r'20[12]\d年[01]?\d月[0123]?\d日?').findall(kv[k])) > 0:
                continue
            result_list.append(p_res[0])

    pattern = r'(^|\W)([12]年|\d+个月|[一二三四五六七八九十]+个月|\d+天)$'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "无理由" not in text and "退" not in text and "天内" not in text:
                p_res = p_res[0]
                result_list.append(p_res[1])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

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
            if d_res > 1 and d_res < 367:
                return str(d_res) + "天"

    date_list = list(set(date_list))
    date_list.sort(reverse=True)
    if len(date_list) >=2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y%m%d")
        df = datetime.datetime.strptime(date_list[-1], "%Y%m%d")
        d_res = (d0 - df).days
        if d_res > 1 and d_res < 367:
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
            if d_res > 1 and d_res < 367:
                return str(d_res) + "天"

    date_list = list(set(date_list))
    date_list.sort(reverse=True)
    if len(date_list) >= 2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y年%m月%d日")
        df = datetime.datetime.strptime(date_list[-1], "%Y年%m月%d日")
        d_res = (d0 - df).days
        if d_res > 1 and d_res < 367:
            return str(d_res) + "天"

    return "不分"

def category_rule_134(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    type = "不分"
    taste = "不分"
    EXP = "不分"
    ingredients = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [],["FKO","Aji", "Aij", "贝贝", "遇见",
                                                                        "好麦", "松小贝", "inm", "OCOCO","全家",
                                                                        "卖吧","AYK","鲜吃","绿活","轻态","EURO"], [])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("年年西", "年年酉", brand_1)
    brand_1 = re.sub("马焙盒烘", "盒马烘焙", brand_1)
    brand_1 = re.sub("HPES六合信", "HOPES六合信", brand_1)
    brand_1 = re.sub("EURO","欧乐宾",brand_1,re.IGNORECASE)

    if ingredients == "不分":
        ingredients = get_ingredients(dataprocessed, datasorted)
    if ingredients == "不分":
        ingredients_list = get_info_list_by_list([[product_name]],Ingredients_list)
        if len(ingredients_list) > 0:
            ingredients = "，".join(ingredients_list)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐", 0)

    # datasorted_formated = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("送你", "迷你", product_name)
    product_name = re.sub("泡美", "泡芙", product_name)
    product_name = re.sub("草萄", "草莓", product_name)
    product_name = re.sub("订糕", "打糕", product_name)
    product_name = re.sub("剪越莓", "蔓越莓", product_name)
    product_name = re.sub("布工", "布丁", product_name)

    product_name = re.sub("^森林蛋糕", "黑森林蛋糕", product_name)
    product_name = re.sub("^[^纯清鸡焗老鲜干]蛋糕", "蛋糕", product_name)

    product_name = re.sub("^\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)
    product_name = re.sub("\d+[gG克%]?$", "", product_name)

    type = get_type(datasorted, product_name)

    taste = get_taste(datasorted, product_name)
    EXP = get_EXP(dataprocessed, datasorted)
    exp_res = re.compile("\d{4,}").findall(EXP)
    if len(exp_res) > 0:
        for long_num in exp_res:
            if len(long_num) in [4, 5]:
                long_num_sub = long_num[:2] + "度" + long_num[2:]
                EXP = re.sub(long_num, long_num_sub, EXP)

    EXP = re.sub("常漏","常温",EXP)
    EXP = re.sub("^\W+", "", EXP)
    if len(re.compile("^18[度Cc]?\D").findall(EXP)) > 0:
        EXP = re.sub("^18[度Cc]?", "零下18度", EXP)

    result_dict['info1'] = taste
    result_dict['info2'] = ingredients
    result_dict['info3'] = EXP
    result_dict['info4'] = type
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
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_2\149-速冻食品'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3039104"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_134(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)