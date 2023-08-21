import os
import re

from util import *
from glob import glob



LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/217_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/217_brand_list_2",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/217_type_list",encoding="utf-8").readlines())]
Fruit_list = [i.strip() for i in set(open("Labels/217_fruit_list",encoding="utf-8").readlines())]
Place_list = [i.strip() for i in set(open("Labels/217_place_list",encoding="utf-8").readlines())]
suffix_name_list = [i.strip() for i in set(open("Labels/217_suffix_name_list",encoding="utf-8").readlines())]

Spacial_productname = ["\w*花雕[酒王]$","\w+预调酒","\w+鸡尾酒","\w+露酒","\w+起泡酒"]

#提取产地
def get_place(texts_list,placeOrigin):
    '''
    提取产地
    提取依据：217定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：选项：法国、英国、美国等，如果是国产的给不分。
    :param texts_list: 有序文本列表
    :return:
    '''

    pattern = "("
    for i in Place_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"

    p_res = get_info_by_pattern(placeOrigin, pattern)
    if len(p_res) > 0:
        return p_res[0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

#提取分类、类型
def get_type_bak(texts_list):
    pattern = "(预调酒|鸡尾酒|露酒)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "不分",p_res[0]

    pattern = "(威士[忌忘]|伏特加|白兰地|朗姆酒|利口酒|力娇|金酒|杜松子酒|龙舌兰酒)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                p_res[0] = p_res[0].replace("威士忘","威士忌")
                return p_res[0],"洋烈酒"

    pattern = "(cognac|whisky|vodka|brandy|li[qo]ueur|te[qo]uila)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text.lower(), pattern)
            if len(p_res) > 0:
                if p_res[0][0] == "c":
                    return "干邑", "洋烈酒"
                elif p_res[0][0] == "w":
                    return "威士忌", "洋烈酒"
                elif p_res[0][0] == "v":
                    return "伏特加", "洋烈酒"
                elif p_res[0][0] == "b":
                    return "白兰地", "洋烈酒"
                elif p_res[0][0] == "l":
                    return "利口酒", "洋烈酒"
                elif p_res[0][0] == "t":
                    return "龙舌兰酒", "洋烈酒"

    pattern = "(G[Ii][Nn]|R[uU][Mm])"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if p_res[0][0] == "G":
                    return "金酒", "洋烈酒"
                elif p_res[0] == "R":
                    return "朗姆酒", "洋烈酒"

    pattern = "果酒"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "不分", "果酒"


    result_type_1 = "不分"
    result_type_2 = "不分"

    pattern = "("
    for i in Fruit_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result_type_1 = "果酒"
                result_type_2 = p_res[0] + "酒"

    pattern = "起泡酒"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result_type_2 = "起泡酒"

    pattern = "酸奶酒|奶酒"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result_type_2 = p_res[0]

    pattern = "配制酒"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result_type_2 = "配制酒"
                # result_type_1 = result_type_1 if result_type_1 != "不分" else "鸡尾酒"

    return result_type_2,result_type_1

#提取分类、类型
def get_type(texts_list):
    '''
    提取分类、类型
    提取依据：217定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    分类：
       1、封闭选项： 预调酒/鸡尾酒、洋烈酒、果酒、露酒、不分
       2、预调酒-鸡尾酒：以发酵酒、蒸馏酒或食用酒精为酒基，加入可食用或药食两用的辅料或食品添加剂，进行调配、混合或再加工制成的、已改变了其原酒基风格的饮料酒。预调酒的酒精含量通常为为3%-7%左右
       3、洋烈酒： 也可以称为国外蒸馏酒。
                   按制造原料可分为白兰地（brandy）、威士忌（whisky）和朗姆酒（rum）
                   白兰地以葡萄为原料。
                   威士忌以麦芽和谷类为原料。
                   朗姆酒则以甘蔗粮蜜为原料，一般是黑色和白色，瓶上通常有“Run”字样。
                   此外，还有以高纯酒精为基础酿制而成的杜松子酒（gin）和伏特加酒（vodka），
                         杜松子酒：为药用植物杜松子和食用酒精经串蒸或冷混而成。
                         伏特加酒：可分为纯酒精伏特加（中性酒精）和调香伏特加两大类
        4、果酒：用水果本身的糖分被酵母菌发酵成为酒精的酒，含有水果的风味与酒精，也叫果子酒。
        5、露酒：全称中含有“露酒”字样的酒。
        分类判断思路：
        1、根据包装上的描述和全称进行判断，分几种情况：
            1.1、预调酒-鸡尾酒：全称有“预调”、“鸡尾”字样的；全称既含洋烈酒字样，又含预调/鸡尾字样的，优先给“预调酒-鸡尾酒”。
            1.2、洋烈酒：如白兰地BRANDY、威士忌WHISKEY、伏特加VODKA、利口酒LIQUEUR、力娇酒LIQUEUR、朗姆酒RUM、金酒GIN、杜松子酒GIN、龙舌兰酒TEQUILA等就给“洋烈酒”，不能判断的给“其他”
            1.3、果酒：指除葡萄酒外的其他水果酒，如蓝莓酒、提子酒、梅酒、青梅酒、杨梅酒、石榴酒、苹果酒、山楂酒、桑椹酒、猕猴桃酒、草莓酒、木瓜酒、樱桃酒、柠檬酒、桃酒、荔枝酒、枣酒、树莓酒、枇杷酒、蜜桃酒等
            1.4、露酒：全称有“露酒”字样的，多为水果/花卉类酒
                       以葡萄酒为基酒，利用植物、动物以及食品添加剂等作为呈色、呈香、呈味的物质，采用浸渍、复蒸馏或直接添加法等特定的工艺，经过混合、调配、勾兑、贮藏、过滤等加工方法后改变了原酒基风格的饮料酒，也给“露酒”。
            1.5、不分：不能判断的给“不分”。
    类型：
        选项：白兰地/威士忌/伏特加/利口酒/力娇酒/朗姆酒/金酒/杜松子酒/龙舌兰酒/苹果酒/草莓酒/梅酒等
              根据包装上的描述和全称进行判断，分两种情况：
              1、洋烈酒类，给包装或描述上的全称，如白兰地就给“白兰地”；威士忌就给“威士忌”等等 。
              2、果酒类，给包装或描述上的全称，如苹果酒就给“苹果酒”，草莓酒就给“草莓酒”。
    “分类”与“类型”两段的逻辑关系：
                分类：预调酒/鸡尾酒；类型：不分
                分类：洋烈酒       类型：白兰地、威士忌、伏特加、利口酒、力娇酒、朗姆酒、金酒、杜松子酒、龙舌兰酒、其他(请注明)
                分类：果酒         类型：蓝莓酒、提子酒、梅酒、青梅酒、杨梅酒、石榴酒、苹果酒、山楂酒、桑椹酒、猕猴桃酒、草莓酒、木瓜酒、樱桃酒、柠檬酒、桃酒、荔枝酒、枣酒、树莓酒、枇杷酒、蜜桃酒、其他(请注明)
                分类：露酒         类型：不分
                分类：不分         类型：不分
    :param texts_list:
    :return:
    '''
    pattern = "(预调酒|鸡尾酒)"
    pattern1 = "(露酒)"
    pattern2 = "\d+.?\d+%vol"
    #根据酒精含量：预调酒的酒精含量通常为为3%-7%左右
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 :
                return "不分",'预调酒-鸡尾酒'
            else:
                p_res = get_info_by_pattern(text, pattern1)
                if len(p_res) > 0:
                    return "不分", '露酒'
                # else:
                #     p_res = get_info_by_pattern(text, pattern2)
                #     if len(p_res) > 0:
                #         alcohol = float(p_res[0].replace('%vol', '').replace(',', '.'))
                #         if alcohol >= 3 and alcohol <= 7:
                #             return "不分", '预调酒-鸡尾酒'

    pattern = "(威士[忌忘]|伏特加|白兰地|朗姆酒|利口酒|力娇|金酒|杜松子酒|龙舌兰酒)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                p_res[0] = p_res[0].replace("威士忘","威士忌")
                return p_res[0],"洋烈酒"

    pattern = "(cognac|whisky|vodka|brandy|li[qo]ueur|te[qo]uila)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text.lower(), pattern)
            if len(p_res) > 0:
                if p_res[0][0] == "c":
                    return "干邑", "洋烈酒"
                elif p_res[0][0] == "w":
                    return "威士忌", "洋烈酒"
                elif p_res[0][0] == "v":
                    return "伏特加", "洋烈酒"
                elif p_res[0][0] == "b":
                    return "白兰地", "洋烈酒"
                elif p_res[0][0] == "l":
                    return "利口酒", "洋烈酒"
                elif p_res[0][0] == "t":
                    return "龙舌兰酒", "洋烈酒"

    pattern = "(G[Ii][Nn]|R[uU][Mm])"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if p_res[0][0] == "G":
                    return "金酒", "洋烈酒"
                elif p_res[0] == "R":
                    return "朗姆酒", "洋烈酒"

    result_type_1 = "不分"
    result_type_2 = "不分"

    pattern = "("
    for i in Fruit_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result_type_1 = "果酒"
                result_type_2 = p_res[0] + "酒"
                return result_type_2,result_type_1

    return result_type_2,result_type_1
def get_productName(texts_list):
    for pattern in Spacial_productname:
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern)
                if len(p_res) > 0 and "的" not in p_res[0]:
                    return p_res[0]

    pattern = "("
    for i in Type_list:
        pattern += "\w*" + i + "|"
    pattern = pattern[:-1] + ")$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "("
    for i in Type_list:
        pattern += "\w*" + i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "\w+酒$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "饮酒" not in p_res[0] and "喝酒" not in p_res[0] and "的" not in p_res[0]:
                    return p_res[0]

    pattern = "\w+酒"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "饮酒" not in p_res[0] and "喝酒" not in p_res[0] and "的" not in p_res[0]:
                    return p_res[0]

    return "不分"




def get_Capacity(kvs_list,texts_list):
    pattern = r'(净含量|净重|NETWT|重量)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\W*(ml|毫升|mL|L|kg|ML)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        return p_res[0] + p_res[1]

    pattern = r'(规格)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\W*(ml|毫升|mL|L|ML)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        return p_res[0] + p_res[1]

    pattern = r'(量$)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    pattern = r'(\d+\.?\d*)\W*(ml|毫升|mL|ML)'
                    p_res = re.compile(pattern).findall(kv[k])
                    if len(p_res) > 0:
                        p_res = p_res[0]
                        return p_res[0] + p_res[1]

    return "不分"

def get_Capacity_bak(texts_list):
    p = re.compile(r'(\d+\.?\d*)\s?(ml|毫升|mL|ML)')
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = p.findall(text)
            if len(p_res) > 0 and "每" not in text:
                p_res = p_res[0]
                tmp_list.append(p_res[0] + p_res[1])

        if len(set(tmp_list)) == 1:
            return tmp_list[0]

    p = re.compile(r'^(\d+\.?\d*)\s?(ml|毫升|mL|ML)$')
    for texts in texts_list:
        for text in texts:
            p_res = p.findall(text)
            if len(p_res) > 0 and "每" not in text:
                p_res = p_res[0]
                return p_res[0] + p_res[1]

    p = re.compile(r'(\d+\.?\d*)\s?(ml|毫升|mL|ML)$')
    for texts in texts_list:
        for text in texts:
            p_res = p.findall(text)
            if len(p_res) > 0 and "每" not in text:
                p_res = p_res[0]
                return p_res[0] + p_res[1]

    p = re.compile(r'(\d+\.?\d*)[m毫]$')
    for texts in texts_list:
        for text in texts:
            p_res = p.findall(text)
            if len(p_res) > 0 and "每" not in text:
                return p_res[0] + "ml"

    return "不分"

def get_Capacity_2(texts_list):
    pattern = r'\d+\.?\d*\D*[l升L]\D{0,3}\d+\D*[包袋罐瓶听]装?\)?'
    pattern_2 = r'(\d+\.?\d*)\W*(毫升|ml|mL|ML)\D{0,3}(\d+)\D*[包袋罐瓶听]装?\)?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), p_res_2[1])), re.sub(u"\)", "",
                                                                                                        p_res[0])
                            else:
                                return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[l升L][*xX]\d+[包袋罐瓶听\)]?$'
    pattern_2 = r'(\d+\.?\d*)\W*(毫升|ml|mL|ML)[*xX](\d+)[包袋罐瓶听\)]?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), p_res_2[1])), re.sub(u"\)", "",
                                                                                                        p_res[0])
                            else:
                                return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    pattern = r'\d+\.?\d*\D*[l升L][*xX]\d+[包袋罐瓶听\)]?'
    pattern_2 = r'(\d+\.?\d*)\W*(毫升|ml|mL|ML)[*xX](\d+)[包袋罐瓶听\)]?'
    p = re.compile(pattern)
    for text_list in texts_list:
        for text in text_list:
            p_res = p.findall(text)
            if len(p_res) > 0:
                p_res_2 = re.compile(pattern_2).findall(p_res[0])
                if len(p_res_2) > 0:
                    p_res_2 = p_res_2[0]
                    if len(p_res_2) == 3:
                        if p_res_2[2] != "0" and p_res_2[2] != "":
                            if "*" in p_res[0] or "x" in p_res[0] or "X" in p_res[0]:
                                return ("%d%s" % (float(p_res_2[0]) * float(p_res_2[2]), p_res_2[1])), re.sub(u"\)", "",
                                                                                                        p_res[0])
                            else:
                                return "不分", re.sub(u"\)", "", p_res[0])
                    else:
                        return "不分", re.sub(u"\)", "", p_res[0])

    return "不分", "不分"

