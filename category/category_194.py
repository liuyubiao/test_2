import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity


LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/194_brand_list_1",encoding="utf-8").readlines())]
#
Taste_list = [i.strip() for i in set(open("Labels/194_taste_list",encoding="utf-8").readlines())]
suffix_name_list = [i.strip() for i in open("Labels/194_suffix_name_list",encoding="utf-8").readlines()]


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

#调用公告方法提取口味
def get_taste(texts_list,product_name):
    '''
    调用公告方法提取口味
    基本思路是要维护口味列表194_taste_list，根据商品名称全程和口味列表进行匹配提取
    :param texts_list:
    :param product_name:
    :return:
    '''
    pattern = "(\w+味)"
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
                # result.append(p_res[0])
                result.append(p_res[0])

    if len(result) == 0:
        res = get_taste_normal(texts_list, Taste_list)
        res = res.replace('，','')
    else:
        res = "".join(result)

    if res == '香辣' or res=='麻辣' or res=='甜辣':
        res = res + '味'
    else:
        res = res.replace('，', '')
        res = res.replace('招牌风味', '')
        if len(res) == 0:
            res = '不分'

    return res

#提取商品全称
def get_productName_voting(texts_list):
    result_list = []
    abort_list = ['胶型','浆型','实型','质型','造型','配料表','凝胶',"做好"]
    # 产品类型
    pre_result_list = []
    pattern_1 = "("
    for i in suffix_name_list:
        pattern_1 += "\w+" + i + "|"

    pattern_0 = '品名:?(\w+\(\w+\))'
    pattern_1 = pattern_1[:-1] + ")$"
    pattern_2 = pattern_1.replace("+", "*")[:-1]
    pattern_3 = '\w+糖$'
    for texts in texts_list:
        for text in texts:
            flag = True
            for it in abort_list:
                if it in text:
                    flag = False
                    break
            if flag:

                p_res = get_info_by_pattern(text, pattern_0)
                if len(p_res) > 0:
                    result_list.append(p_res[0])
                else:
                    if '产品类型' in text and '品名' in text:
                        if text.index('产品类型') > text.index('品名'):
                            text = text.split('产品类型')[0]

                    p_res = get_info_by_pattern(text, pattern_1)
                    if len(p_res) > 0 and '的' not in p_res[0]:
                        result_list.append(p_res[0])
                        if '品名' in text:
                            pre_result_list.append(p_res[0])


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
                if '产品类型' in text and '品名' in text:
                    if text.index('产品类型') > text.index('品名'):
                        text = text.split('产品类型')[0]
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
    if len(result_list) > 0:
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return '不分'

#提取子类
def get_sub_category(product_name,texts_list):
    '''
    提取子类
    提取依据：194定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：

    :param texts_list: 有序文本列表
    '''

    if '点心糖' in product_name:
        return '点心糖'
    elif '咖啡糖' in product_name:
        return '咖啡糖'
    elif '榴莲糖' in product_name:
        return '榴莲糖'
    elif '棉花糖' in product_name:
        return '棉花糖'
    elif '奶糖' in product_name or '奶贝' in product_name or '奶芙' in product_name or '奶片糖' in product_name or '奶棒糖' in product_name or '奶酪糖' in product_name or '牛乳糖' in product_name:
        return '奶糖'
    elif product_name.endswith( '棒棒糖') or '棒棒糖' in product_name or '棒糖' in product_name or '棒棒' in product_name or '奶棒' in product_name or '糖棒' in product_name:
        return '棒棒糖'
    elif '牛皮糖' in product_name:
        return '牛皮糖'
    elif '牛轧糖' in product_name:
        return '牛轧糖'
    elif '泡泡糖' in product_name:
        return '泡泡糖'
    elif '气泡糖' in product_name:
        return '气泡糖'
    elif '瑞士糖' in product_name or '瑞土糖' in product_name:
        return '瑞士糖'
    elif '什锦' in product_name:
        return '什锦糖'
    elif '酥糖' in product_name:
        return '酥糖'
    elif '橡皮糖' in product_name:
        return '橡皮糖'
    elif '星空糖' in product_name:
        return '星空糖'
    elif '橡皮糖' in product_name:
        return '橡皮糖'

    return '水果糖'

