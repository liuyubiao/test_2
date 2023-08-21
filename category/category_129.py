import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/129_brand_list",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/129_taste_list",encoding="utf-8").readlines())]

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

def get_taste(texts_list,product_name):
    pattern = "([\u4e00-\u9fa5]+味)"
    result = []
    if len(product_name) > 4:
        result = get_info_list_by_list([[product_name,],], Taste_list)
        if len(result) == 0:
            p_res = re.compile(pattern).findall(product_name)
            if len(p_res) > 0 and p_res[0] not in Taste_Abort_List_pres:
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
    pattern_text = "[、，,]|干燥|产品类型|参考"
    pattern_pres = "^(果[味肉]|含乳|味)型果冻$|^[吃的]|其他|挤出|冰冻$|^认真果冻$"
    result_list = []
    result_list_tmp = []
    pattern_1 = "([\w\-]+[果梅]冻|\w*梨膏冻|[\w\-]+[布果][丁町]|\w+吸吸冻|\w+沙棘膏|\w+果Q乐|\w+果味爽|\w+甜品锅|\w+果汁[冰冻]|\w+[果菓]乐吸|\w+水果杯|\w*蒸雪糕)($|\()"
    pattern_2 = "[\w\-]+[果梅][冻片]|\w*梨膏冻|[\w\-]+[布果][丁町]|\w+吸吸冻|\w+沙棘膏|\w+果Q乐|\w+果味爽|\w+[果菓]乐吸|\w+冰淇淋$"
    pattern_3 = "(\w+冻)($|\()"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("[冻丁膏果町冰]").findall(kv[k])) > 0:
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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0]:
        return count[1][0]
    return count[0][0]

def get_package_pre(texts_list):
    for texts in texts_list:
        for text in texts:
            if len(re.compile("\d+杯|[杯粒][装型]").findall(text)) > 0:
                return True
    return False

def get_package_129(base64strs):
    url_shape = url_classify + ':5029/yourget_opn_classify'
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    result_shape = task_shape.get_result()

    if len(result_shape) > 0:
        shape = Counter(result_shape).most_common(1)[0][0]
        if "吸嘴袋" in result_shape:
            shape = "吸嘴袋"
        elif "袋" in shape:
            shape = "袋"
        elif "桶" in shape or "杯" in shape or "瓶" in shape:
            shape = "杯"
        elif shape in ["托盘", "格", "盒"]:
            shape = "盒"
        elif shape in ["碗"]:
            shape = "碗"
        else:
            shape = "杯"
        return shape + "装"
    else:
        return "杯装"

def category_rule_129(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    taste = "不分"
    package = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,[],["OCOCO","FKO","keep","COCON","Aji","Zk","小熊","TmJ",
                                                                      "Ozi","妙趣多","a1","我得","NBR","小黄鸭","班同学","袋享",
                                                                      "UNO","UDK","DOLE","元气"],[])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("町の锈惑", "町の诱惑", brand_1)
    brand_1 = re.sub("纤秀生", "纤秀1生", brand_1)
    brand_1 = re.sub("果叮星语", "果町星语", brand_1)
    brand_1 = re.sub("金祺语", "金祺之语", brand_1)
    brand_1 = re.sub("^SOHAMU$", "邂逅SOHAMU", brand_1)
    brand_1 = re.sub("[塑望]小[纟幺]", "望小幺", brand_1)
    brand_1 = re.sub("South.Littlebird", "南小鸟", brand_1)
    brand_1 = re.sub("班同学","二班同学",brand_1)
    brand_1 = re.sub("果篮东", "果篮冻", brand_1)
    brand_1 = re.sub("JOYNOW", "JOYNOW及乐", brand_1)
    brand_1 = re.sub("迪土尼", "迪士尼", brand_1)
    brand_1 = re.sub("HAOQU", "好趣", brand_1)
    brand_1 = re.sub("赞物", "赞扬", brand_1)
    brand_1 = re.sub("奶花nailong", "奶龙", brand_1)


    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒杯个", 0)

    capcity_1 = re.sub("00[89][克g]","00克",capcity_1)

    # datasorted = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("[蒟蒻萄药葫萌菊藕幕场蒋苪商][蒻萄药葫萌菊藕薯幕葬万歌葛蔬拌蒋蘭鹅]?果冻", "蒟蒻果冻", product_name)
    product_name = re.sub("[蒟蒻萄药葫萌菊藕幕场蒋苪商][蒻萄药葫萌菊藕薯幕葬万歌葛蔬拌蒋蘭鹅]?椰冻", "蒟蒻椰冻", product_name)
    product_name = re.sub("[蒟蒻萄药葫萌菊藕幕场蒋苪商][蒻萄药葫萌菊藕薯幕葬万歌葛蔬拌蒋蘭鹅]?棒", "蒟蒻棒", product_name)
    product_name = re.sub("[蒟蒻萄药葫萌菊藕幕场蒋苪商][蒻萄药葫菊藕薯幕葬万歌葛蔬拌蒋蘭鹅]", "蒟蒻", product_name)
    product_name = re.sub("[菜]冻", "果冻", product_name)
    product_name = re.sub("南瓜十", "南瓜汁", product_name)
    product_name = re.sub("果十", "果汁", product_name)
    product_name = re.sub("^吸", "可吸", product_name)

    product_name = re.sub("柑得", "柑橘", product_name)
    product_name = re.sub("郴果", "椰果", product_name)
    product_name = re.sub("荔祛", "荔枝", product_name)
    product_name = re.sub("肉桃", "白桃", product_name)
    product_name = re.sub("蜜插", "蜜橘", product_name)
    product_name = re.sub("草[鹤藜]", "草莓", product_name)

    product_name = re.sub("混合口$", "混合口味", product_name)
    product_name = re.sub("^\w布丁", "布丁", product_name)
    product_name = re.sub("^\w果冻", "果冻", product_name)

    product_name = re.sub("\(\w{0,2}$", "", product_name)
    product_name = re.sub("\)\w{0,2}$", ")", product_name)
    product_name = re.sub("^\w*品名称?", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)
    product_name = re.sub("\d+[gG克]$", "", product_name)

    taste = get_taste(datasorted, product_name)

    taste = re.sub("柑得", "柑橘", taste)
    taste = re.sub("荔祛", "荔枝", taste)
    taste = re.sub("草草", "草莓", taste)
    taste = re.sub("艺果", "芒果", taste)

    package_pre = get_package_pre(datasorted)
    if package_pre:
        package = "杯装"
    else:
        package = get_package_129(base64strs)

    result_dict['info1'] = taste
    result_dict['info2'] = package
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 2
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
        result_dict = category_rule_129(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)