#取出所有品牌，目的是为了刷选品牌用
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

#提取商品全称
def get_productName_voting(texts_list):
    result_list = []
    abort_list = ['饮用','了解','进口','注入','类型','网红']
    pre_result_list = []
    pattern_1 = "("
    for i in suffix_name_list:
        pattern_1 += "\w+" + i + "|"
    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1.replace("+", "*")[:-1]

    pattern_3 = "奶酒王"
    # pattern_4 = "\w+粉"


    for texts in texts_list:
        for text in texts:
            flag = True
            for it in abort_list:
                if it in text:
                    flag = False
                    break
            if flag:
                p_res = get_info_by_pattern(text, pattern_1)
                if len(p_res) > 0 and '的' not in p_res[0]:
                    result_list.append(p_res[0])
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        if len(pre_result_list)>0:
            return pre_result_list[0]
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            flag = True
            for it in abort_list:
                if it in text:
                    flag = False
                    break
            if flag:
                p_res = get_info_by_pattern(text, pattern_2)
                if len(p_res) > 0 and '的' not in p_res[0]:
                    result_list.append(p_res[0])
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        if len(pre_result_list)>0:
            return pre_result_list[0]
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            flag = True
            for it in abort_list:
                if it in text:
                    flag = False
                    break
            if flag:
                p_res = get_info_by_pattern(text, pattern_3)
                if len(p_res) > 0 and '的' not in p_res[0]:
                    result_list.append(p_res[0])
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        if len(pre_result_list)>0:
            return pre_result_list[0]
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return "不分"

