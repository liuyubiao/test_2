import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity


LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/325_brand_list",encoding="utf-8").readlines())]
function_list = [i.strip() for i in set(open("Labels/325_function_list",encoding="utf-8").readlines())]
function_list.sort(key=len,reverse=True)
suffix_name_list = [i.strip() for i in open("Labels/325_suffix_name_list",encoding="utf-8").readlines()]
type_english_list = [i.strip() for i in open("Labels/325_type_english_list",encoding="utf-8").readlines()]


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
    abort_list = []
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
                    if '品名' in text or '名:' in text:
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
                    if '品名' in text or '名:' in text:
                        pre_result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        if len(pre_result_list) > 0:
            return pre_result_list[0]
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return '不分'

# 提取系列
def get_SubBrand(texts_list):
    '''
    提取系列
    提取依据：325定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：包含类似XX系列
    :param texts_list:有序文本列表
    :return:
    '''
    pattern = '\w+系列'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]
    return '不分'

#提取适用人群
def get_suitpeople(texts_list):
    '''
    提取适用人群
    提取依据：325定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：注意包装特色对特殊人群的辨别，像儿童、男士、孕产妇、婴幼儿
    :param texts_list: 有序文本列表
    :return:
    '''
    # 适合婴幼儿和准妈妈

    pattern0 ='(儿童|男士|孕产妇|婴幼儿|孕妇|婴儿|婴童|宝宝|成人|baby|BABY)'
    pattern = '适用人群' + pattern0
    pattern1 = '适合\w*' + pattern0
    pattern2 = r'专为' + pattern0 + '研制配方'
    pattern3 = "男士"
    for texts in texts_list:
        text_origi = ''.join(texts)
        p_res = get_info_by_pattern(text_origi, pattern)
        if len(p_res) > 0:
            result = p_res[0]
            if result == '婴儿' or result == '婴童' or result == 'BABY' or result == 'baby':
                return '婴幼儿'
            elif result == '宝宝':
                return '儿童'
            return result
        else:
            p_res = get_info_by_pattern(text_origi, pattern1)
            if len(p_res) > 0:
                result = p_res[0]
                if result == '婴儿' or result == '婴童' or result == 'BABY' or result == 'baby':
                    return '婴幼儿'
                elif result == '宝宝':
                    return '儿童'
                return result
            else:
                p_res = get_info_by_pattern(text_origi, pattern2)
                if len(p_res) > 0:
                    result = p_res[0]
                    if result == '婴儿' or result == '婴童' or result == 'BABY' or result == 'baby':
                        return '婴幼儿'
                    elif result == '宝宝':
                        return '儿童'
                    return result
                else:
                    p_res = get_info_by_pattern(text_origi, pattern3)
                    if len(p_res) > 0:
                        return p_res[0]
    return '不分'

# 提取功能信息
def get_function(texts_list):
    '''
    提取功能信息
    提取依据：325定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    :param texts_list: 有序文本列表
    '''
    for texts in texts_list:
        txt_orgi = ''.join(texts)
        list1 = []
        for it in function_list:
            if it in txt_orgi:
                if it not in list1:
                    if len(list1)==1:
                        if it in list1[0]:
                            continue
                        elif list1[0] in it:
                            list1[0] = it
                        else:
                            if txt_orgi.find(it)<txt_orgi.find(list1[0]):
                                list1[0] = it
                            else:
                                list1.append(it)
                    else:
                        list1.append(it)
                if len(list1) == 2:
                    return '，'.join(list1)
        if len(list1)>0:
            return '，'.join(list1)
    return '不分'

