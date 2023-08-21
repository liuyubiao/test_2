import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity


LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/162_brand_list_1",encoding="utf-8").readlines())]

Taste_list = [i.strip() for i in set(open("Labels/162_taste_list",encoding="utf-8").readlines())]
suffix_name_list = [i.strip() for i in open("Labels/162_suffix_name_list",encoding="utf-8").readlines()]
mixture_list = [i.strip() for i in open("Labels/162_mixture_list",encoding="utf-8").readlines()]
Ingredients_list_ori = [i.strip() for i in open("Labels/162_ingredients_list",encoding="utf-8").readlines()]
Ingredients_list = []
for line in Ingredients_list_ori:
    Ingredients_list.extend(re.split("[^\-0-9a-zA-Z\u4e00-\u9fa5]",line))
Ingredients_list = set(Ingredients_list)
Ingredients_list.remove("")
Ingredients_list = list(Ingredients_list)
Ingredients_list.sort(key=len,reverse=True)


def get_key_Value(kvs_lists,list_key):
    result_list = []
    for kvp_list in kvs_lists:
        for kvp in kvp_list:
            keys_list = kvp.keys()
            for key in list_key:
                if key in keys_list:
                    kvalue = kvp[key]
                    if len(kvalue)>=2:
                        result_list.append(kvalue)

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) >1 and count[0][1] == count[1][1] and len(count[0][0]) < len(count[1][0]) and len(re.compile("[0-9,，、]").findall(count[1][0])) == 0:
        return count[1][0]
    else:
        return count[0][0]

#取出所有品牌，目的是为了刷选品牌用
def get_brand_list_test(texts_list):
    brand_1_list = []
    brand_2 = []
    for texts in texts_list:
        text_str = "".join(texts)
        text_str_ori = ",".join(texts)
        for bb in Brand_list_1:
            if bb in text_str :
                if len(bb) > 2 and len(re.compile("[\u4e00-\u9fa5]").findall(bb)) > 0:
                    brand_1_list.append(bb)
                elif len(re.compile("(,|^)%s($|,)"%(",".join(list(bb)))).findall(text_str_ori)) > 0:
                    brand_1_list.append(bb)

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
    abort_list = ['把','含有','是']
    pre_result_list = []
    pattern_1 = "("
    for i in suffix_name_list:
        pattern_1 += "\w+" + i + "|"

    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1.replace("+", "*")[:-1]

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
                    if '品名' in text:
                        pre_result_list.append(p_res[0])
                    continue


    if len(result_list) > 0:
        if len(pre_result_list) > 0:
            return pre_result_list[0]
        result_list.sort(key=len, reverse=True)
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
                    if '品名' in text:
                        pre_result_list.append(p_res[0])
                    continue


    if len(result_list) > 0:
        if len(pre_result_list) > 0:
            return pre_result_list[0]
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return '不分'

#提取系列
def get_SubBrand(texts_list):
    '''
    提取系列
    提取依据：162定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、只抄肉类的描述，按照实际包装配料表抄录；如鸭脖、鸡肉、猪肉、牛板筋等。
    2、如果配料含两种及以上的**肉都要抄全；配料里有含肉量百分比，也要抄一下
    3、配料里的调味料、调味汁等信息不用抄录；如下图抄录“猪软骨”即可
    :param texts_list: 有序文本列表
    '''
    pattern = '\w+系列'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]
    return '不分'

#提取配料
def get_mixture(product_name,kvs_list,texts_list):
    '''提取配料
    提取依据：162定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：只抄跟“海鲜肉”相关的描述。如鱼肉、蟹、虾等
    :param kvs_list: 文本键值对
    :param texts_list: 有序文本列表
    :return:
    '''
    mixture = ''
    for it in mixture_list:
        if it in product_name:
            return it
    result = get_key_Value(kvs_list, ['配料','配科','配料表','配科表','料表','科表','酸料','料'])
    if result!='不分':
        if '、' in result:
            mixture =  result.split('、')[0]
        elif ',' in result:
            mixture =  result.split(',')[0]
        elif '(' in result:
            mixture =  result.split('(')[0]
        if len(mixture)==0:
            mixture = result


        if '(' in mixture:
            mixture = mixture.split('(')[0]
        # if '谨慎' in mixture or '省' in mixture or '添加剂' in mixture or '白砂糖' in mixture:
        #     return '不分'
        return mixture


    return '不分'

