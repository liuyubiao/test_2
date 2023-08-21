import re
from collections import Counter
from util import isNutritionalTable,get_info_by_pattern

def get_capacity_keyword(kvs_list,mode,unit = "G|g|克|[千干]克|kg|KG|斤|公斤"):
    kvs_list.sort(key=len, reverse=False)
    pattern = r'(净含量?|净重|^含?量$|^净\w量$|[Nn][Ee][Tt][Ww]|重量)'
    result_list = []
    p = re.compile(pattern)
    if mode == 1 or mode == 2:
        unit += "|m|M|毫"
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\s?({})'.format(unit)
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克","kg","kG","Kg","KG","斤","公斤","干克","升","L"]:
                                if float(p_res[0]) <= 10:
                                    if p_res[1] == "干克":
                                        result_list.append(p_res[0] + "千克")
                                    else:
                                        result_list.append(p_res[0] + p_res[1])
                            else:
                                if float(p_res[0]) < 5000:
                                    if p_res[1] in ["m","M","毫"]:
                                        result_list.append(p_res[0] + "毫升")
                                    else:
                                        result_list.append(p_res[0] + p_res[1])

    result_list.sort(key=len, reverse=True)
    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    pattern = r'(规格)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\s?({})'.format(unit)
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0":
                            if p_res[1] in ["千克","kg","kG","Kg","KG","斤","公斤","干克","升","L"]:
                                if float(p_res[0]) <= 10:
                                    return p_res[0] + p_res[1]
                            else:
                                if float(p_res[0]) < 5000:
                                    return p_res[0] + p_res[1]

    return "不分"

def get_Capacity_texts(texts_list,unit = "G|g|克|千克|kg|KG|Kg",min_num = 10):
    pattern = r'(\d+\.?\d*)\s?({})'.format(unit)
    p = re.compile(pattern)
    for texts in texts_list:
        tmp_list = []
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0 and float(p_res[0][0]) < 5000 and float(p_res[0][0]) >= min_num:
                if not isNutritionalTable(text, texts, index):
                    continue
                if "每份" in text:
                    continue
                if p_res[0][1] in ["kg","KG","Kg","千克","升","L"] and float(p_res[0][0]) > 30:
                    continue
                tmp_list.append(p_res[0][0] + p_res[0][1])

        if len(tmp_list) == 1:
            return tmp_list[0]

    result_list = []
    p = re.compile(pattern)
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res = p.findall(text)
            if len(p_res) > 0:
                if not isNutritionalTable(text, texts, index):
                    continue
                if "每份" in text:
                    continue
                p_res = p_res[0]
                if p_res[1] in ["Kg","kg","KG","千克","升","L"]:
                    if float(p_res[0]) <= 30:
                        result_list.append(p_res[0] + p_res[1])
                else:
                    if float(p_res[0]) < 5000 and "." not in p_res[0] and float(p_res[0]) >= min_num:
                        result_list.append(p_res[0] + p_res[1])

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    return count[0][0]