#提取产品归类信息
def get_category(product_name,texts_list):
    '''
    提取产品归类信息
    提取依据：325定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    :param texts_list: 有序文本列表
    :param product_name:
    :return:
    '''
    list_product = ['隔离','防晒','防嗮']
    list_jinghuashui = ['精华水','精萃水','精粹水']
    list_jinghuayou = ['精华油', '精粹油']
    list_yuanye = ['原液', '原浆液']
    list_otherjinghua = ['精华液','精华露','精华']
    list_jinghua = ['精华乳','精粹乳','精华霜','精华乳液','精华面霜','精华乳霜']
    list_makeup = ['喷雾','舒颜水','小粉水','丽肤水','臻萃水','嫩肤水','透肌水','肌活水','柔肤水','舒缓水']


    pattern ='\w*(按摩|精华?[水液露乳霜面油]霜?|精[粹萃]水|精粹[油乳]|原浆?液|肌底液|颜霜|防晒|防嗮|隔离|冻干|精华$)'
    pattern1='\w+(喷雾|舒颜水|小粉水|丽肤水|臻萃水|嫩肤水|透肌水|肌活水|柔肤水|舒缓水)'
    p_res = get_info_by_pattern(product_name, pattern)
    if len(p_res) > 0:
        result = p_res[0]
        if result in list_jinghuayou:
            return '精华油'
        elif result in list_jinghuashui:
            return '精华水'
        elif result in list_otherjinghua:
            if '冻干粉' in product_name:
                return '冻干粉'
            return '其他纯精华'
        elif result in list_jinghua:
            return '一般精华'
        elif result in list_yuanye:
            return '原液'
        elif result in list_product:
            return result.replace('防嗮','防晒') + '产品'
        elif result == '冻干':
            return '冻干粉'
        elif result == '肌底液':
            return '肌底液'
        elif result == '颜霜':
            return '素颜霜'
    else:
        p_res = get_info_by_pattern(product_name, pattern1)
        if len(p_res) > 0:
            result = p_res[0]
            if result in list_makeup:
                return '化妆水'
        else:
            for texts in texts_list:
                for text in texts:
                    p_res = get_info_by_pattern(text, pattern)
                    if len(p_res) > 0:
                        result = p_res[0]
                        if result in list_jinghuayou:
                            return '精华油'
                        elif result in list_jinghuashui:
                            return '精华水'
                        elif result in list_otherjinghua:
                            return '其他纯精华'
                        elif result in list_jinghua:
                            return '一般精华'
                        elif result in list_yuanye:
                            return '原液'
                        elif result in list_product:
                            return result.replace('防嗮', '防晒') + '产品'
                        elif result == '冻干':
                            return '冻干粉'
                        elif result == '肌底液':
                            return '肌底液'
                        elif result == '素颜霜':
                            return '素颜霜'
                    else:
                        p_res = get_info_by_pattern(text, pattern1)
                        if len(p_res) > 0:
                            result = p_res[0]
                            if result in list_makeup:
                                return '化妆水'
    return '其他滋润产品'