#提取产品类型
def get_product_type(kvs_list,texts_list):
    '''
    提取产品类型
    提取依据：162定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、根据包装背面“产品类型”或全称后(括号)里的内容抄录，没有给不分。
    :param product_type:
    :param kvs_list:文本键值对
    :param texts_list:有序文本列表
    :return:
    '''
    result = get_key_Value(kvs_list, ['食品类型','食品类别','产品类型','产品类别'])
    if result!='不分':
        if not result.endswith('水'):
            return result


    pattern1 ='(熟制动物性水产?|熟制水|风味熟制水|动物性水产|水产制品熟制水|熟肉|水产品)(制品|产品|罐头)'
    pattern2='(产品类型|食品类型|食品类别|产品类别):?'+pattern1
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern1)
            if len(p_res) > 0:
                p_res = p_res[0]
                return p_res[0]+p_res[1]
            else:
                p_res = get_info_by_pattern(text, pattern2)
                if len(p_res) > 0:
                    p_res = p_res[0]
                    return p_res[1] + p_res[2]
    return '不分'


#提取种类
def get_type(product_name,texts_list):
    '''
    提取种类
    提取依据：162定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、鱼类：带鱼，黄鱼（小黄鱼）、鳕鱼，草鱼，鳗鱼，三文鱼，秋刀鱼等鱼类
    2、贝类：蚌、鲍鱼、蛏子、蛤、蚝、花甲、蛎、蛎蝗、牡蛎、螺、青口贝、扇贝、鲜贝、蚬、柱连籽、小仁仙、瑶柱、青口、象拔蚌、贻贝等贝类
    3、蟹类：河蟹，毛蟹，大闸蟹等蟹类。注意蟹柳/蟹棒等按照实际配料归属。
    4、软体类：鱿鱼，章鱼，墨鱼，八爪鱼海肠等软体类
    5、混合：两种及以上海鲜种类；
    :param product_name:商品全称
    :param texts_list:有序文本列表
    :return:
    '''
    soft_list = ['鱿鱼','章鱼','墨鱼','八爪鱼']
    bei_list = ['蚌', '鲍鱼', '蛏子', '蛤','蚝','花甲','蛎','蛎蝗','螺','青口贝','扇贝','鲜贝','蚬','柱连籽','小仁仙','瑶柱','青口','象拔蚌','贻贝']
    xie_list = ['河蟹', '毛蟹', '大闸蟹','螃蟹','珍珠蟹']
    for it in soft_list:
        if it in product_name:
            return '软体类'
    for it in bei_list:
        if it in product_name:
            return '贝类'
    for it in xie_list:
        if it in product_name:
            return '蟹类'
    if '鱼' in product_name or '泥鳅' in product_name:
        return '鱼类'

    elif '虾' in product_name:
        return '虾类'

    return '不分'

