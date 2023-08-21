import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,包装形式,类型,包装类型,配料
'''

Brand_list_1 = [i.strip() for i in set(open("Labels/114_brand_list_1",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/114_type_list",encoding="utf-8").readlines())]
Type_list_2 = [i.strip() for i in set(open("Labels/114_type_list_2",encoding="utf-8").readlines())]
Taste_list_1 = [i.strip() for i in set(open("Labels/114_taste_list_1",encoding="utf-8").readlines())]
Taste_list_2 = [i.strip() for i in set(open("Labels/114_taste_list_2",encoding="utf-8").readlines())]

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

#提取类型
def get_type(texts_list,serchList,product_name):
    '''
    提取类型
    提取依据：KWPO品类数据审核_20211231.xlsx定义类型分为：薄荷糖/口香糖/泡泡糖/润喉糖四种类型
    提取思路：根据文本序列匹配类型
    :param texts_list:文本序列
    :param serchList:类型列表
    :return:
    '''
    pattern = "(润喉|"
    for i in serchList:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    type = ''
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                type =  p_res[0]
                break
        if len(type)>0:
            break

    if len(type)==0:
        if "含片" in product_name or '梨膏糖' in product_name or '软糖' in product_name:
            type = "润喉糖"
        if "吹泡" in product_name:
            type = "泡泡糖"
        if "香口珠" in product_name or '香味糖' in product_name or '香口爆珠' in product_name:
            type = "口香糖"
        if '薄荷' in product_name:
            type = "薄荷糖"
    type = type if type != "口嚼糖" else "口香糖"
    type = type if type != "润喉" else "润喉糖"
    if len(type)>0:
        return type
    return '不分'


#提取子类型
def get_Type2_list(texts_list,serchList):
    '''
    提取子类型
    提取依据：114定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：针对薄荷糖和润喉糖进行填写，口香糖、泡泡糖填写NA，
    数据举例：可口型硬糖;压粉型硬糖;功能型硬糖;咀嚼型软糖;其他软糖;其他硬糖;NA
    操作：更加文本序列，匹配114_type_list_2对应列表
    :param texts_list:
    :param serchList:
    :return:
    '''
    result = []
    for texts in texts_list:
        for text in texts:
            for t in serchList:
                if t in text:
                    result.append(t)
    if len(result) > 0:
        result = list(set(result))
        return result[0]
        # return "，".join(result)
    else:
        return '其他硬糖'
#提取是否含糖
def get_sugar_list(texts_list,serchList):
    '''
    提取是否含糖
    提取依据：114定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：定义包含无糖和含糖两种
    无糖：1、产品描述含“无糖” 或 “木糖醇” 或 “Sugarfree”“Xylitol”字样
          2、配料里含有“糖醇”的产品也归为无糖
          3、有山梨糖醇、甘露糖醇、赤藓糖醇、麦芽糖醇、乳糖醇、木糖醇等，糖醇虽然不是糖但具有某些糖的属性。糖醇作为食糖替代品，所以有这些字样的，都为无糖。
          4、配料里注明是“甜味剂”字样的归为无糖
    含糖：配料表里有“白砂糖”则为含糖
    操作：更加文本序列，匹配114_type_list_2对应列表
    :param texts_list:
    :param serchList:
    :return:
    '''
    result = []
    for texts in texts_list:
        for text in texts:
            for t in serchList:
                if t in text:
                    result.append(t)
    if len(result) > 0:
        result = list(set(result))
        return "".join(result)
    return "不分"

#提取子类型
def get_info_by_list(texts_list,serchList):
    '''
    :param texts_list:
    :param serchList:
    :return:
    '''
    result = []
    for texts in texts_list:
        for text in texts:
            for t in serchList:
                if t in text:
                    result.append(t)
    if len(result) > 0:
        result = list(set(result))
        return "".join(result)
    return "不分"


def get_productName_voting(kvs_list,texts_list):
    result_list = []
    pre_result_list =[]
    abort_list = ['联名','1','是', '吹', '刷', '装', '测', '制','提取','配','用','类型','美型','教','含量']
    pattern_1 = "(\w+薄荷糖|\w+薄荷味糖|\w+柠檬味糖|\w+荷风味糖|\w*薄荷味\w*|\w*梨膏糖|\w*维生素|\w*秋梨软糖|\w+爆珠糖|\w+凝胶糖果|\w*\W?润喉糖|" \
                "\w*润喉糖|\w+颗粒糖|\w+棒棒糖|\w*梨膏糖|\w+枇杷糖|\w+冰爽糖|\w+大海糖|\w*秋梨膏|\w*无糖含片|\w+压片糖果|\w+硬质糖果|\w*金银花含片|" \
                "\w+口宝含片|罗汉果糖|\w+软糖|\w+蜂胶糖|\w+珊瑚糖|\w+含片|\w*咽喉片|\w*金银花糖|\w+胶姆糖|诺特兰德|" \
                "\w+泡泡糖|\w+胶基糖果|奥特陀螺蛋|\w+蔗糖|\w+柠檬味|\w+柠檬红茶味|\w+玫瑰花可乐味|\w+水蜜桃味)$"
    pattern_2 = pattern_1.replace("+","*").replace("$","")
    pattern_3 = "\w+片$|\w+糖果?$"
    pattern_4 = "\w+糖果"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["品名","名"]):
                    if len(kv[k]) > 1 :
                        if '(' in kv[k]:
                            kv[k] = kv[k].split('(')[0]
                        flag = True
                        for it in abort_list:
                            if it in kv[k]:
                                flag = False
                                break
                        if flag:
                            pre_result_list.append(kv[k])

    if len(pre_result_list) > 0:
        return pre_result_list[0]
    for texts in texts_list:
        for text in texts:
            if '类型' not in text:
                p_res = get_info_by_pattern(text, pattern_1)
                if len(p_res) > 0:
                    flag = True
                    for it in abort_list:
                        if it in p_res[0]:
                            flag = False
                            break
                    if flag:
                        result_list.append(p_res[0])

    if len(result_list) > 0:
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        if len(count) == 1:
            return count[0][0]
        else:
            if count[0][1] < count[1][1]:
                return count[1][0]
            else:
                return count[0][0]

    for texts in texts_list:
        for text in texts:
            if '类型' not in text:
                p_res = get_info_by_pattern(text, pattern_2)
                if len(p_res) > 0:
                    flag = True
                    for it in abort_list:
                        if it in p_res[0]:
                            flag = False
                            break
                    if flag:
                        result_list.append(p_res[0])
    if len(result_list) > 0:
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        if len(count) == 1:
            return count[0][0]
        else:
            if count[0][1] < count[1][1]:
                return count[1][0]
            else:
                return count[0][0]

    for texts in texts_list:
        for text in texts:
            if '类型' not in text:
                p_res = get_info_by_pattern(text, pattern_3)
                if len(p_res) > 0:
                    flag = True
                    for it in abort_list:
                        if it in p_res[0]:
                            flag = False
                            break
                    if flag:
                        result_list.append(p_res[0])

    if len(result_list) > 0:
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        if len(count) == 1:
            return count[0][0]
        else:
            if count[0][1] < count[1][1]:
                return count[1][0]
            else:
                return count[0][0]

    for texts in texts_list:
        for text in texts:
            if '类型' not in text:
                p_res = get_info_by_pattern(text, pattern_4)
                if len(p_res) > 0:
                    flag = True
                    for it in abort_list:
                        if it in p_res[0]:
                            flag = False
                            break
                    if flag:
                        result_list.append(p_res[0])

    if len(result_list) > 0:
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        if len(count) == 1:
            return count[0][0]
        else:
            if count[0][1] < count[1][1]:
                return count[1][0]
            else:
                return count[0][0]
    return '不分'

def get_productName_new(product_name):
    pattern_1 = "^牌"
    p_res = get_info_by_pattern(product_name, pattern_1)
    if len(p_res) > 0:
        product_name = product_name.replace('牌', '')
    product_name = re.sub('\W', "", product_name)
    product_name = re.sub('峰密', "蜂蜜", product_name)
    product_name = re.sub('金良花', "金银花", product_name)
    product_name = re.sub('春柠', "青柠", product_name)
    product_name = re.sub('批杷', "枇杷", product_name)
    product_name = re.sub('尊荷味', "薄荷味", product_name)
    product_name = re.sub('甜膏', "梨膏", product_name)
    product_name = re.sub('合片', "含片", product_name)
    if product_name.find('名') == 0:
        product_name = product_name[1:]
    return product_name

#调用公告方法提取口味
def get_taste_bak(texts_list,product_name):
    '''
    调用公告方法提取饼干口味
    基本思路是要维护口味列表139_taste_list，根据商品名称全程和口味列表进行匹配提取
    :param texts_list:
    :param product_name:
    :return:
    '''
    pattern = "(\w+味)"
    abort_list=['西瓜','别咬我']
    result = get_info_list_by_list([[product_name,],], Taste_list_1)
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
    taste = ''
    if len(result) == 0:
        taste = get_taste_normal(texts_list, Taste_list_1)
    else:
        result = list(set(result))
        taste =  "".join(result)
    taste = re.sub('演荷', "薄荷", taste)
    for it in abort_list:
        if it in taste:
            taste = re.sub(it, "", taste)
    if len(taste) == 0:
        taste = '不分'
    return taste

#提取口味
def get_taste(texts_list,product_name):
    '''
    调用公告方法提取饼干口味
    基本思路是要维护口味列表114_taste_list，根据商品名称全程和口味列表进行匹配提取
    :param texts_list:
    :param product_name:
    :return:
    '''
    abort_list=['西瓜','别咬我']
    taste = get_taste_normal(texts_list, Taste_list_1)
    # for it in abort_list:
    #     if it in taste:
    #         taste = re.sub(it, "", taste)
    if len(taste) == 0:
        taste = '不分'
    else:
        taste = re.sub('演荷', "薄荷", taste)
    return taste

#提取糖体形状
def get_suger_shape(brand,product_name,type):
    '''
    提取糖体形状
    提取依据：114定义文档、及人为标注Excel测试数据、KWPO品类数据审核_20211231.xlsx
    提取思路：形状包含：粒状、砖状、球状、短厚片状、长薄片状、块状、卷状、圆环状、其它（请注明)
    1、目前有少数口香糖品牌有短厚片状，如炫迈、乐天、曼妥思、TRIDENT LAYERS
    2、目前已经没有“片状”糖体形状，一定要区分出是“短厚片状”还是“长薄片状”
    3、圆环状：糖体形状为圆环状，一般全称中会有“哨”字样，雀巢宝路目前都归为圆环状
    4、球状：糖体形状为小球（丸）状。
    5、砖状：糖体形状是(正方体)砖的形状，参考产品图片上的信息进行判断。
    6、压粉型硬糖大多为“粒状”不应出现“片状“的产品
    7、“短厚片状”、“长薄片状”产品多在泡泡糖和口香糖中出现。薄荷糖和润喉糖这个两个片状产品很少。
    8、块状：目前大部份是泡泡糖。短厚片状目前没有在泡泡糖中出现。
    9、全称中有含片字样的不一定是“短厚片状”和“长薄片状”，大部份的“含片”应归为“粒状”
    10、“长薄片状”、“短厚片状”、块状的区别之一“厚度”，一般情况下 长薄片状 ≤ 短厚片状 ≤ 块状
    11、长薄片状只可能出现在口香糖和泡泡糖中，短厚片状只会出现在口香糖
    12、徐福记的嘟嘟泡水果味泡泡糖应该是块装的，而不是长薄片状。
    13、目前大部分测试数据都是粒状，因此默认是粒状
    :param brand: 品牌
    :param product_name: 全称
    :param type: 类型
    :return:
    '''
    shape='粒状'
    if '含片' in product_name:
        shape = '粒状'
    elif '哨' in product_name or brand == '宝路':
        shape = '圆环状'
    return shape

def get_package_114(base64strs):
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

    if material == "塑料底" or "塑料" in material:
        material = "塑料"
    elif material == "玻璃底":
        material = "玻璃"

    if shape == "立式袋":
        return "自封袋装"
    elif "袋" in shape:
        return "袋装"
    elif "瓶" in shape:
        return "瓶装"
    else:
        shape = "盒"

    if material == "金属":
        return "金属盒(铁盒)"

    return material + shape

def category_rule_114(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    taste_1 = "不分"
    taste_2 = "不分"
    type = "不分"
    type_2 = "不分"
    package = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    capcity_3 = "不分"
    product_name = "不分"
    shape = "不分"
    jiaxin = "不分"
    suger = "不分"

    dataprocessed.sort(key=lambda c: (len(c), len(str(c))), reverse=True)
    datasorted.sort(key=len)

    brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], [],[])
    brand_1 = brand_1 if brand_1 != "Extra" else "益达"
    brand_1 = re.sub("DOUBLEMINT","绿箭",brand_1,re.IGNORECASE)

    if product_name == "不分":
        product_name = get_productName_voting(dataprocessed,datasorted)
        product_name = get_productName_new(product_name)
    if brand_1!='不分':
        if (len(product_name)-len(brand_1))>1:
            product_name = re.sub(brand_1, "", product_name)

    type = get_type(datasorted, Type_list, product_name)

    type_2 = get_keyValue(dataprocessed, ["品类"])
    if type_2 == "不分":
        # 泡泡糖和口香糖不用区分子类型
        type_2 = get_Type2_list(datasorted,Type_list_2)
    type_2 = re.sub('、', '，', type_2)
    type_2 = re.sub('^\W', '', type_2)


    # 包袋盒罐支杯粒瓶片
    capcity_1 ,capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐支杯粒瓶片", 0)

    taste_1 = get_taste(datasorted,product_name)
    if taste_2 == "不分":
        # 1、根据产品包装上注明的相关口味特殊形容词字样。如特强、超酷、强劲、清劲、超爽等。
        # 2、其他相关水果蔬菜等口味都是写在口味1里，不要抄录在口味2里，
        # 3、口味2里只放特殊形容词，如果不能区分两个字段优先写在口味1里
        taste_2 = get_info_by_list(datasorted,Taste_list_2)
    if type == "不分":
        if "硬" in type_2 or "胖大海" in taste_1 or "罗汉果" in taste_1 or "草珊瑚" in taste_1 or "含片" in type_2 :
            type = "润喉糖"
        if "吹泡" in type_2 :
            type = "泡泡糖"
    # 泡泡糖和口香糖不用区分子类型
    if (type == "泡泡糖" or type == "口香糖"):
        type_2 = "NA"


    jiaxin = get_info_by_list(datasorted,["果心","夹心","冻心","馅","软心","爆浆","流心","注心"])
    jiaxin = "夹心" if jiaxin != "不分" else "无夹心"

    suger = get_sugar_list(datasorted,["无糖","木糖醇","free","Xylitol","Extra",'糖醇','甜味剂'])
    suger = "无糖" if suger != "不分" else "含糖"

    # if "混合水果味" in taste_1:
    #     taste_1 = "混合水果味"
    # elif "果味" in taste_1:
    #     taste_1 = "水果味"

    package = get_package_114(base64strs)
    shape = get_suger_shape(brand_1,product_name,type)
    # 类型
    result_dict['info1'] = type
    # 口味1
    result_dict['info2'] = taste_1
    # 包装形式
    result_dict['info3'] = package
    # 糖体形状
    result_dict['info4'] = shape
    # 口味2
    result_dict['info5'] = taste_2
    # 重量2
    result_dict['info6'] = capcity_3
    # 子类型
    result_dict['info7'] = type_2
    # 是否夹心
    result_dict['info8'] = jiaxin
    # 是否含糖
    result_dict['info9'] = suger
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    real_use_num = 9
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = ""

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_1\114-口香糖泡泡糖润喉糖薄荷糖'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3097214"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_114(image_list)
        with open(os.path.join(root_path, product) + r'\%s_new.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)