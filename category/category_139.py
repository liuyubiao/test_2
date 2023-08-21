import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity
'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,类型,包装类型,代餐功能,食用方法用量,适宜/不适宜人群
'''
# 目前已知的属性列表, 可以进行扩展
TASTE_RULE = ['口味', '味']
TYPE_RULE = ['普通饼干','夹心饼干','克力架','苏打','梳打','软曲奇','硬曲奇','普通威化','巧克力涂层威化','其他涂层威化','蛋卷','休闲饼干','沾酱饼干','异形饼干','薄片饼干','注心饼干','混合饼干','煎饼']
PACKAGE_RULE = ['单包装','多包装']
FOOD_RULE = ['代餐','高蛋白','低脂','高膳食纤维','低GI生酮','轻食','高饱腹','低卡']
PEOPLE_RULE = ['不适宜', '不适用']
#食用方法常用描述
list_eat_function = ['适量饮水', '温开水食用', '每日三餐', '温开水', '搭配', '效果更佳']
Brand_list_1 = [i.strip() for i in set(open("Labels/139_brand_list_1",encoding="utf-8").readlines())]
Brand_replace_dict_1 = {i.strip().split(':')[0]:i.strip().split(':')[1] for i in set(open("Labels/139_brand_list_3", encoding="utf-8").readlines())}
Brand_list_2 = [i.strip() for i in set(open("Labels/139_brand_list_2",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/139_taste_list",encoding="utf-8").readlines())]

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")
# 通常来看需要20个非通用属性
LIMIT_NUM = 20

#调用公告方法提取饼干口味
def get_taste(texts_list,product_name):
    '''
    调用公告方法提取饼干口味
    基本思路是要维护口味列表139_taste_list，根据商品名称全程和口味列表进行匹配提取
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
        res=get_taste_normal(texts_list, Taste_list)
        return res
    else:
        result = list(set(result))
        return "，".join(result)

def get_type(texts_list,flag = "None"):
    result = "不分"
    pattern = "(克力架|苏打|梳打|曲奇|威化|蛋卷|煎饼|脆片|泡芙|薄脆饼干|注[心芯]卷)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result = p_res[0]
    if result == "不分":
        pattern_2 = r"(\w+饼干)\)?"
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern_2)
                if len(p_res) > 0:
                    if len(p_res[0]) >= 8:
                        continue
                    if flag in p_res[0]:
                        p_res[0] = p_res[0].split(flag)[-1]
                    if p_res[0] == "饼干":
                        result ="普通饼干"
                    else:
                        result = p_res[0]
    return result