#提取健康概念信息
def get_health_concept(texts_list):
    '''
    提取健康概念信息
    提取依据：162定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：开放字段 ：涉及健康理念的信息，如低脂、零脂、高蛋白、零添加等
              注意抄录包装上的“0脂、低脂、0蔗糖、0油、高蛋白等信息”，可以互相组合
              注意包装有“无添加、零添加”时看下配料，只要有其中一种添加剂的都不给“无添加”
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern='低脂|零脂|0脂|低糖|零糖|0糖|高蛋白'
    result_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if p_res[0] not in result_list:
                    result_list.append(p_res[0])
    if len(result_list)>0:
        return '，'.join(result_list)
    return '不分'

#提取加工工艺信息
def get_processing_technology(product_name,product_type,taste,texts_list):
    '''
    提取加工工艺信息
    提取依据：162定义文档、及人为标注Excel测试数据
    提取思路：封闭字段 ：风干、手撕、熏、烤、虎皮、油炸、盐焗、泡、卤、酱等
              不分：全称或包装上任何位置无相关加工工艺字样。
    :param product_name:商品全称
    :param texts_list: 有序文本列表
    '''
    # 熏烤/锁水工艺/盐烧/油浸/油炸

    if taste=='烧烤味' or taste=='烧烤':
        return '不分'
    if '铁板烧' in product_name:
        return '铁板烧'
    elif '铁板' in product_name:
        return '铁板'
    elif '板烧' in product_name:
        return '板烧'
    elif '爆烧' in product_name:
        return '爆烧'
    elif '炒' in product_name:
        return '炒'
    elif '豆豉' in product_name:
        return '豆豉'
    elif '红烧' in product_name:
        return '红烧'
    elif '酱' in product_name:
        return '酱'
    elif '慢烤' in product_name:
        return '慢烤'
    elif '炭烤' in product_name:
        return '炭烤'
    elif '碳烤' in product_name:
        return '碳烤'
    elif '烤制' in product_name:
        return '烤制'

    elif '烤' in product_name:
        return '烤'
    elif '卤' in product_name:
        return '卤'
    elif '手撕' in product_name:
        return '手撕'

    if '油浸' in product_type:
        return '油浸'

    for texts in texts_list:
        txt_orig = ''.join(texts)
        if '酱料' in txt_orig or '酱' in txt_orig:
            return '酱'
    return '不分'

def get_package_162(base64strs):
    '''
    调用服务提取包装信息
    :param base64strs: 图片列表
    :return:
    '''
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if material == "纸":
        material = "纸"
    else:
        material = "塑料"

    if shape in ["盒", "托盘"]:
        shape = "盒"

    result = material + shape
    if '袋' in result :
        return '袋装'
    elif '塑料瓶' in result:
        return '塑料瓶、桶'
    elif '塑料盒' in result:
        return '塑料盒'
    elif '纸盒' in result:
        return '纸盒、礼盒'
    return result

# 提取储藏方式
def get_storage(kvs_list,texts_list):
    '''
    提取储藏方式
    :param kvs_list:文本键值对
    :param texts_list:有序文本列表
    :return:
    '''
    result = get_key_Value(kvs_list, ["贮藏方法", '贮存条件'])
    if result != '不分':
        if '存于阴凉通风干燥处或冷藏' in result or '阴凉干燥处或冷藏' in result:
            return '常温、冷藏'
        elif '冷藏贮存' in result:
            return '冷藏'
        else:
            return '常温'
        # return result
    for texts in texts_list:
        text = ''.join(texts)
        if '存于阴凉通风干燥处或冷藏' in text or '阴凉干燥处或冷藏' in text:
            return '常温、冷藏'
        if '冷藏贮存' in text:
            return '冷藏'
        else:
            return '常温'
    return '常温'

#提取部位/形状
def get_position_shape(product_name,texts_list):
    '''
    提取部位/形状
    提取依据：162定义文档、及人为标注Excel测试数据
    提取思路：
    1、整只/整条、须/足、尾、翅、皮、丸、粒/块、棒/条、柳、片、排、丝等
    2、根据全称和配料判断。优先判断是否整只，然后须、足、尾、翅等部位。
    3、整只/整条：比如墨鱼仔、鱿鱼仔、整只小鱼干、不带壳的整贝等
    4、须/足：比如鱿鱼须、章鱼足等
    5、尾、翅：比如鱼尾、虾尾、鱼翅等，不包含头部
    :param product_name: 商品全称
    :param texts_list: 有序文本列表
    :return:
    '''
    if '尾' in product_name:
        return '尾'
    elif '头' in product_name:
        return '头'
    elif '柳' in product_name:
        return '柳'
    elif '棒' in product_name or '条' in product_name:
        return '棒、条'
    elif '须' in product_name or '足' in product_name:
        return '须、足'
    elif '鱼块' in product_name or '带鱼' in product_name or '豆腐' in product_name:
        return '粒、块'
    elif product_name.endswith('丝'):
        return '丝'
    elif '鱼片' in product_name:
        return '片'
    elif '鱼皮' in product_name:
        return '皮'
    elif '鱼排' in product_name:
        return '排'
    elif '丸' in product_name:
        return '丸'
    return '整只、整条'
#################################################主要成份或原料##################################

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

def get_ingredients(kvs_list, texts_list):
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
                            tmp_list,_ = get_ingredients_list([[texts[index + i],],])
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
########################################################################################3

#调用公告方法提取口味
def get_taste(texts_list,product_name):
    '''
    调用公告方法提取口味
    基本思路是要维护口味列表160_taste_list，根据商品名称全程和口味列表进行匹配提取
    :param texts_list:
    :param product_name:
    :return:
    '''
    pattern = "(\w+味)"
    result = get_info_list_by_list([[product_name,],], Taste_list)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0 and p_res[0] not in ["口味","新口味","风味"]:
            Flag = True
            for i in Taste_Abort_List:
                if i in p_res[0]:
                    Flag = False
                    break
            if Flag:
                # result.append(p_res[0])
                result.append(p_res[0])

    if len(result) == 0:
        res = get_taste_normal(texts_list, Taste_list)
        res = res.replace('，','')
    else:
        res = "".join(result)
    abort_list =['手撕','记录','保留']
    for it in abort_list:
        if it in res:
            return '不分'

    return res


# 入口函数
def category_rule_162(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    # 系列	配料	产品类型	子品类	种类	口味	去骨/去皮	包装	储藏方式	独立装	健康概念	加工工艺
    SubBrand = "不分"
    # 配料
    mixture = "不分"
    # 产品类型
    product_type = "不分"
    # 部位/形状
    shape = "不分"
    # 种类
    type = "不分"
    # 口味
    taste = "不分"
    # 包装
    package = "不分"
    # 储藏方式
    storage='不分'
    # 独立装/非独立装
    independent_packet ='非独立装'
    # 健康概念
    health_concept ='不分'
    # 加工工艺
    processing_technology='不分'
    materials ='不分'

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["渤海","劲仔"], [])
        brand_1 = re.sub('恋鱼几', "恋鱼儿", brand_1)
        brand_1 = re.sub('集果', "集味果", brand_1)
        brand_1 = re.sub('抓鱼描', "抓鱼的猫", brand_1)
        brand_1 = re.sub('三仔', "三公仔", brand_1)
        brand_1 = re.sub('三松仔', "三公仔", brand_1)
        brand_1 = re.sub('季山庄', "六季山庄", brand_1)
        brand_1 = re.sub('灵气姐', "灵气小姐", brand_1)
        brand_1 = re.sub('NB盒马', "盒马NB", brand_1)
        brand_1 = re.sub('盛茗缘', "庐茗缘", brand_1)

    # 测试用，暴露更多的品牌，过滤刷选用
    # brand_1_test, brand_2_test = get_brand_list_test(datasorted)
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)

    if product_name != '不分' and brand_1 != '不分' and brand_1.title() in product_name.title():
        product_name = product_name.title().replace(brand_1.title(), '')


    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "袋瓶盒", 0)
    if capcity_2 != "不分":
        pattern = "\*(\d+)"
        # 独立装：包装内有独立小包，或重量注明内有几小包的产品类似：15克*4袋
        # 非独立装：包装内没有独立小包，或无法区分是否独立装时。
        p_res = get_info_by_pattern(capcity_2, pattern)
        if len(p_res) > 0 and int(p_res[0]) > 1:
            independent_packet = '独立装'

    SubBrand = get_SubBrand(datasorted)
    type = get_type(product_name, datasorted)
    product_type = get_product_type(dataprocessed, datasorted)
    shape = get_position_shape(product_name, datasorted)
    taste = get_taste(datasorted, product_name)
    storage = get_storage(dataprocessed, datasorted)
    mixture = get_mixture(product_name, dataprocessed, datasorted)
    mixture = re.sub('鱼素', "鱼糜", mixture)
    mixture = re.sub('鱼度', "鱼糜", mixture)
    mixture = re.sub('鱼腐', "鱼糜", mixture)
    processing_technology = get_processing_technology(product_name, product_type,taste,datasorted)
    if materials == "不分":
        materials = get_ingredients(dataprocessed, datasorted)
    if mixture=='不分' and materials!='不分':
        it = materials
        if ',' in it:
            it = it.split(',')[0]
        if '(' in it:
            it = it.split('(')[0]
        if it.endswith('鱼') or it.endswith('虾') or it.endswith('糜') or it.endswith('贝') or it.endswith('蟹') or it.endswith('皮'):
            mixture = it
    health_concept = get_health_concept(datasorted)
    package = get_package_162(base64strs)
    # 系列
    result_dict['info1'] = SubBrand
    # 配料
    result_dict['info2'] = mixture
    # 种类
    result_dict['info3'] = type
    # 产品类型
    result_dict['info4'] = product_type
    # 部位/形状
    result_dict['info5'] = shape

    # 口味
    result_dict['info6'] = taste
    # 加工工艺
    result_dict['info7'] = processing_technology
    # 储藏方式
    result_dict['info8'] = storage
    # 包装
    result_dict['info9'] = package
    # 独立装
    result_dict['info10'] = independent_packet
    # 健康概念
    result_dict['info11'] = health_concept

    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name
    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])
    real_use_num = 11
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []

    # 全部成分
    result_dict['info19'] = materials

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\162-肉类零食'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3124131"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_162(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)