def get_Capacity_amount(kvs_list,texts_list,unit,num_sample,mode = 0,min_num = 1):
    bracket_pattern = "[千kK]?[克gG]"
    if mode == 1:
        bracket_pattern = "[Mm毫]?[lL升]"
    elif mode == 2:
        bracket_pattern = "[千kKMm毫]?[克gGlL升]"
    elif mode == 2.5:
        bracket_pattern = "[Mm毫]?[克gGlL升]"

    pattern = r'(净含量?|净重|[Nn][Ee][Tt][Ww]|重量|规格)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    if len(re.compile("\d+%s\d+%s"%(bracket_pattern,bracket_pattern)).findall(kv[k])) > 0 or "装" in kv[k]:
                        continue
                    pattern = r'(\d+\.?\d*)\s?(%s)(\d+)[\u4e00-\u9fa5]{0,2}\)?$'%(unit)
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        if p_res[0][0] != "0" and p_res[2][0] != "0":
                            if p_res[1] in ["千克", "kg", "KG", "斤", "公斤", "升", "L"]:
                                if float(p_res[0]) <= 30 and float(p_res[2]) <= 30:
                                    return str(int(float(p_res[0]) * int(p_res[2]))) + p_res[1], p_res[0] + p_res[1] + "*" + p_res[2]
                            else:
                                if float(p_res[0]) < 5000 and float(p_res[0]) >= min_num and float(p_res[2]) <= 50:
                                    return str(int(float(p_res[0]) * int(p_res[2]))) + p_res[1], p_res[0] + p_res[1] + "*" + p_res[2]

    pattern = r'^(净含量?|净重|^[\u4e00-\u9fa5]?含量$|[Nn][Ee][Tt][Ww]|重量):?$'
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res_1 = get_info_by_pattern(text, pattern)
            total_len = len(texts)
            if len(p_res_1) > 0:
                for i in [-3, -2, -1, 1, 2, 3]:
                    if index + i >= 0 and index + i < total_len:
                        pattern_tmp = r'(\d+\.?\d*)\s?(%s)(\d+)[\u4e00-\u9fa5]{0,2}\)?$'%(unit)
                        p_res_tmp = re.compile(pattern_tmp).findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            if len(re.compile("\d+%s\d+%s"%(bracket_pattern,bracket_pattern)).findall(texts[index + i])) > 0 or "装" in texts[index + i]:
                                continue
                            p_res_tmp = p_res_tmp[0]
                            if p_res_tmp[0][0] != "0" and p_res_tmp[2][0] != "0":
                                if p_res_tmp[1] in ["千克", "kg", "KG", "斤", "公斤", "升", "L"]:
                                    if float(p_res_tmp[0]) <= 30 and float(p_res_tmp[2]) <= 30:
                                        return str(int(float(p_res_tmp[0]) * int(p_res_tmp[2]))) + p_res_tmp[1], p_res_tmp[0] + p_res_tmp[1] + "*" + p_res_tmp[2]
                                else:
                                    if float(p_res_tmp[0]) < 5000 and float(p_res_tmp[0]) >= min_num and float(p_res_tmp[2]) <= 50:
                                        return str(int(float(p_res_tmp[0]) * int(p_res_tmp[2]))) + p_res_tmp[1], p_res_tmp[0] + p_res_tmp[1] + "*" + p_res_tmp[2]

    pattern = r'\d+\.?\d*\D*%s\D{0,3}\d+\D?[%s]装?\)?'%(bracket_pattern,num_sample)
    pattern_2 = r'(\d+\.?\d*)\W*(%s)\D{0,3}(\d+)\D?[%s]装?\)?'%(unit,num_sample)
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            if len(re.split("[*xX]\d",text)) > 2:
                continue
            if "每份" in text:
                continue
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    unit = p_res_2[1]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if float(p_res_2[0]) >= min_num and float(p_res_2[0]) <= 5000 and float(p_res_2[2]) < 201:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0] :
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "", p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*%s[*xX]\d+[%s\)]?'%(bracket_pattern,num_sample)
    pattern_2 = r'(\d+\.?\d*)\W*(%s)[*xX](\d+)[%s\)]?'%(unit,num_sample)
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            if len(re.split("[*xX]\d",text)) > 2:
                continue
            p_res = p.findall(text)
            if len(p_res) > 0:
                if len(re.compile("\d+\.\d+克\([\dg]\)").findall(text)) > 0:
                    continue
                if "(9)" in text:
                    continue
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    unit = p_res_2[1]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if float(p_res_2[0]) >= min_num and float(p_res_2[0]) <= 5000:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[2]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+[%s]?[*xX]\d+\.?\d*\D*%s'%(num_sample,bracket_pattern)
    pattern_2 = r'(\d+)[%s]?[*xX](\d+\.?\d*)\W*(%s)'%(num_sample,unit)
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            if len(re.split("[*xX]\d", text)) > 2:
                continue
            p_res = p.findall(text)
            if len(p_res) > 0:
                if len(re.compile("\d+\.\d+克\([\dg]\)").findall(text)) > 0:
                    continue
                if "(9)" in text:
                    continue
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    unit = p_res_2[2]
                    if len(p_res_2) == 3:
                        if p_res_2[0] != "0" and p_res_2[0] != "":
                            if float(p_res_2[0]) >= min_num and float(p_res_2[0]) <= 5000:
                                if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                    return ("%.1f%s" % (float(p_res_2[0]) * float(p_res_2[1]), unit)), re.sub(u"\)", "",p_res[0])
                                else:
                                    return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*%s\D{0,3}\d+\D*\)$'%(bracket_pattern)
    pattern_2 = r'(\d+\.?\d*)\W*(%s)\D{0,3}(\d+)\D*'%(unit)
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                if len(re.compile("\d+\.\d+克\([\dg]\)").findall(text)) > 0:
                    continue
                if "(9)" in text or "(0)" in text:
                    continue
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    return "不分", re.sub(u"\)", "", p_res[0])

    return "不分","不分"