#提取产品类型
def get_product_type(product_name,sub_category,kvs_list,texts_list):
    '''
    提取产品类型
    提取依据：194定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、根据包装背面“产品类型”或全称后(括号)里的内容抄录，没有给不分。
    :param product_type:
    :param kvs_list:文本键值对
    :param texts_list:有序文本列表
    :return:
    '''
    result = get_key_Value(kvs_list, ['产品类型','产品类别','品类型','品类别'])
    if result!='不分':
        return result


    pattern1 ='(砂糖、淀粉糖浆型硬质糖果|定粉型|砂糖淀粉糖浆硬质型糖果|包衣包衣抛光型压片糖果|砂糖淀粉糖浆型硬质糖果|低度充气类胶质型糖果|砂糖、淀粉糖浆型糖果|高度充气类夹心型糖果|高度充气类胶质型糖果|高度充气弹性型糖果|高度充气夹心型糖果|淀粉糖浆型硬质糖果|植物凝胶型凝胶糖果|低度充气砂质型糖果|包衣抛光型压片糖果|液体糖液型留质糖果|低度充气胶质型糖果|中度充气混合型糖果|砂质型低度充气糖果|混合胶型凝胶糖果|低度充气胶质糖果|植物胶型凝胶糖果|混合胶型凝胶软糖|高度充气类弹性型|高度充气弹性糖果|高度充气类夹心型|淀粉型凝胶糖果|混合型凝胶糖果|其他型硬质糖果|无皮型酥质糖果|坚实型压片糖果|高度充气糖果|混合凝胶糖果|其他型糖果|抛光型糖果|淀粉糖浆型|酥质糖果|其他硬糖|凝胶糖果|其他软糖|压片糖果|硬质糖果|其他糖果|充气糖果|淀粉型|压片糖)'
    pattern2='(产品类型|产品类别|品类型|品类别):?'+pattern1
    for texts in texts_list:
        text = ''.join(texts)
        if len(text)<=20:
            continue
        p_res = get_info_by_pattern(text, pattern1)
        if len(p_res) > 0:
            result = p_res[0]
            if result == '压片糖':
                result = '坚实型压片糖果'
            elif result=='定粉型':
                result = '淀粉型'
            return result
        else:
            p_res = get_info_by_pattern(text, pattern2)
            if len(p_res) > 0:
                result = p_res[0][1]
                if result == '压片糖':
                    result = '坚实型压片糖果'
                elif result == '定粉型':
                    result = '淀粉型'
                return result
    if '棒糖' in product_name:
        return '其他硬糖'
    elif '软糖' in product_name:
        return '其他软糖'
    if '水果糖' in sub_category:
        return '其他软糖'
    elif '水果糖' in sub_category:
        return '其他硬糖'
    return '不分'

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
        if len(p_res) > 0 and p_res[0] not in ["口味","新口味"]:
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
    # abort_list =['手撕','记录','保留']
    # for it in abort_list:
    #     if it in res:
    #         return '不分'

    return res

def get_package_194(base64strs):
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
    if result=='塑料立式袋' or result =='塑料真空袋':
        return '塑料袋'
    elif result=='塑料杯':
        return '塑料盒'

    return result

# 糖体形状
def get_sugar_shape(product_name,sub_category,texts_list):
    '''
    提取糖体形状
    :param texts_list:
    :return:
    '''

    pattern0 = '棒棒糖|棒糖|CC棒|棒状|火柴|棒'
    pattern1 = '星空糖|手工乐画|西瓜形|爱心|曲奇形|大舌怪|造型|芝士三角|汉堡|寿司|寿司形|3D缤纷|3D造型|盒马造型|水晶造型|雪糕杯|彩绳形|花卷形|麻花形|花朵形|可乐状|星星状|陀螺|卡通|点心糖|炫彩糖|桔子糖|飞流直上|棉花糖'
    pattern2 = '彩针糖|薯条'
    pattern3 = '球|珍珠糖'
    pattern4 = '牛轧糖|咖啡糖|牛皮糖'
    pattern5 = '卷'
    p_res = get_info_by_pattern(product_name, pattern0)
    if len(p_res) > 0:
        return '棒状'
    p_res = get_info_by_pattern(product_name, pattern1)
    if len(p_res) > 0:
        return '卡通造型'
    p_res = get_info_by_pattern(product_name, pattern2)
    if len(p_res) > 0:
        return '条状'
    p_res = get_info_by_pattern(product_name, pattern4)
    if len(p_res) > 0:
        return '块状'

    p_res = get_info_by_pattern(product_name, pattern3)
    if len(p_res) > 0:
        return '粒状'

    p_res = get_info_by_pattern(product_name, pattern5)
    if len(p_res) > 0:
        return '卷状'



    for texts in texts_list:
        text = ''.join(texts)
        p_res = get_info_by_pattern(text, pattern0)
        if len(p_res) > 0:
            return '棒状'
        p_res = get_info_by_pattern(text, pattern0)
        if len(p_res) > 0:
            return '棒状'
        p_res = get_info_by_pattern(text, pattern1)
        if len(p_res) > 0:
            return '卡通造型'
        p_res = get_info_by_pattern(text, pattern2)
        if len(p_res) > 0:
            return '条状'
        p_res = get_info_by_pattern(text, pattern4)
        if len(p_res) > 0:
            return '块状'
        p_res = get_info_by_pattern(text, pattern3)
        if len(p_res) > 0:
            return '粒状'
        p_res = get_info_by_pattern(text, pattern5)
        if len(p_res) > 0:
            return '卷状'


    return '粒状'

# 提取是否夹心
def get_sandwich(product_name,texts_list):
    '''
    提取是否夹心
    :param product_name:
    :return:
    '''
    if '夹心' in product_name:
        return '夹心'

    for texts in texts_list:
        text = ''.join(texts)
        if '夹心型' in text or '夹心' in text:
            return '夹心'

    return '无夹心'

