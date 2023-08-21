import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/126_brand_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/126_taste_list",encoding="utf-8").readlines())]
Ingredients_list_ori = [i.strip() for i in open("Labels/126_ingredients_list",encoding="utf-8").readlines()]
Ingredients_list = []
for line in Ingredients_list_ori:
    Ingredients_list.extend(re.split("[^\-0-9a-zA-Z\u4e00-\u9fa5]",line))
Ingredients_list = set(Ingredients_list)
if "" in Ingredients_list:
    Ingredients_list.remove("")
Ingredients_list = list(Ingredients_list)
Ingredients_list.sort(key=len,reverse=True)

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

PRELIST = []

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

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    Taste_list_PLUS = Taste_list.copy()
    for taste in Taste_list:
        if "味" not in taste:
            Taste_list_PLUS.append(taste + "味")
    result = get_info_list_by_list_taste([[product_name,],], Taste_list_PLUS)
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
        # result = list(set(result))
        return "".join(result)

def get_type(texts_list,product_name,ingredients):
    type = "不分"
    shape = "不分"

    pattern_1 = "即食|调味|味附"
    pattern_2 = "夹心|三明治"
    pattern_3 = "[烤炒]海苔|寿司|手卷|拌饭|海苔碎"
    pattern_4 = "海\w卷"

    flag_1 = False
    flag_2 = False
    flag_3 = False
    flag_4 = False

    for texts in texts_list:
        for text in texts:
            # if not flag_1:
            #     p_res = get_info_by_pattern(text, pattern_1)
            #     if len(p_res) > 0:
            #         flag_1 = True

            if not flag_2:
                p_res = get_info_by_pattern(text, pattern_2)
                if len(p_res) > 0:
                    flag_2 = True

            if not flag_3:
                p_res = get_info_by_pattern(text, pattern_3)
                if len(p_res) > 0:
                    flag_3 = True

            if not flag_4:
                p_res = get_info_by_pattern(text, pattern_4)
                if len(p_res) > 0:
                    flag_4 = True

    if flag_2:
        shape = "夹心"
        type = "多味即食海苔"
    elif flag_3:
        shape = "不分"
        type = "烹饪用烤、炒海苔"
    else:
        if ingredients != "不分":
            type = "多味即食海苔"
        else:
            type = "纯即食海苔"

        if "卷" in product_name or flag_4:
            shape = "卷"
        else:
            shape = "片"

    if "卷" in product_name and "夹心" not in product_name:
        shape = "卷"

    return type,shape

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
    pattern_text = "[、，,]|干燥|产品类型|工艺|海苔上"
    pattern_pres = "[的用勿入在]|只选|每日海苔$|^\w海苔$"
    result_list = []
    result_list_tmp = []
    pattern_1 = "([^烤炒\W]+海苔[片卷碎脆]*|[^烤炒\W]*海苔\w+[卷碎脆]+|\w*海苔寿司|\w*紫菜碎|\w*海苔天妇罗)($|\()"
    pattern_2 = "(\w+海苔[片卷碎脆]*)($|\()"
    pattern_3 = "([^烤炒\W]+海苔[片卷碎脆]*|[^烤炒\W]*海苔\w+[卷碎脆]+)"
    pattern_4 = "([^烤炒\W]+海[苦台茗][片卷碎脆]*|[^烤炒\W]*海苔\w+[卷碎脆]+)"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("海[苦台茗苔]").findall(kv[k])) > 0:
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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 and p_res[0] not in ["调味海苔"]:
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
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 and p_res[0] not in ["调味海苔"]:
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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 and p_res[0] not in ["调味海苔"]:
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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 and p_res[0] not in ["每日海苔"]:
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

def get_brand_list_test(texts_list):
    brand_1_list = []
    brand_2 = []
    for texts in texts_list:
        for text in texts:
            for b1 in Brand_list_1:
                if b1.upper() in text or b1.title() in text:
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
                if (ingredient in Ingredients_list):
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

    ingredients = [[i for i in j if i in Ingredients_list] for j in ingredients]
    ingredients.sort(key=len,reverse=True)
    # ingredients_list 认为是顺序可靠的，ingredients_list_bak认为内容是可靠且完整的
    ingredients_list = []
    best_score = 0
    for ingredient in ingredients:
        score = 0
        for i in ingredient:
            if i in Ingredients_list:
                score += 1
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


    result = insertList(ingredients_list, ingredients_list_bak)
    # result = sorted(list(set(result)), key=result.index)

    if len(result) > 0:
        result = "，".join(result)
    else:
        result = "不分"

    return result



def category_rule_126(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    type_1 = "不分"
    shape = "不分"
    taste = "不分"
    inside = "不分"
    package = "不分"
    package_type = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,["金添动漫","野铺子"],["V2000","十足","Hala","a1","ZEK"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("满之津", "澫之津", brand_1)
    brand_1 = re.sub("小茗家", "小苔家", brand_1)


    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐", 0, min_num = 0.1)

    # datasorted = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("艺麻", "芝麻", product_name)
    product_name = re.sub("海[^苔]片", "海苔片", product_name)
    product_name = re.sub("海[^苔]卷", "海苔卷", product_name)
    product_name = re.sub("海[^苔]碎", "海苔碎", product_name)
    product_name = re.sub("夹心[髓能]", "夹心脆", product_name)
    product_name = re.sub("海苔[髓能]", "海苔脆", product_name)
    product_name = re.sub("橄?榄油", "橄榄油", product_name)
    product_name = re.sub("满之津", "澫之津", product_name)
    product_name = re.sub("[夹来央][心山]?海\w$", "夹心海苔", product_name)
    product_name = re.sub("^[心山芯]海[苔台茗苦]$", "夹心海苔", product_name)
    product_name = re.sub("海$", "海苔", product_name)
    product_name = re.sub("海[台茗苦]", "海苔", product_name)

    product_name = re.sub("[产食]品名[称种]", "", product_name)
    product_name = re.sub("^品?名一?", "", product_name)
    product_name = re.sub("^味", "", product_name)

    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    inside = get_ingredients(dataprocessed, datasorted)
    if inside == "不分":
        inside_list = get_info_list_by_list([[product_name,],],Ingredients_list)
        for i in get_info_list_by_list(datasorted,Ingredients_list):
            if i not in inside_list:
                inside_list.append(i)
        if len(inside_list) > 0:
            inside = "，".join(inside_list)
    type_1, shape = get_type(datasorted, product_name, inside)
    taste = get_taste(datasorted, product_name)
    if taste.replace("味","") in inside or len(taste) > 6:
        taste = "不分"

    if product_name == "不分":
        tmp_pre = ""
        if taste != "不分":
            if "味" not in taste:
                tmp_pre += taste + "味"
            else:
                tmp_pre += taste
        if shape == "夹心":
            tmp_pre += "夹心"

        product_name = tmp_pre + "海苔"

    # package = get_package(base64strs)
    package = get_package_126(base64strs)

    if capcity_2 != "不分":
        package_type = "独立包装"
    else:
        package_type = "非独立包装"

    result_dict['info1'] = taste
    result_dict['info2'] = package
    result_dict['info3'] = type_1
    result_dict['info4'] = inside
    result_dict['info5'] = package_type
    result_dict['info6'] = shape
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
    root_path = r'D:\Data\商品识别\stage_2\149-速冻食品'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3039104"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_126(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)