def get_Capacity_amount_bak(texts_list,num_sample = "包袋盒罐支片只个张"):
    p_bak = re.compile(r'(\d+)(\s?[%s]装)'%(num_sample))
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1]

    p_bak = re.compile(r'(\d+)([%s])\w*(装)$'%(num_sample))
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return p_res[0] + p_res[1] + p_res[2]

    p_bak = re.compile(r'内[装含](\d+)(小?[%s])'%(num_sample))
    for texts in texts_list:
        for text in texts:
            p_res = p_bak.findall(text)
            if len(p_res) > 0:
                p_res = p_res[0]
                if int(p_res[0]) <= 200:
                    return "内装"+ p_res[0] + p_res[1]
    return "不分"

def get_Capacity_keyword_bak(texts_list,mode = 0):
    bracket_pattern = "[千Kk]?[克gG]"
    if mode == 1:
        bracket_pattern = "[毫Mm]?[lL升]"
    elif mode == 2:
        bracket_pattern = "[毫Mm千kK]?[克gGlL升]"
    pattern = r'^(净含量?|净重|^含量$|[Nn][Ee][Tt][Ww]|重量)\W?$'
    num = "不分"
    for texts in texts_list:
        for index,text in enumerate(texts):
            p_res_1 = get_info_by_pattern(text, pattern)
            total_len = len(texts)
            if len(p_res_1) > 0:
                for i in [1,2,-1,-2]:
                    if index + i >=0 and index + i <total_len:
                        p_res_tmp = re.compile("^[\d\.]{1,4}%s$"%(bracket_pattern)).findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            return p_res_tmp[0]

                for i in [1,2,-1,-2]:
                    if index + i >=0 and index + i <total_len:
                        p_res_tmp = re.compile("^[\d\.]{1,4}$").findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            if p_res_tmp[0] == ".":
                                continue
                            if mode == 0:
                                if "." in p_res_tmp[0] or len(p_res_tmp[0]) == 1:
                                    return p_res_tmp[0] + "千克"
                                else:
                                    return p_res_tmp[0] + "克"
                            if mode == 1:
                                if "." in p_res_tmp[0] or len(p_res_tmp[0]) == 1:
                                    return p_res_tmp[0] + "升"
                                else:
                                    return p_res_tmp[0] + "毫升"
    return num

