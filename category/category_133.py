import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/133_brand_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/133_taste_list",encoding="utf-8").readlines())]
Ingredients_list_ori = [i.strip() for i in open("Labels/133_ingredients_list",encoding="utf-8").readlines()]
Ingredients_list = []
for line in Ingredients_list_ori:
    Ingredients_list.extend(re.split("[^\-0-9a-zA-Z\u4e00-\u9fa5]",line))
Ingredients_list = set(Ingredients_list)
Ingredients_list.remove("")
Ingredients_list = list(Ingredients_list)
Ingredients_list.sort(key=len,reverse=True)
# 通常来看需要20个非通用属性
LIMIT_NUM = 20

def sort_keyWord(unsort_list,key_words):
    tmp_dict = {}
    for info in unsort_list:
        if info not in tmp_dict.keys():
            tmp_dict[info] = 0
        else:
            continue
        for kw in key_words:
            if kw in info:
                tmp_dict[info] += 1

    sorted_list = sorted(unsort_list,key=lambda x: tmp_dict[x],reverse=True)
    return sorted_list

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    Taste_list_plus = Taste_list.copy()
    Taste_list_plus.extend(["黄油","牛肉","可可"])
    result = get_info_list_by_list([[product_name,],], Taste_list_plus)
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
        result = list(set(result))
        return "".join(result)

def get_inside(texts_list,product_name):
    if "面包干" in product_name or "面包脆" in product_name:
        return "面包脆"

    if "切" in product_name or "片" in product_name or "吐司" in product_name:
        return "切片"

    tmp_list = []
    for texts in texts_list:
        for text in texts:
            if "面包干" in text or "面包脆" in text:
                return "面包脆"
            if "厚切" in text or "吐司" in text or len(re.compile("[叶时]司|吐[回饲]").findall(text)) > 0:
                tmp_list.append("切片")
    if len(tmp_list) > 0:
        return "切片"

    pattern = "调理面包|肉松|香松|肠|火腿|肉|培根|虾|翅|丸|热狗|豆沙|豆蓉|红豆|绿豆|糖纳豆|果酱|果泥|巧克力酱|沙拉酱|奶酪酱|蛋黄酱|芝士酱|果脯|葡萄干|蓝莓干|椰蓉|椰丝|核桃仁|榛子|瓜子仁|巧克力豆|芝麻|燕麦片|奶油|酸奶"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "有馅"
    return "不分"

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
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+[面餐]包[干脆棒]?|\w+列巴|\w+切片|\w+吐司|\w+甜甜[圈围]|\w+软欧包?|\w+汉堡|\w+麻花|\w*手撕棒|\w+方酥[圈围]?|\w+法棍|\w+生乳包|\w+三明治|\w+铜锣烧)($|\()"
    pattern_2 = "(\w+[^背\W]包|\w+[^真好\W]棒|\w+[^图照\W]片|\w+杉木)($|\()"
    pattern_3 = "\w+面包[干脆]?|\w+列巴|\w+切片|\w+吐司|\w+甜甜[圈围]"

    pattern_tmp = "\w+包|列巴|切?片|吐司|甜甜[圈围]|汉堡|麻花|手撕棒|厚切|方酥"
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
                if len(re.compile("有|调理|软式|发现|用好|专做").findall(p_res[0])) ==0 and len(re.compile("[、，]|类型").findall(text)) ==0:
                    result_list.append(p_res[0])

    result_list = sort_keyWord(result_list,["厚切","吐司","面包","餐包","列巴","甜甜圈","麻花"])
    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile("有|发现|用好|专做").findall(p_res[0])) ==0 and len(re.compile("[、，]|包装|类型").findall(text)) ==0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if len(re.compile("有|发现|用好|专做").findall(p_res[0])) ==0 and len(re.compile("[、，]|类型").findall(text)) ==0:
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
            if text in ["海苔",]:
                continue

            for ingredient in re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\\/]", text):
                if ingredient in tmp:
                    continue
                if (ingredient in Ingredients_list and ingredient != "糖") or "固态复合调味料" in ingredient:
                    tmp.append(ingredient)
                    index += 1

            # if index >= 2 :
            #     if ":" in text:
            #         tmp_bak_str += text.split(":")[-1]
            #     else:
            #         tmp_bak_str += text
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

    # ingredients = [[i for i in j if isIngredient(i) and i in Ingredients_list] for j in ingredients]
    # ingredients = [[sorted(list(set(i)),key=i.index) for i in ingredients]]
    ings_tmp = []
    for j in ingredients:
        ing_tmp = []
        for i in j:
            if isIngredient(i) and i in Ingredients_list and i not in ing_tmp:
                ing_tmp.append(i)
            elif i not in Ingredients_list and isIngredient(i) and i not in ing_tmp:
                for I in Ingredients_list:
                    if I in i and I not in ing_tmp and len(I) > 4:
                        ing_tmp.append(I)
                        break
        ings_tmp.append(ing_tmp)
    ingredients = ings_tmp
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
    result = [re.sub(".*核苷酸二钠", "5-呈味核苷酸二钠", i) for i in result]
    result = [re.sub(".*甲氧基苯氧基.*", "2-(4-甲氧基苯氧基)丙酸钠", i) for i in result]
    result = [re.sub("^用盐$", "食用盐", i) for i in result]
    result = [re.sub("围体复合", "固体复合", i) for i in result]
    # result = sorted(list(set(result)), key=result.index)

    if len(result) > 0:
        result = ",".join(result)
    else:
        result = "不分"

    return result