# 提取适用部位
def get_applicable_parts(product_name,texts_list):
    '''
    提取适用部位
    提取依据：325定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：肌肤/脸部/脸部、颈部/面部、身体/身体/手部/眼部/其它
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern = '\w*手[霜乳]|眼|身体'
    pattern0 = '[喷涂]抹?袜?\w*(颈部及身体|颈部、身体|面部、颈部、手臂、腿部|面部、颈部、胳膊及腿部)'
    pattern1 = '[喷涂]抹?袜?\w*(面部、颈部及|脸部、肩颈四肢|面部和身体|面部或身体|面部、身体|面部,身体|面部、颈部、手臂|面部、手部|面部、颈部、|面部/身体|涂抹于脸部、肩颈四肢|面部及全身)'
    pattern11 = '使用方法\w*(面部、颈部及|脸部、肩颈四肢|面部和身体|面部或身体|面部、身体|面部,身体|面部、颈部、手臂|面部、手部|面部、颈部、|面部/身体|涂抹于脸部、肩颈四肢|面部及全身)'
    pattern2 = '[喷涂]抹?袜?\w*(面部颈?部|面颈部|脸部颈?部|面部和颈部|脸部和颈部|面部,颈部?|脸部,颈部?|面部、颈部?|脸部、颈部?|面部及颈部?|脸部及颈部?)'
    pattern3 = '[喷涂]抹?袜?\w*(脸部|面部)'
    pattern4 = '[喷涂]抹?袜?\w*(全身肌肤|肌肤|皮肤)'
    p_res = get_info_by_pattern(product_name, pattern)
    if len(p_res) > 0:
        result = p_res[0]
        if '手' in result:
            return '手部'
        elif '眼' in result:
            return '眼部'
        elif '身体' in result:
            return '身体'
    for texts in texts_list:
        txt_ori = ''.join(texts)
        txt_ori = txt_ori.replace('(','')
        p_res = get_info_by_pattern(txt_ori, pattern0)

        if len(p_res) > 0:
            return '身体'
        p_res = get_info_by_pattern(txt_ori, pattern1)
        p_res1 = get_info_by_pattern(txt_ori, pattern11)
        if len(p_res) > 0 or len(p_res1)>0:
            return '面部、身体'
        else:
            p_res = get_info_by_pattern(txt_ori, pattern2)
            if len(p_res) > 0:
                return '脸部、颈部'
            else:
                p_res = get_info_by_pattern(txt_ori, pattern3)
                if len(p_res) > 0:
                    return '脸部'
                else:
                    p_res = get_info_by_pattern(txt_ori, pattern4)
                    if len(p_res) > 0:
                        if '暴露在阳光下' in txt_ori or '全身肌肤' in txt_ori:
                            return '身体'
                        return '肌肤'

    return '脸部'

# 提取状态
def get_status(product_name,product_category):
    '''
    提取状态
    提取依据：325定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：雾状：Spray 使用时以极细微的水粒喷射出来的装瓶液体产品，包含 “雾”，”喷剂”，“喷雾”，“喷露”
    例如：胶囊状、乳液状、啫喱状、油状、粉状、膏状、露状、水状、雾状
    :param product_name: 商品全称
    :param product_category:产品归类
    :return:
    '''
    if product_category=='冻干粉':
        return '粉状'

    pattern1 ='\w+(喷雾|露|油|乳|精华液$|胶囊|啫喱|膏|原液$|底液$|浆液$|精华$)'
    pattern2= '\w+水$'
    p_res = get_info_by_pattern(product_name, pattern1)
    if len(p_res)>0:
        result = p_res[0]
        if '喷雾' == result:
            return '雾状'
        elif result in ['精华液','露','精华','原液','底液','浆液']:
            if '胶囊' in product_name:
                return '胶囊状'
            return '露状'
        elif '油' in result:
            return '油状'
        elif '啫喱' in result:
            return '啫喱状'
        elif '乳' in result:
            return '乳液状'
        elif '胶囊' in result:
            return '胶囊状'
        elif '膏' in result:
            return '膏状'
    p_res = get_info_by_pattern(product_name, pattern2)
    if len(p_res) > 0:
        return '水状'

    return '膏状'

#提取适用时间
def get_applicable_time(texts_list):
    '''
    提取适用时间
    提取依据：325定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：早晚/日间/晚间
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern ='早晚|日间|晚间|日常|早脱|晚安'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result = p_res[0]
                if result=='日常':
                    return '日间'
                elif result=='早脱' and '洁面' in text:
                    return '早晚'
                elif '晚安' in result:
                    return '晚间'
                return result
    return '不分'

#提取防晒指数
def get_sun_protection(texts_list):
    '''
    提取防晒指数
    提取依据：325定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：
    1、有SPF和PA两个方面
    2、SPF值按照包装说明实际抄录，有两个SPF值的请将两个值都抄录回来
    3、PA值需要注意包装上有明确PA（+++，++，+）值的或有UVA或UV字样的都要抄录回来
    :param texts_list: 有序文本列表
    :return:
    '''
    pattern = 'SPF\d+\+*.?[A-Z]{0,5}\+*.?[A-Z]{0,5}\+*.?[A-Z]{0,5}\+*.?[A-Z]{0,5}\+*.?'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]
    return '不分'

