import os
import re
import json

from util import *
from glob import glob
from utilCapacity import get_capacity
from util import get_info_item_by_list,get_info_list_by_list


LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/223_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/223_brand_list_2",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/223_type_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/223_taste_list",encoding="utf-8").readlines())]

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")

def get_keyValue(kvs_list,keys):
    result_list = []
    for kvs in kvs_list:
        for kv in kvs:
            for key in keys:
                for k in kv.keys():
                    if len(key) == 1:
                        if key == k:
                            result_list.append(kv[k])
                    else:
                        if key in k and  len(k) < 6 and len(kv[k]) > 1:
                            result_list.append(kv[k])

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) >1 and count[0][1] == count[1][1] and len(count[0][0]) < len(count[1][0]) and len(re.compile("[0-9,，、]").findall(count[1][0])) == 0:
        return count[1][0]
    else:
        return count[0][0]

def get_brand_list(texts_list,Brand_list_1,Brand_list_2,keyWords,abortWords,num = 2):
    brand_1_tmp_list = []
    brand_1_txt_list = []
    brand_1_merge_tmp_list = []
    brand_1_merge_list = []
    brand_1_merge_absort_list = []
    brand_2 = []
    for texts in texts_list:
        # text_str = TextFormatNormal(texts)
        text_str = "".join(texts)
        text_str_ori = ",".join(texts)
        for bb in Brand_list_1:
            if bb in text_str :
                if len(bb) > 2:
                    brand_1_merge_tmp_list.append(bb)
                elif len(re.compile("(,|^)%s($|,)"%(",".join(list(bb)))).findall(text_str_ori)) > 0:
                    brand_1_merge_tmp_list.append(bb)
        for text in texts:
            if text in keyWords:
                brand_1_txt_list.append(text)
            for b1 in Brand_list_1:
                if b1.upper() in text.upper() or b1 in text:
                    if b1 == text and b1 not in abortWords:
                        brand_1_txt_list.append(text)
                    if len(b1) > num or (len(re.compile("[市省镇区村县请勿]|大道|街道").findall(text)) == 0 and "地址" not in text):
                        brand_1_tmp_list.append(b1)
                    else:
                        brand_1_merge_absort_list.append(b1)

        for b2 in Brand_list_2:
            if b2 in texts:
                brand_2.append(b2)

    if len(brand_2) > 0:
        brand_2 = ",".join(list(set(brand_2)))
    else:
        brand_2 = "不分"

    for bm in brand_1_merge_tmp_list:
        if bm not in brand_1_tmp_list:
            brand_1_merge_list.append(bm)

    # wll修改位置：2023-3-28 17:21:33
    if len(brand_1_merge_tmp_list) > 0:
        count = Counter(brand_1_merge_tmp_list).most_common(1)
        brand_1 = count[0][0]
        if brand_1 not in brand_1_merge_absort_list:
            return brand_1,brand_2

    if len(brand_1_txt_list) > 0:
        brand_1_tmp_list.sort(key=len, reverse=True)
        count = Counter(brand_1_txt_list).most_common(1)
        brand_1 = count[0][0]
    else:
        brand_1_list = []
        for i in brand_1_tmp_list:
            flag = True
            for j in brand_1_tmp_list:
                if j != i and i in j:
                    flag = False
                    break
            if flag:
                brand_1_list.append(i)

        if len(brand_1_list) == 0:
            brand_1 = "不分"
        else:
            brand_1_list.sort(key=len, reverse=True)
            count = Counter(brand_1_list).most_common(1)
            brand_1 = count[0][0]
    return brand_1,brand_2

#口味
def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    result = get_info_list_by_list([[product_name,]], Taste_list)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0 and p_res[0] not in ["口味","新口味", "风味", "天高新味"]:
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
        dejoy = ","
        return dejoy.join(result)

#类型
def get_type(texts_list):
    pattern = "("
    for i in Type_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "祁红|红豆|金骏眉"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "红茶"

    pattern = "竹叶青|银毫|毛尖|龙井|碧螺春|炒青|毛峰|珠茶|珍眉|秀眉|辣木"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "绿茶"

    pattern = "铁观音|岩茶|水仙|冻顶乌龙|单枞|肉桂|鸭屎香|大红袍"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "乌龙茶"

    pattern = "茉莉花|花毛峰|茉莉白毫|茉莉银毫|茉莉银尖"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "茉莉花茶"

    pattern = "刺梨|桑葚干|莓茶|[刺雪]梨|[白|水蜜|蜜]桃|鲜花|马齿苋|柠檬|菠萝|枇杷|金桔|百香果|玛咖|荷叶|薰衣草"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "花果茶"

    pattern = "姜|决明子|蒲公英|牛蒡|菊[花粉]|桂圆|薄荷|陈皮|薏米|玉米须|枸杞|金银花|葛根|甘草|干姜|茯苓|柠叶|勒花|四洋参|黄药|溪黄"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "中草药"

    pattern = "普洱|白茶|黄茶|银针|白牡丹|黄芽|大叶青|苦荞|寿眉春|玉米"
    for texts in texts_list:
        for productname in texts:
            p_res = get_info_by_pattern(productname, pattern)
            if len(p_res) > 0:
                return "其它"

    return "不分"