#提取饼干类型
def get_type_new(product_name,texts_list):
    '''
    提取饼干类型
    提取依据：139饼干定义文档及人为标注Excel测试数据
    提取思路：139饼干定义文档只明确定义了软曲奇和硬曲奇两种类型：曲奇饼干分为“硬曲奇”和“软曲奇”两种类型
              根据人为标注的Excel数据，发现饼干类型并不是图片中的产品类型中的内容，而是依据其它逻辑
    1、曲奇饼干
        1、软曲奇：全称包含“软曲奇”
        2、硬曲奇：全称包含“曲奇”不包含“软曲奇”归为“硬曲奇
    2、其类型只能根据人为标注的Excel数据寻找规律，根据Excel数据，共分为以下类型：
       3、巧克力涂层威化：全称中包含“巧克力”并且包含“威化” （蛋卷不一定是紧挨着）
       4、普通威化：全称中包含“威化”
       5、蛋卷：全称中包含“蛋卷”或者 包含“蛋”但是不包含饼干
       6、薄片：全称中包含“薄片”或者 “薄片”或者 同时包含“薄”和“片” （薄片不一定是紧挨着）
       7、苏打、梳打：全称中只要包含“苏打”或者 “梳打”
       8、注心饼干：全称中只要包含“注心”并且包含 “饼” （注心和饼不一定是紧挨着）
       9、夹心饼干：全称中只要包含“夹心”并且不包含 “卷”
       10、异形饼干：就是形状比较奇怪的饼干比如全称中包含：'咖啡豆型','棒','小馒头','骨头形','爱心','碎','飞机','字母','芝士脆','数字','动物造型'
       11、混合饼干：包含2个以上的产品名称，2个以上的营养成分表
       12、普通饼干：除了以上饼干外都是普通饼干，没有明显特点
    :param product_name:商品名称全程
    :param texts_list: 文本列表
    :return:
    '''
    type = '不分'
    list_yixing = ['咖啡豆型', '棒', '小馒头', '骨头形', '爱心', '碎', '飞机', '字母', '数字', '动物造型']
    for it in list_yixing:
        if it in product_name:
            type = '异形饼干'
            break


    if type=='不分':
        # pattern1='营养成分表'
        pattern1 = '成分表'
        for texts in texts_list:
            count1 = 0
            for text in texts:
                if pattern1 in text:
                    count1 += 1
            if count1>=2 :
                type = '混合'
                break
        if type == '不分':
            if '煎饼' in product_name:
                type = '煎饼'

            elif '薄片' in product_name or ('薄' in product_name and ('片' in product_name or  '饼干' in product_name)) or '薄饼' in product_name or '薄脆' in product_name :
                type = '薄片'
            elif '蛋卷' in product_name or ('卷' in product_name and '饼干' not in product_name):
                type = '蛋卷'
            elif ('休闲' in product_name or '沾酱' in product_name) and '饼' in product_name:
                type = '休闲、沾酱饼干'
            elif '威化' in product_name:
                type = '普通威化'
            elif '注心' in product_name and '饼'  in product_name:
                type = '注心饼干'
            elif '夹心' in product_name and '卷' not in product_name:
                type = '夹心饼干'
            elif '曲奇' in product_name:
                if '软曲奇' in product_name or ('软' in product_name and '曲奇' in product_name):
                    type = '软曲奇'
                else:
                    type = '硬曲奇'
            elif '苏打' in product_name or '梳打' in product_name:
                type = '苏打、梳打'
            else:
                type = '普通饼干'
    return type