# 提取英文全称
def get_englis_Full_Name(texts_list):
    '''
    英文全称
    提取思路：
    :param texts_list: 有序文本列表
    '''

    pattern = "([A-Z-\s]+)"
    # 关键词英文单词列表
    list_key = ['MOISTURIZING', 'MOISTURIZER', 'CONCENTRATE', 'PENETRATING', 'GELESSENCE', 'PROTOPLASM', 'ISOLATION', 'WHITENING', 'SUNSCREEN', 'XUNSCREEN', 'CONCUBIN', 'HYDROSOL', 'EMLLSION', 'SKINCARE', 'SOOTHING', 'EMULSION', 'PROTECT', 'REMOVER', 'ESSENCE', 'WRINKLE', 'LIQUID', 'BEIRUN', 'SHUANG', 'LIOUID', 'POWDER', 'LOTION', 'WATER', 'TONER', 'PASTE', 'SERUM', 'CREAM', 'BOMD', 'BODY', 'MILK', 'DREN', 'MIST', 'HAND', 'OIL', 'GEL']
    result_list =[]
    for text_list in texts_list:
        txt_orig = ' '.join(text_list).upper().strip()
        if len(txt_orig)>10:
            # 1、首先把英文字符串分离出来
            p_res = get_info_by_pattern(txt_orig, pattern)
            if len(p_res) > 0:
                for title in p_res:
                    # 2、排除长度小于10英文串
                    if len(title) > 10:
                        words_list = []
                        words = title
                        flag = False
                        for it in list_key:
                            if it in words:
                                flag = True
                                break
                        if flag:
                            # 3、把在英文字符串中出现的单词按照先后顺序存储在列表中，最后用空格链接起来就是英文全称
                            if len(type_english_list)>0:
                                for it in type_english_list:
                                    if it in words:
                                        words = words.replace(it, '*')
                                        if len(words_list) == 0:
                                            words_list.append(it)
                                        else:
                                            flag = True
                                            # 根据单词的先后顺序存在列表中
                                            for index, tt in enumerate(words_list):
                                                if title.find(it) < title.find(tt):
                                                    words_list.insert(index, it)
                                                    flag = False
                                                    break
                                            if flag:
                                                words_list.append(it)
                                        temp = words.replace('*', '')
                                        # 如果都找到并且替换完了，结束循环
                                        if len(temp) == 0:
                                            break
                            else:
                                words_list.append(title)
                            if len(words_list)>0:
                                result = ' '.join(words_list)
                                result_list.append(result)
    if len(result_list)>0:
        result_list.sort(key=len, reverse=True)
        return result_list[0]
    return '不分'

def category_rule_325(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    SubBrand = '不分'
    function = '不分'
    #适用人群
    suitpeople = '不分'
    product_category ='不分'
    applicable_parts = '不分'
    status = '不分'
    type = '不分'
    full_name = '不分'
    applicable_time = '不分'
    sun_protection ='不分'

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["ULY","TOVT","HIH","Belli","LBX"], [])
        brand_1 = re.sub("OCEANDIARY", "OCEAN DIARY", brand_1)
        brand_1 = re.sub("^nourrir$", "若熙nourrir", brand_1,re.IGNORECASE)
        brand_1 = re.sub("^CLARINS$", "娇韵诗CLARINS", brand_1, re.IGNORECASE)
        brand_1 = re.sub("^COLORKEY$", "珂拉琪COLORKEY", brand_1, re.IGNORECASE)
        brand_1 = re.sub("^BIOHYALUX$", "润百颜BIOHYALUX", brand_1, re.IGNORECASE)
        brand_1 = re.sub("^UPCOSER$", "吉艾UPCOSER", brand_1, re.IGNORECASE)

    # product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)

    if product_name != '不分' and brand_1 != '不分' and brand_1.title() in product_name.title():
        product_name = product_name.title().replace(brand_1.title(), '')

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "ml|毫升|mL|L|kg|ML|升|g|克", "瓶支", 0)
    SubBrand = get_SubBrand(datasorted)
    suitpeople = get_suitpeople(datasorted)
    function = get_function([[product_name]])
    if function == "不分":
        function = get_function(datasorted)

    product_category = get_category(product_name, datasorted)
    applicable_parts = get_applicable_parts(product_name, datasorted)
    status = get_status(product_name, product_category)
    applicable_time = get_applicable_time(datasorted)
    sun_protection = get_sun_protection(datasorted)
    full_name = get_englis_Full_Name(datasorted)
    # 系列
    result_dict['info1'] = SubBrand
    # 功能
    result_dict['info2'] = function
    # 适用人群
    result_dict['info3'] = suitpeople
    # 产品归类
    result_dict['info4'] = product_category
    # 适用部位
    result_dict['info5'] = applicable_parts
    # 状态
    result_dict['info6'] = status
    # 类型
    result_dict['info7'] = type
    # 英文全称
    result_dict['info8'] = full_name
    # 适用时间
    result_dict['info9'] = applicable_time
    # 防晒指数及PA信息
    result_dict['info10'] = sun_protection


    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])
    real_use_num = 10
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\325-包装饮用水'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3124131"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_325(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)