#子类
def get_type_2(texts_list):
    pattern = "茶粉|奶茶|固体饮料"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "茶粉"

    pattern = "茶液|果汁"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "茶液"

    pattern = "冻干|冻干茶块"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "冻干茶块"

    return "不分"

#商品全称
def get_productName(kvs_list,texts_list):
    pattern_absort = "[投为好上盖园尺角森暖用味林茶结]茶|\d*克|市"
    pattern1 = "(\w*菊花茶|\w*普洱茶?|\w*柠檬[茶片]|\w*茯苓茶|\w*枸杞茶|\w*龙井茶?|\w*金骏眉|\w*竹叶青|\w*茉莉花茶|\w*大红袍|\w*甘草片|\w*玛咖片|\w*绿毛峰|\w*抹茶粉|\w*椰子粉|\w*铁观音|\w*刺梨|\w*桑葚干|\w*姜[粉汤茶]|\w*薄荷叶|\w*甘露茶|\w*毛尖|\w*金银花)$"
    pattern2 = "\w*[白花红果]茶|\w*普洱茶|\w*柠檬茶|\w*茯苓茶|\w*枸杞茶|\w*龙井茶|\w*大红袍|\w*甘草片|\w*铁观音|\w*毛尖|\w*玛咖片|\w*绿毛峰|\w*抹茶粉|\w*椰子粉|\w*铁观音|\w*刺梨|\w*正山小种"
    pattern3 = "(\w+茶[膏饼饮飲]|\w{2,}茶$|\w+固体饮料$|\w*茶包袋$)"

    result_list = []
    result_list_tmp = []

    pattern_tmp = "茶|铁观音|大红袍|毛尖|竹叶青|碧螺春|金骏眉|龙井|普洱|陈皮|祁红|胎菊|小种"
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in [ "名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("[委托单位|生产|企业]").findall(kv[k])) ==0 and len(re.compile(pattern_tmp).findall(kv[k])) > 0:
                        result_list.append(kv[k])
                    elif len(kv[k]) > 1:
                        result_list_tmp.append(kv[k])

    if len(result_list_tmp) == 0:
        product_name_tmp = "不分"
    else:
        count = Counter(result_list_tmp).most_common(2)
        product_name_tmp = count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern1)
            if len(p_res) > 0:
                p_res = p_res[0]
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(text)) ==0 and len(re.compile(pattern_absort).findall(text)) == 0:
                    result_list.append(p_res)

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]


    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern2)
            if len(p_res) > 0:
                p_res = p_res[0]
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(text)) ==0 and len(re.compile(pattern_absort).findall(text)) == 0:
                    result_list.append(p_res)

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern3)
            if len(p_res) > 0:
                p_res = p_res[0]
                if "的" not in p_res[0] and len(re.compile("[、，,]").findall(text)) ==0 and len(re.compile(pattern_absort).findall(text)) == 0:
                    result_list.append(p_res)

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return product_name_tmp

def get_package_223(base64strs):
    url_shape = url_classify + ':5029/yourget_opn_classify'
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    result_shape = task_shape.get_result()

    if len(result_shape) > 0:
        shape = Counter(result_shape).most_common(1)[0][0]
        if "袋" in shape:
            shape = "袋"
        elif "瓶" in shape:
            shape = "瓶"
        elif "桶" in shape or "杯" in shape:
            shape = "杯"
        elif shape in ["托盘","格","盒"]:
            shape = "盒"
        elif "罐" in shape:
            shape = "罐"
        elif "礼包" in shape:
            shape = "礼盒"
        else:
            shape = "盒"
        return shape
    else:
        return "盒"