def get_EXP(kvs_list,texts_list):
    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    p_1 = re.compile(r'[0-9一-十]+个?[年天月]')
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    p_res_1 = p_1.findall(kv[k])
                    if len(p_res_1) > 0:
                        if len(re.compile(r'20[12]\d年[01]?\d月[0123]?\d日?').findall(kv[k])) > 0:
                            continue
                        return kv[k]

    pattern = "-?\d{0,2}[-至]\d+[度C]?以?下?\d+个?[月天]|零下\d+以?下?\d+个?[月天]|-\d+以?下?\d+个?[月天]"
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                tmp_list.append(p_res[0])
        if len(tmp_list) > 0:
            return ",".join(tmp_list)

    pattern = r'(\D+[12]年|^[12]年|\d+个月|[一-十]+个月|\d+天)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "无理由" not in text and "退" not in text:
                return p_res[0]

    pattern = r'20[12]\d[-\\/\s\.]?[01]\d[-\\/\s\.]?[0123][\d]'
    date_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                date_list.append(re.sub("\D","",p_res[0]))

    for ddate in date_list:
        try:
            d0 = datetime.datetime.strptime(ddate, "%Y%m%d")
        except:
            date_list.remove(ddate)

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
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "日" not in p_res[0]:
                    date_list.append(p_res[0] + "日")
                else:
                    date_list.append(p_res[0])

    for ddate in date_list:
        try:
            d0 = datetime.datetime.strptime(ddate, "%Y年%m月%d日")
        except:
            date_list.remove(ddate)

    date_list = list(set(date_list))
    date_list.sort(reverse=True)
    if len(date_list) >= 2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y年%m月%d日")
        df = datetime.datetime.strptime(date_list[-1], "%Y年%m月%d日")
        d_res = (d0 - df).days
        if d_res > 1:
            return str(d_res) + "天"

    return "不分"

def TextFormat(texts_list):
    full_text = []
    for texts in texts_list:
        l = len(texts)
        if l == 0:
            continue
        txt_tmp = "#" + "#".join(texts) + "#"
        if "#面#包#" in txt_tmp or "#吐#司#" in txt_tmp:
            txt_tmp = txt_tmp.replace("#面#包#","#面包#")
            txt_tmp = txt_tmp.replace("#吐#司#", "#吐司#")
            texts = txt_tmp[1:-1].split("#")
        tmp_str = ""
        texts_tmp = []
        for index, txt in enumerate(texts):
            if len(re.compile("^[a-zA-Z0-9\W]+$").findall(txt)) > 0:
                continue
            texts_tmp.append(txt)

        for index,txt in enumerate(texts_tmp):
            split_flag = "&"
            txt_tmp = ""
            if txt in ["面包", "吐司", "切片", "列巴", "软欧","生吐司","软欧包","甜甜圈","汉堡","小汉堡","面包干","面包脆", "餐包","味餐包","味面包","味吐司"]:
                for ii in range(index):
                    if index- ii - 1 < 0 :
                        break
                    if len(re.compile("^[\u4e00-\u9fa5]$").findall(texts_tmp[index- ii - 1])) > 0:
                        txt_tmp = texts_tmp[index- ii - 1] + txt
                    else:
                        if ii == 0:
                            if len(re.compile("^[\u4e00-\u9fa5]{2,4}$").findall(texts_tmp[index- ii - 1])) > 0:
                                txt_tmp = texts_tmp[index- ii - 1] + txt
                                break
                        break
                if len(txt_tmp.replace(txt,"")) > 1:
                    txt = txt_tmp
            tmp_str += txt
            if index != l - 1:
                tmp_str += split_flag
        full_text.append(tmp_str.split("&"))
    return full_text

def category_rule_133(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    type = "不分"
    taste = "不分"
    package = "不分"
    bags = "无"
    EXP = "不分"
    ingredients = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    datasorted = [[re.sub("[叶吐][司词饲]", "吐司", str) for str in strs] for strs in datasorted]

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, ["多菲角",], ["蜜甜","RUBY","全家","HIPP"], [])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    if ingredients == "不分":
        ingredients = get_ingredients(dataprocessed, datasorted)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐", 0)

    datasorted_formated = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed, datasorted_formated)

    product_name = re.sub("奇业籽", "奇亚籽", product_name)
    product_name = re.sub("手腩", "手撕", product_name)
    product_name = re.sub("[叶时]司", "吐司", product_name)
    product_name = re.sub("^司", "吐司", product_name)
    product_name = re.sub("吐[回饲]", "吐司", product_name)
    product_name = re.sub("[成饿]罗斯", "俄罗斯", product_name)
    product_name = re.sub("乳酸画", "乳酸菌", product_name)
    product_name = re.sub("奶醇", "奶酪", product_name)
    product_name = re.sub("甜甜围", "甜甜圈", product_name)
    product_name = re.sub("方酥围", "方酥圈", product_name)

    product_name = re.sub("^\w面包", "面包", product_name)
    product_name = re.sub("^\w吐司", "吐司", product_name)

    product_name = re.sub("杉木$", "杉木面包", product_name)

    product_name = re.sub("^\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    type = get_inside(datasorted, product_name)
    if type == "不分":
        if "酱" in ingredients or "馅" in ingredients:
            type = "有馅"
        else:
            if capcity_1 != "不分":
                num = float(re.compile("\d+\.?\d*").findall(capcity_1)[0])
                if num > 100 and num < 500:
                    type = "无馅大包"
                else:
                    type = "无馅小包"
            else:
                type = "有馅"

    taste = get_taste(datasorted, product_name)
    EXP = get_EXP(dataprocessed, datasorted)

    result_dict['info1'] = "非现烤"
    result_dict['info2'] = taste
    result_dict['info3'] = type
    result_dict['info4'] = ingredients
    result_dict['info5'] = EXP
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
        result_dict = category_rule_133(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)