#提取是否含糖
def get_contain_sugar(product_name):
    '''
    提取是否含糖
    :param product_name:
    :return:
    '''
    pattern = '([无0Oo]糖|[0Oo]蔗糖)'
    p_res = get_info_by_pattern(product_name, pattern)
    if len(p_res) > 0:
        return '无糖'
    return '含糖'

#提取是否有包衣
def get_coating(product_name,product_type):
    '''
    提取是否有包衣
    :param product_name:
    :return:
    '''
    if '包衣' in product_name or '包衣' in product_type:
        return '有包衣'

    return '无包衣'

# 入口函数
def category_rule_194(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    # 子类
    sub_category = "不分"
    # 糖体形状
    sugar_shape = "不分"
    # 产品类型
    product_type = "不分"
    # 是否夹心
    sandwich = "无夹心"
    # 是否含糖
    contain_sugar = "含糖"
    # 口味
    taste = "不分"
    # 包装
    package = "不分"
    # 是否有包衣
    coating = '无包衣'
    # 是否礼品装
    gift_packet ='非礼品装'


    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["MOMV","激烈","美成"], [])
        brand_1 = re.sub('嘟嘟力', "嘟嘟象", brand_1)
        brand_1 = re.sub('KINGPOWER', "KING POWER", brand_1)
        brand_1 = re.sub('好多呢', "好多喔", brand_1)
        brand_1 = re.sub('简欢咪乐', "简欢娱乐", brand_1)
        brand_1 = re.sub('小伦玩具', "小伶玩具", brand_1)
        brand_1 = re.sub('尚可猫', "尚叮猫", brand_1)
        brand_1 = re.sub('^RICHDAYS$', "天天好日子RICFHDAYS", brand_1,re.IGNORECASE)
        brand_1 = re.sub('^Skittles$', "彩虹SKITTLES", brand_1,re.IGNORECASE)
    #
    #KINGPOWER
    # # 测试用，暴露更多的品牌，过滤刷选用
    # brand_1_test, brand_2_test = get_brand_list_test(datasorted)
    # product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)
    product_name = re.sub('寿同软糖', "寿司软糖", product_name)
    product_name = re.sub('批杷', "枇杷", product_name)
    product_name = re.sub('蓝霉', "蓝莓", product_name)
    product_name = re.sub('波个', "啵个", product_name)
    product_name = re.sub('PIPAGAO', "枇杷膏", product_name)
    product_name = re.sub('草萄味', "草莓味", product_name)

    product_name = re.sub('^\w棉花糖', "棉花糖", product_name)

    product_name = re.sub('^\d+克', "", product_name)
    product_name = re.sub('[\(\)]', "", product_name)
    #
    if product_name != '不分' and brand_1 != '不分' and brand_1.title() in product_name.title():
        product_name = product_name.title().replace(brand_1.title(), '')

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "袋瓶盒桶", 0)

    sub_category = get_sub_category(product_name,datasorted)
    taste = get_taste(datasorted, product_name)
    sugar_shape = get_sugar_shape(product_name,sub_category,datasorted)
    product_type = get_product_type(product_name,sub_category,dataprocessed,datasorted)
    product_type = re.sub('暴胶|发胶|准胶|复胶|摄胶|及胶|物胶|凝膜|漫胶|凝纹', "凝胶", product_type)
    product_type = re.sub('感果|班果|能果|料$|罐果|精$|稳类', "糖果", product_type)
    product_type = re.sub('[.·\(\)]', "", product_type)
    product_type = re.sub('砂塑', "砂糖", product_type)
    product_type = re.sub('植凝', "植物", product_type)
    product_type = re.sub('程合|温合|混台|湿合', "混合", product_type)

    sandwich = get_sandwich(product_name, datasorted)
    contain_sugar = get_contain_sugar(product_name)
    coating = get_coating(product_name, product_type)
    # image_list = ["/data/zhangxuan/images/43-product-images" + i.split("ocr_test")[-1].replace("\\", "/") for i in base64strs]
    # package = get_package_194(image_list)
    package = get_package_194(base64strs)
    #     # 子类	口味	糖体形状	包装形式	产品类型	是否夹心	是否含糖	是否有包衣	是否礼品装
    # 子类
    result_dict['info1'] = sub_category
    # 口味
    result_dict['info2'] = taste
    # 糖体形状
    result_dict['info3'] = sugar_shape
    # 包装形式
    result_dict['info4'] = package
    # 产品类型
    result_dict['info5'] = product_type

    # 是否夹心
    result_dict['info6'] = sandwich
    # 是否含糖
    result_dict['info7'] = contain_sugar
    # 是否有包衣
    result_dict['info8'] = coating
    # 是否礼品装
    result_dict['info9'] = gift_packet
    # result_dict['info10'] = brand_1_test

    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])
    real_use_num = 9
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\194-肉类零食'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3124131"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_194(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)