def category_rule_223(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    taste = "不分"
    package = "不分"
    bag = "不分"
    type_1 = "不分"
    type_2 = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # wll添加品牌字段规则：2023-3-14 09:53:44
    if brand_1 == "不分":
        brand_1 = get_keyValue(dataprocessed,["品牌"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["汉中","999","CHALI","RIO","AJI","一杯香","春光",
                                                                         "MIA","RG","白果","论道","简茶","中茶","岳西","天香",
                                                                         "DN5","强香","瑰香","金花","源于花香","邻品"], [])

    brand_1 = re.sub("老侯节","老侯爷",brand_1)
    brand_1 = re.sub("焦韵堂", "谯韵堂", brand_1)
    brand_1 = re.sub("孙思邀", "孙思邈", brand_1)
    brand_1 = re.sub("青進里", "青谯里", brand_1)
    brand_1 = re.sub("JlaSuperfood", "OlaSuperfood", brand_1)
    brand_1 = re.sub("谁客", "谯客", brand_1)
    brand_1 = re.sub("漓早鲜", "漓果鲜", brand_1)
    brand_1 = re.sub("德鑫堂", "谯鑫堂", brand_1)
    brand_1 = re.sub("微娘子", "徽娘子", brand_1)
    brand_1 = re.sub("肚草堂", "彤草堂", brand_1)
    brand_1 = re.sub("悦来秀", "悦来香", brand_1)
    brand_1 = re.sub("天原居", "天源居", brand_1)

    if product_name == "不分":
        product_name = get_productName(dataprocessed, datasorted)

    product_name = re.sub("[芳茗]荞茶", "苦荞茶", product_name)
    product_name = re.sub("安吉自茶", "安吉白茶", product_name)
    product_name = re.sub("幕漫红茶", "雾漫红茶", product_name)
    product_name = re.sub("萄茶", "莓茶", product_name)
    product_name = re.sub("磊枝红茶", "荔枝红茶", product_name)
    product_name = re.sub("甘四味", "廿四味", product_name)
    product_name = re.sub("金银花医清茶", "金银花莲清茶", product_name)
    product_name = re.sub("[菜莱]莉花", "茉莉花", product_name)
    product_name = re.sub("口粮红浆", "口粮红茶", product_name)
    product_name = re.sub("四际贡茶", "四保贡茶", product_name)
    product_name = re.sub("寿唐散茶", "寿眉散茶", product_name)
    product_name = re.sub("工茶", "红茶", product_name)
    product_name = re.sub("干[姜菱][活汤]", "干姜汤", product_name)
    product_name = re.sub("牛[费劳]", "牛蒡", product_name)
    product_name = re.sub("鸟龙", "乌龙", product_name)
    product_name = re.sub("苦养茶", "苦荞茶", product_name)
    product_name = re.sub("美茶", "姜茶", product_name)
    product_name = re.sub("菌花", "菊花", product_name)
    product_name = re.sub("减味", "咸味", product_name)
    product_name = re.sub("慧米", "薏米", product_name)
    product_name = re.sub("海堤", "海提", product_name)

    product_name = re.sub("^\w*品名称?", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    #wll添加重容量字段规则：2023-3-16 10:17:25
    capcity_1 ,capcity_2= get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤|升|毫[开元升]|ML|ml|mL|L", "瓶包袋罐片", 2)

    capcity_2 = re.sub("[元开]", "升", capcity_2)
    capcity_1 = re.sub("[元开]", "升", capcity_1)

    #有无小袋
    if capcity_2 != "不分":
        p_res = re.compile(".*\D+(\d+)小?[袋包]?$").findall(capcity_2)
        if len(p_res) > 0 and float(p_res[0]) != 1.0:
            bag = "有小袋"
    if bag == "不分" and capcity_2 != "不分":
        bag = "有小袋"

    #类型
    type_1 = get_type([[product_name,],])
    if type_1 == "不分":
        type_1 = get_type(datasorted)
    if type_1 == "不分":
        if "果" in product_name or "花" in product_name:
            type_1 = "花果茶"

    # 口味     if type_1 == "奶茶" or "果茶" in type_1:
    taste = get_taste(datasorted,product_name)

    taste = re.sub("水果茶","水果味",taste)

    #子类
    if type_2 == "不分":
        type_2 = get_type_2(datasorted)
    if type_2 == "不分" and bag == "有小袋" :type_2 = "茶袋"
    if type_2 == "不分":type_2 = "茶叶"

    package = get_package_223(base64strs)

    result_dict['info1'] = taste
    result_dict['info2'] = package
    result_dict['info3'] = bag
    result_dict['info4'] = type_1
    result_dict['info5'] = type_2
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\223-固体茶类'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3038991"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_223(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)