def get_capacity_lastchance(kvs_list,texts_list,mode = 0):
    tmp_unit_1 = "克"
    tmp_unit_2 = "千克"
    if mode == 1 or mode == 2.5:
        tmp_unit_1 = "毫升"
        tmp_unit_2 = "升"

    kvs_list.sort(key=len, reverse=False)
    pattern = r'(净含量?|净重|^含量$|[Nn][Ee][Tt][Ww]|重量)'
    result_list = []
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'^\d+\.?\d*$'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        if p_res[0][0] != "0":
                            if len(p_res[0]) == 1 or "." in p_res[0]:
                                result_list.append(p_res[0] + tmp_unit_2)
                            elif len(p_res[0]) > 1:
                                result_list.append(p_res[0] + tmp_unit_1)
    result_list.sort(key=len,reverse=True)
    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'^\d+\.?\d*'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        if p_res[0][0] != "0":
                            if len(p_res[0]) == 1 or "." in p_res[0]:
                                result_list.append(p_res[0] + tmp_unit_2)
                            elif len(p_res[0]) > 1:
                                result_list.append(p_res[0] + tmp_unit_1)
    result_list.sort(key=len,reverse=True)
    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    pattern = r'(净含量?|净重|^含量$|[Nn][Ee][Tt][Ww]|重量)\W?(\d+\.?\d*)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                p_res = p_res[0]
                if p_res[1][0] != "0":
                    if len(p_res[1]) == 1 or "." in p_res[1]:
                        result_list.append(p_res[1] + tmp_unit_2)
                    elif len(p_res[1]) > 1:
                        result_list.append(p_res[1] + tmp_unit_1)

    result_list.sort(key=len, reverse=True)
    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    pattern = r'(净含量?|净重|^含量$|[Nn][Ee][Tt][Ww]|重量)'
    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res_key = get_info_by_pattern(text, pattern)
            total_len = len(texts)
            if len(p_res_key) > 0:
                for i in [1, 2, -1, -2]:
                    if index + i >= 0 and index + i < total_len:
                        p_res = re.compile("^(\d{1,3})[gG克]?$").findall(texts[index + i])
                        if len(p_res) > 0:
                            if len(p_res[0]) == 1 or "." in p_res[0]:
                                result_list.append(p_res[0] + tmp_unit_2)
                            elif len(p_res[0]) > 1:
                                result_list.append(p_res[0] + tmp_unit_1)

    result_list.sort(key=len, reverse=True)
    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return "不分"

def get_capacity(dataprocessed,datasorted,unit,num_sample,mode,min_num = 10):
    capcity_1 = get_capacity_keyword(dataprocessed,mode, unit)
    unit = re.sub("[元开]", "", unit)
    capcity_1_bak, capcity_2 = get_Capacity_amount(dataprocessed,datasorted,unit,num_sample,mode,min_num/10.)
    if capcity_1_bak != "不分":
        if capcity_1 == "不分":
            capcity_1 = capcity_1_bak
        elif re.compile("\d+\.?\d*").findall(capcity_1)[0] in capcity_2:
            capcity_1 = capcity_1_bak
    if capcity_1 == "不分":
        capcity_1 = get_Capacity_texts(datasorted,unit,min_num)
    if capcity_1 == "不分":
        capcity_1 = get_Capacity_keyword_bak(datasorted,mode)
    if capcity_2 != "不分":
        try:
            num_0 = re.compile("\d+\.?\d*").findall(capcity_1)[0]
            num_1, num_2 = re.compile("\d+\.?\d*").findall(capcity_2)
            if float(num_1) == 0:
                capcity_2 = "不分"
            elif float(num_0) * float(num_2) == float(num_1):
                capcity_1 = capcity_1.replace(num_0, num_1)
            elif float(num_1) * float(num_2) != float(num_0) and float(num_0) != float(num_1) and float(num_0) != float(num_2):
                capcity_2 = "不分"
        except:
            pass
    if capcity_2 == "不分":
        capcity_2 = get_Capacity_amount_bak(datasorted,num_sample)

    if capcity_1 == "不分":
        capcity_1 = get_capacity_lastchance(dataprocessed,datasorted,mode)
    return capcity_1,capcity_2