def category_rule_217(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    type_1 = "不分"
    type_2 = "不分"
    placeOrigin = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["RAC","MANIAO"], [])

    brand_1 = re.sub("MANIAO","马尿maniao",brand_1,re.IGNORECASE)
    brand_1 = re.sub("Migar","觅呷Migar",brand_1,re.IGNORECASE)

    product_name = get_productName_voting(datasorted)
    product_name = re.sub('\W', "", product_name)
    product_name = re.sub("威士[总忘]", "威士忌", product_name)
    product_name = re.sub("著梅酒", "青梅酒", product_name)


    placeOrigin = get_keyValue(dataprocessed, ['原产国','原酒产地'])
    if placeOrigin not in Place_list:
        placeOrigin = get_place(datasorted,placeOrigin)
    placeOrigin = re.sub('苏格兰', "英国", placeOrigin)
    placeOrigin = re.sub('俄国', "俄罗斯", placeOrigin)


    capcity_1 = get_Capacity(dataprocessed, datasorted)
    capcity_1_bak, capcity_2 = get_Capacity_2(datasorted)
    if capcity_1_bak != "不分" and capcity_1_bak[0] != "0":
        capcity_1 = capcity_1_bak
    if capcity_1 == "不分":
        capcity_1 = get_Capacity_bak(datasorted)


    if type_1 == "不分":
        type_2, type_1 = get_type([[product_name,],])
    if type_1 == "不分" and type_2 == "不分":
        type_2,type_1= get_type(datasorted)


    if product_name == "不分" and type_2 != "不分":
        product_name = brand_1 + type_2 if brand_1 != "不分" else type_2

    if brand_1 != "不分":
        if brand_1.title() in product_name.title():
            product_name = product_name.title().replace(brand_1.title(), '')
    #分类
    result_dict['info1'] = type_1
    #类型
    result_dict['info2'] = type_2
    #产地
    result_dict['info3'] = placeOrigin
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])
    result_dict["info3"] = re.sub("[,，：:：]", "", result_dict["info3"])
    real_use_num = 3
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_2\217-鸡尾酒'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        product = "3044105"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_217(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)