#提取商品名称全称（关键词，投票）
def get_productName_voting(texts_list):
    '''
    提取商品名称全称（关键词，投票）
    提取依据：139饼干定义文档及人为标注Excel测试数据，
    提取思路：文档要求完整抄录正面的信息，（另外还有就是存在混合情况，人为的把所有涉及的全称信息都抄录在名称全称里面，这种根本无法提取准确）
    这个做到很难，好多修饰词分行并且距离间隔很大其不固定，只能根据测试数据中出现的关键词用正则提取：如果提取结果有多个，那么取出现次数最多的
    关键词比如：饼干、蛋卷、曲奇、煎饼、雪饼、脆片、礼盒、棒、蛋酥、注芯卷、注心卷、芹菜卷、夹心卷等待
    :param texts_list:
    :return:
    '''
    product_name = '不分'
    result_list = []
    pattern_1 = "(\w+饼干|\w{2,}饼|\w+克力架|\w+注[心芯]卷|\w+苏打|\w+梳打|\w+曲奇|\w+威化|\w+蛋卷|\w+[煎烧米圆脆酥]饼|\w+脆片|\w+泡芙条?|" \
                "\w+礼盒|\w+瓦夫脆|\w+吐司饼|\w+可可卷|\w+胡椒卷|\w+芹菜卷|\w+夹心卷)$"
    pattern_2 = "(\w+饼干|\w+克力架|\w+注[心芯]卷|\w+苏打|\w+梳打|\w+曲奇|\w+威化|\w+蛋卷|\w+煎饼|\w+脆片|\w+泡芙条?|\w+礼盒|\w+酥皮卷|\w{2,}[脆棒]$|\w+蛋酥)"
    pattern_3 = "(\w*饼干|\w*克力架|\w*注[心芯]卷|\w*苏打|\w*梳打|\w*曲奇|\w*威化|\w*蛋卷|\w*煎饼|\w*雪饼|\w*脆片|\w*泡芙条?)"

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "是" not in p_res[0]:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        product_name = count[0][0]
        # return count[0][0]

    if product_name=='不分':
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern_2)
                if len(p_res) > 0:
                    if "的" not in p_res[0] and "是" not in p_res[0]:
                        result_list.append(p_res[0])
                        continue

        if len(result_list) > 0:
            count = Counter(result_list).most_common(2)
            product_name = count[0][0]
            # return count[0][0]

    if product_name == '不分':
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern_3)
                if len(p_res) > 0:
                    if "的" not in p_res[0] and "是" not in p_res[0]:
                        result_list.append(p_res[0])
                        continue
    product_name = re.sub("^[名称]+", "", product_name)
    product_name = re.sub("\d+[g克]", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = product_name.replace(',', '').replace('艺士', '芝士').replace('/', '').replace('离小芽', '窝小芽')
    return product_name

#提取代餐功能
def get_food(texts_list):
    '''
    提取依据：139饼干定义文档及人为标注Excel测试数据
    提取思路：139饼干定义文档 代餐定义：代餐食品是可以代替或部分代替正餐的食物
    代餐相关的关键字信息，如：代餐、高蛋白、高纤维、谷物粗粮、轻食、低热量、低GI、运动营养、生酮等等
    通过判断文本列表中是否包含关键字信息来判断是否具有代餐功能
    :param texts_list: 文本列表
    :return:
    '''
    result = "不分"
    # list1=['代餐', '高蛋白', '高纤维', '谷物粗粮', '轻食', '低热量', '低GI', '运动营养', '生酮', '控制体重', '体重管理', '粗粮', '谷物', '杂粮', '燕麦', '全麦', '纤麦',
    #  '五谷', '麦麸', '纤麸', '藜麦', '荞麦', '粟米', '多谷', '五粮', '高膳食纤维', '高纤', '富含膳食纤维', 'High fiber', '膳食', '纤维', '膳食纤维', '高蛋白质',
    #  'High protein', '轻断食', '全素', '素食', '低脂', '低脂肪', '轻脂', '高饱腹', '低卡', '低卡路里', '控卡', '低能量']
    # pattern = "[代餐|高蛋白|低脂|高膳食纤维|低GI生酮|轻食|高饱腹|低卡]"
    # 代餐、高蛋白、高纤维、谷物粗粮、轻食、低热量、低GI、运动营养、生酮
    # list1=['代餐','高蛋白','高纤维','谷物粗粮','轻食','低热量','低GI','运动营养','生酮']

    # pattern = "代餐|高蛋白|高纤维|谷物粗粮|轻食|低热量|低GI|运动营养|生酮"
    pattern = '|'.join(FOOD_RULE)
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "代餐"
    return result

#提取食用方法及用量
def get_eat(kvs_list,texts):
    '''
    提取食用方法及用量
    提取依据：139饼干定义文档及人为标注Excel测试数据，从图片及测试数据来看，介绍用量的很少，是小概率
    提取思路：139饼干定义文档 定义：根据产品包装“食用方法/用量”，抄录无/有
    食用方法用量只有开袋即食字样，给无；包装上没有食用方法用量信息，给无；
    包装上食用方法用量除了开袋即食字样，还有其他用量方法描述的字样，给有
    比如：开袋即食，每餐一袋，每日三餐；食用后适量饮水，建议饮水量250ml以上；温开水食用；餐前30分钟食用效果更佳等，
    :param kvs_list:
    :param texts:
    :return:
    '''
    for kvs in kvs_list:
        for kv in kvs:
            if "食用方法及用量" in kv.keys():
                return '有'
            elif "食用方法" in kv.keys():
                kvp=str(kv["食用方法"])
                for it in list_eat_function:
                    if it in kvp:
                        return '有'
                # if '适量饮水' in kvp or '温开水食用' in kvp or '每日三餐' in kvp or '温开水' in kvp or '搭配' in kvp or '效果更佳' in kvp:
                #     return '有'
                return kvp
    return "无"

def get_brand(kvs_list):
    pattern = r'(生产商|经销商)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    return kv[k].replace("有限公司","").replace("有限责任公司","").replace("实业","")
    return "不分"

#提取适宜/不适宜人群
def get_people_type(text_list, infos, RULE_LIST):
    '''
    对适宜/不适宜人群进行规则化的判定
    :param text:
    :param infos:
    :param RULE_LIST:
    :return:
    '''
    people_type_list = []
    people_type = "不分"
    for text in text_list:
        text = "".join(text)
        for item_rule in RULE_LIST:
            # 对不适宜人群进行筛选
            if text.find(item_rule) >= 0:
                for info in infos:
                    for it in info:
                        if it.find(item_rule) >= 0:
                            people_type_list.append(it)

            else:
                # 对适宜人群进行筛选
                tmp_rule = item_rule.replace('不', '')
                if text.find(tmp_rule) > 0:
                    for info in infos:
                        for it in info:
                            if it.find(tmp_rule) >= 0:
                                people_type_list.append(it)

    if len(people_type_list)>0:
        people_type = people_type_list[0]
    return people_type

def get_package_139(base64strs):
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

    if material == "金属":
        return "金属盒，桶"
    elif shape == "礼包":
        return "礼盒，礼袋"
    elif shape == "真空袋":
        return "真空袋"

    if "塑料底" in result_material or "塑料" in material:
        material = "塑料"
    if "玻璃底" in result_material:
        material = "玻璃"

    if "瓶" in shape or "桶" in shape or shape in ["罐","筒","杯"]:
        shape = "瓶，桶"
    if shape in ["托盘", "格", "碗"]:
        shape = "盒"
    if shape in ["立式袋", "吸嘴袋"]:
        shape = "袋"

    if material + shape in ["纸盒"]:
        return "纸盒，箱"
    elif material + shape in ["纸袋"]:
        return "纸袋，桶"
    else:
        return material + shape

def category_rule_139(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    taste = "不分"
    type = "不分"
    package_type = "单包装"
    food = "不分"
    eat = "无"
    people = "不分"
    package = "不分"

    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["Hibo","白威","好的","Aji","FKO","黑粗粮","27度","力儿","优食"], [])
    if brand_1 == "不分":
        brand_1 = get_brand(dataprocessed)
    for key in Brand_replace_dict_1.keys():
        brand_1 = re.sub(key, Brand_replace_dict_1.get(key), brand_1)

    brand_1 = re.sub("一启智兔一","启智兔",brand_1)
    brand_1 = re.sub("KUNIO", "陌姿KUNIO", brand_1,re.IGNORECASE)
    brand_1 = re.sub("Furuta", "富璐达Furuta", brand_1, re.IGNORECASE)

    #调用公共方法提取商品名称全称
    product_name = get_keyValue(dataprocessed,["品名"])
    if product_name=='不分':
        #利用关键词投票提取商品名称全称
        product_name = get_productName_voting(datasorted)

    # 输出类型
    type = get_type_new(product_name,datasorted)

    # 输出口味
    if taste == "不分":
        taste = get_taste(datasorted,product_name)

    # 输出代餐
    if food == "不分":
        food = get_food(datasorted)
    # 输出实用方法用量
    if eat == "不分":
        eat = get_eat(dataprocessed, datasorted)
    # 适宜/不适宜人群(需要额外的方法进行判定)
    if people == "不分":
        people = get_people_type(datasorted, datasorted, PEOPLE_RULE)


    if product_name == "不分":
        if brand_1 != "不分":
            product_name = brand_1 + type if type != "不分" else type

    if taste == "不分":
        tmp_product_name = product_name.split(brand_1)[-1]
        pattern_taste = "(\w+味)"
        p_taste = re.compile(pattern_taste)
        p_taste_res = p_taste.findall(tmp_product_name)
        if len(p_taste_res) > 0:
            taste = p_taste_res[0]

    if capcity_1=='不分':
        capcity_1 ,capcity_2= get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐支", 0)


    if capcity_2 != "不分" and len(re.compile("(^|\D+)1($|\D+)").findall(capcity_2)) == 0:
        package_type = "多包装"
    else:
        package_type = "单包装"

    if "礼盒" in product_name:
        package_type = "多包装"

    package = get_package_139(base64strs)

    #口味
    result_dict['info1'] = taste
    # 类型
    result_dict['info2'] = type
    # 包装类型
    result_dict['info3'] = package_type
    # 代餐功能
    result_dict['info4'] = food
    # 食用方法用量
    result_dict['info5'] = eat
    #   适宜 / 不适宜人群
    result_dict['info6'] = people
    #  包装
    result_dict['info7'] = package

    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    real_use_num = 7
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = ""

    return result_dict



if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_1\139-饼干'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        product = "3035714"
        for image_path in glob(os.path.join(root_path,product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_139(image_list)
        with open(os.path.join(root_path,product) + r'\%s_new.json'%(product),"w",encoding="utf-8") as f:
            json.dump(result_dict,f,ensure_ascii=False,indent=4)

