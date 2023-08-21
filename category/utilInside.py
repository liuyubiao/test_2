from util import get_info_by_pattern,isIngredient
import re


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

def insertList(result,insertingList,Ingredients_list):
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

def insertList_bak(result,insertingList,Ingredients_list):
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

def get_ingredients_list(texts_list,Ingredients_list):
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

            if index >= 2 :
                if ":" in text:
                    tmp_bak_str += text.split(":")[-1]
                else:
                    tmp_bak_str += text
        if len(tmp) > 0:
            result.append(tmp)
            result_bak.append([i for i in re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\(\)]", tmp_bak_str) if isIngredient(i)])

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

def get_ingredients(kvs_list, texts_list,Ingredients_list):
    pattern = r'\w*配[料科]表?$|^[料科]表?$'
    pattern_pre = r'\w*配[料科]表?\W?$|^[料科]表?\W?$'
    ingredients = []
    ingredients_group = []
    p = re.compile(pattern)
    for kvs in kvs_list:
        group = []
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    ingredients.append(re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\(\)]", kv[k]))
                    group.append([k,re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\(\)]", kv[k])])
        if len(group) > 1:
            ingredients_group.append(group)

    if len(ingredients_group) > 0:
        ingredients_group.sort(key=len,reverse=True)
        res_str = ""
        return_flags = []
        for g in ingredients_group[0]:
            tmp_list = [i for i in g[1] if isIngredient(i)]
            tmp_list_limit = [i for i in tmp_list if i in Ingredients_list]
            if tmp_list_limit != []:
                res_str += g[0] + ":" + ",".join(tmp_list) + "\n"

            return_flag = 1 if len(tmp_list_limit) > 0 else 0
            return_flags.append(return_flag)
        if sum(return_flags) > 1:
            return res_str

    if len(ingredients) == 0:
        for texts in texts_list:
            for index, text in enumerate(texts):
                p_res_pre = get_info_by_pattern(text, pattern_pre)
                total_len = len(texts)
                if len(p_res_pre) > 0:
                    tmp_str = ""
                    for i in [1,2,3,4]:
                        if index + i >= 0 and index + i < total_len:
                            tmp_list,_ = get_ingredients_list([[texts[index + i],],],Ingredients_list)
                            if len(tmp_list) > 0:
                                tmp_str += texts[index + i]
                    if tmp_str != "":
                        ingredients.append(re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\(\)]", tmp_str))

    ingredients = [[i for i in j if isIngredient(i) and len(i) < 7] for j in ingredients]
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

    ingredients_list_bak,ingredients_list_bak_strs = get_ingredients_list(texts_list,Ingredients_list)
    if len(ingredients_list) == 0 :
        ingredients_list_tmp = ingredients_list_bak.copy()
        ingredients_list_tmp.extend(ingredients_list_bak_strs)
        ingredients_list_tmp = sorted(ingredients_list_tmp,key=len,reverse=True)

        if len(ingredients_list_tmp) > 0 and ingredients_list_tmp[0] != "":
            ingredients_list = ingredients_list_tmp[0].copy()

    ingredients_list = [i for i in ingredients_list if isIngredient(i)]

    result = insertList(ingredients_list, ingredients_list_bak,Ingredients_list)
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