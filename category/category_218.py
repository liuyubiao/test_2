import os
import re
import json

from util import *
from glob import glob
from utilCapacity import get_capacity


LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/218_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/218_brand_list_2",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/218_type_list",encoding="utf-8").readlines())]
Place_list = [i.strip() for i in set(open("Labels/218_place_list",encoding="utf-8").readlines())]

Brand_list_1.sort(key=len,reverse=True)

def get_brand_list_wll(texts_list,Brand_list_1,Brand_list_2,keyWords,abortWords,num = 2):
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

def get_keyValue_218(kvs_list,keys):
    for kvs in kvs_list:
        for kv in kvs:
            for key in keys:
                for k in kv.keys():
                    if len(key) == 1:
                        if key == k:
                            return kv[k]
                    else:
                        if key in k and len(k) < 6 and len(kv[k]) >1:
                                return kv[k]
    return "不分"

#产地
def get_place(texts_list):
    # 优先外国
    pattern_absort= "中级"
    pattern = "俄罗斯|韩国|比利时|澳大利亚|法国|意大利|智利|西班牙|阿根廷|格鲁吉亚|德国|美国|新西兰|南非|智利|阿塞拜疆|南非西开普|加拿大|摩尔多瓦"
    result_list_1 = []
    result_list_2 = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "的" not in p_res[0] and len(re.compile("[、，,：]").findall(text)) == 0 and len(re.compile(pattern_absort).findall(text)) == 0:
                    if len(re.compile("进口|产[国地]").findall(text)) > 0:
                        result_list_1.append(p_res[0])
                    else:
                        result_list_2.append(p_res[0])

    if len(result_list_1) > 0:
        count = Counter(result_list_1).most_common(2)
        return count[0][0]
    elif len(result_list_2) > 0:
        count = Counter(result_list_2).most_common(2)
        return count[0][0]

    #wll添加字段规则2023-3-1 17:14:00
    pattern = "玛歌|波多尔|朗格多克|法[园临]"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "法国"

    pattern = "霍克湾"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "新西兰"
    return "不分"


#分类
def get_type_1(texts_list):
    pattern = "(桃红|淡红|玫瑰红|橘红|砖红|北冰红|宝石红|玫瑰蜜|樱桃红)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "干([红白])"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "([红白])葡萄酒?"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

#类型
def get_type_2(texts_list):
    #所有类型内容
    pattern = "("
    for i in Type_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                #return p_res[0]返回数组中的第一个，↓↓↓全部返回并且将数组转化为字符串格式
                delim = ','
                content = delim.join(p_res)
                return content

    return "不分"

#含糖类型：wll新增判断：2023-2-28 16:46:10
def get_type_3(texts_list):
    pattern = "(半甜|半载)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return p_res[0]
                return "半甜"

    # wll新增含糖量类型判断条件（甜红、甜山）：2023-2-28 14:11:08
    pattern = "(甜加香|甜红|甜山|甜型)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return p_res[0]
                return "甜"

    pattern = "(半[干千于]红|半[干千于]型)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "半干"

    pattern = "([干千于]红|[干千于]型)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "干"

    return "不分"

#商品全称
def get_productName_voting(kvs_list,texts_list):
    pattern_absort = "^葡萄"
    pattern1 = "(\w+[葡荷][药简萄葡]酒|\w+香槟|\w+冰酒|\w+果酒)$"
    pattern2 = "(\w+葡萄酒|\w+香槟)"
    pattern3 = "\w+葡萄汁|\w+葡萄起泡酒"
    result_list = []
    result_list_tmp = []
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称", "名"]):
                    if len(kv[k]) > 1 and len(re.compile("[酒槟]").findall(kv[k])) > 0:
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

#起泡
def get_qipao(texts_list):
    pattern = "[微起气汽]泡"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "起泡"

    return "不分"

def get_year(texts_list):
    pattern = "^\d{4}$"
    result_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                if int(p_res[0]) > 1900 and int(p_res[0]) < 2023:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return "不分"

def category_rule_218(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    type_1 = "不分"
    type_2 = "不分"
    type_3 = "不分"
    placeOrigin = "不分"
    qipao = "不分"
    # brand_tmp = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    if product_name == "不分":
        product_name = get_productName_voting(dataprocessed,datasorted)



    product_name = re.sub("[十于千下]白", "干白", product_name)
    product_name = re.sub("[十于千下]红", "干红", product_name)
    product_name = re.sub("席之眼", "鹰之眼", product_name)
    product_name = re.sub("勃拉奶", "勃拉姆", product_name)

    product_name = re.sub("[葡荷][简葡药][酒道]", "葡萄酒", product_name)

    #wll添加品牌字段规则：2023-2-28 10:47:47
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list_wll(datasorted, Brand_list_1, Brand_list_2, ["CLASICO","富采","富隆","天使","民权","民雄","MISSION","名仕","DZC","1752","JAD"], [])
    brand_1 = re.sub("风特堡","枫特堡",brand_1)
    brand_1 = re.sub("民雄", "民权", brand_1)
    brand_1 = re.sub("^Penfolds$", "奔富PENFOLDS", brand_1,re.IGNORECASE)
    brand_1 = re.sub("^SAFLAM$", "西夫拉姆SAFLAM", brand_1, re.IGNORECASE)

    if brand_1 != "不分":
        brand_len = len(brand_1)
        for i in range(brand_len):
            brand_tmp = brand_1[i:]
            if brand_tmp in product_name:
                product_name = re.sub("^" + brand_tmp,"",product_name)
                break

    year = get_year(datasorted)
    if year != "不分" and year not in product_name and product_name != "不分":
        product_name = product_name + "，" + year

    #产地:info3（wll新增字段规则）
    if placeOrigin == "不分":
        placeOrigin = get_place(datasorted)

    # wll添加重容量：2023-2-23 14:37:31
    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "ml|毫[升元开]|mL|L|[升元开]|ML", "袋盒桶罐瓶", 1)

    capcity_2 = re.sub("[元开]", "升", capcity_2)
    capcity_1 = re.sub("[元开]", "升", capcity_1)
    if len(re.compile("^75\D").findall(capcity_1)) > 0:
        capcity_1 = "750毫升"

    if len(re.compile("^[a-zA-Z]{1,2}[\u4e00-\u9fa5]").findall(product_name)) > 0:
        product_name = re.sub("^[a-zA-Z]+", "", product_name)

    qipao = get_qipao(datasorted)

    if type_1 == "不分":
        type_1 = get_type_1(datasorted)
    if type_2 == "不分":
        type_2 = get_type_2(datasorted)
    if type_3 == "不分":
        type_3 = get_type_3(datasorted)


    if type_1 == "不分" and "干" in type_3:
        type_1 = "红"


    result_dict['info1'] = type_1
    result_dict['info2'] = type_2
    result_dict['info3'] = placeOrigin
    result_dict['info4'] = qipao
    result_dict['info5'] = type_3
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\218-葡萄酒（含香槟）'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3046888"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_218(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)