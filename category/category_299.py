import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/299_brand_list",encoding="utf-8").readlines())]
Wine_name_1 = ["多二两","1949","1935","粮香","贵州茅台酒","小红粱","贝侬","红高粱","臻定荷花","映山红","烧刀子","国台国标","梦之蓝","海之蓝","天之蓝",
               "等着我","老北京","老瀘州","劍南春","五粮精酿","银劍南","湘之笑","富贵吉祥","富贵三宝","汾藏壹号","役直聘","拜泉7号","國色清香","品鉴壹号",
               "八大碗","瀘州品鉴","赖九禾","红好客","金奖88","小白楊","烈刀子","红好客","小高粱","吉祥陆号","鸿运当头","福瑞连年","國酱","国酱","天津大直沽","天津大直活",
               "温河大王","银荔五谷"]

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

class BigWordUtil():
    def __init__(self):
        self.pattern = "[这名美好饮酿]酒|酒精|公司|酒厂|集团|酒厂|[固周]态法|[低中高]温|[前中尾]段|有害"

    def isNear(self,box,bbox):
        box_x_min = min([x[0] for x in box])

        box_x_max = max([x[0] for x in box])
        box_y_min = min([x[1] for x in box])
        box_y_max = max([x[1] for x in box])

        near_x = 1000
        near_y = 1000
        # for bbox in box_list:
        bbox_x_min = min([x[0] for x in bbox])
        bbox_x_max = max([x[0] for x in bbox])
        bbox_y_min = min([x[1] for x in bbox])
        bbox_y_max = max([x[1] for x in bbox])

        if box_x_max < bbox_x_min or box_x_min > bbox_x_max:
            tmp_x = min(abs(box_x_max - bbox_x_min), abs(box_x_min - bbox_x_max))
        else:
            tmp_x = 0
        if box_y_max < bbox_y_min or box_y_min > bbox_y_max:
            tmp_y = min(abs(box_y_max - bbox_y_min), abs(box_y_min - bbox_y_max))
        else:
            tmp_y = 0

        if tmp_x < near_x:
            near_x = tmp_x
        if tmp_y < near_y:
            near_y = tmp_y

        return near_x + near_y

    def process(self,dataoriginals):
        result_list = []
        max_size = 0
        min_size = 10000
        top_list = []
        bottom_list = []
        max_size_list = []
        min_size_list = []
        max_size_box_list = []
        for dataoriginal in dataoriginals:
            top = 10000
            bottom = 0
            tmp_max_size = 0
            tmp_min_size = 1000
            tmp_box = []
            for index, info in enumerate(dataoriginal):
                box = info["box"]
                size = min(abs(box[0][1] - box[3][1]), abs(box[0][0] - box[1][0]))
                dataoriginal[index]["size"] = size
                if size > max_size:
                    max_size = size
                if size < min_size:
                    min_size = size
                if box[0][1] < top:
                    top = box[0][1]
                if box[0][1] > bottom:
                    bottom = box[0][1]
                if size > tmp_max_size:
                    tmp_max_size = size
                    tmp_box = box
                if size < tmp_min_size:
                    tmp_min_size = size

            top_list.append(top)
            bottom_list.append(bottom)
            max_size_list.append(tmp_max_size)
            min_size_list.append(tmp_min_size)
            max_size_box_list.append(tmp_box)

        for index, dataoriginal in enumerate(dataoriginals):
            top = top_list[index]
            bottom = bottom_list[index]
            m_size = max_size_list[index]
            mm_size = min_size_list[index]
            m_box = max_size_box_list[index]

            height = bottom - top
            if float(m_size / mm_size) > 2.5 and m_size > 80:
                result_txt = []
                for info in dataoriginal:
                    if info["size"] > m_size * 0.7 or (info["size"] > m_size * 0.6 and self.isNear(info["box"], m_box) < info["size"] / 3):
                        if len(re.compile("[a-zA-Z0-9]+$|\W").findall(info["txt"])) == 0 and len(re.compile(self.pattern).findall(info["txt"])) == 0:
                            result_txt.append([info["txt"], info["box"][2][1] + info["box"][0][0]])
                result_txt = sorted(result_txt, key=lambda x: x[1])
                result_txt = [x[0] for x in result_txt]

                res_tmp = []
                if len(result_txt) > 0:
                    for i in result_txt:
                        flag = True
                        for j in result_txt:
                            if i == j:
                                continue
                            if i in j:
                                flag = False
                        if flag:
                            res_tmp.append(i)
                    result_list.append("".join(res_tmp))

        result_list = sorted(result_list, key=len)
        res = []
        if len(result_list) > 0:
            for index, i in enumerate(result_list):
                flag = True
                for j in result_list[index + 1:]:
                    if i in j:
                        flag = False
                if flag:
                    res.append(i)
        res = sorted(result_list, key=len, reverse=True)
        if len(res) == 0:
            return "不分"
        count = Counter(res).most_common(2)
        return count[0][0]

def get_taste_type(texts_list):
    pattern_0 = "[泉特浓清酱兼董荷米粮凤濃陶荞]+·?香型"
    pattern_1 = "[泉特浓清酱兼董荷米粮凤濃陶荞]+·?香"
    taste_list = ["芝麻香型","绵柔型","柔雅型","馥郁香型","糯米酱香型","绵柔浓香型","清芝兼香","小曲清香"]
    t_res = get_info_list_by_list(texts_list, taste_list)
    if len(t_res) > 0:
        return t_res[0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_0)
            if len(p_res) > 0:
                return p_res[0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                return p_res[0] + "型"

    return "不分"

def get_type(texts_list):
    pattern = "老窖|高粱酒|陈酿|大曲|小曲|特[曲麯]|二锅头|老白干|黄酒"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]
    return "不分"

def get_degree(kvs_list,texts_list):
    pattern = "(\d+\.?\d*).?%[Vv][Oo][Ll]$|(\d+\.?\d*).?%[Vv][Oo][Ll][^a-zA-Z0-9]"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                p_res = p_res[0][0] if p_res[0][0] != "" else p_res[0][1]
                if float(p_res) > 20 and float(p_res) < 70:
                    return p_res

    result = get_keyValue(kvs_list, ["酒精度"])
    try:
        result = re.compile("(\d+\.?\d*)").findall(result)[0]
    except:
        result = "不分"

    if result != "不分":
        if float(result) > 20 and float(result) < 70:
            return result

    pattern = "(\d+\.?\d*)%"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                p_res = p_res[0]
                if float(p_res) > 10 and float(p_res) < 75:
                    return p_res
    return "不分"

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

def get_productName_voting(kvs_list,texts_list,texts_original):
    pattern_taste = "^[泉特浓清酱兼董荷米粮凤濃陶]?\w?型|[市县]|产地|生产|放心酒|^\d+[毫mM][升lL]酒$|^\w{0,2}香型|^风味\w*酒|^\w?[白基]酒$|^[小]酒$|^\w{0,2}香风?味|态法|[固周]\w法|[低中高]温|[前中尾]段|有害|酿造[浓清酱兼董荷]香型|^[Vv][Oo0][Ll]|采用|源自|每一|恢复"
    pattern_text = "[请勿]|公司|有限|酒[厂镇]|酒精|[饮配为外日喝]酒|[^陈陳]酿酒|类型|地址|小区|用心|许可|分类|配以|原料|贮存|而成"
    result_list = []
    pattern_1 = "(\w*老白[干千子]|\w{2,}原浆|\w{2,}國酱|\w{2,}品鉴酒|\w{2,}陈[酿坛]|\w{2,}[精秘]酿|\w{2,}[小大特][曲麯]|\w{2,}老窖|\w{2,}古酱酒?|^老窖\w+|^窖藏\w+|\w{2,}[窖酒陶]藏|\w*高[梁粱][红王]|\w*二[锅鍋][头頭]酒?|\w{3,}年陈|\w{2,}[老烧]酒|\w*五粮[春液醇]?|^\w{2,3}[1-9壹]号)($|\()"
    pattern_2 = "(\w+[酒曲])(\(|采用|”|以\w+为|是以)"
    pattern_3 = "\w+[井烧君]坊$|\w*老白干|\w{2,}陈[酿坛]|\w{2,}[精秘]酿|\w{2,}[小大特][曲麯]|\w{2,}老窖|\w{2,}[窖酒]藏|\w*高[梁粱][红王]|\w*二锅头酒?|\w{2,}[一二三四五六七八九十]+年陈|\w{2,}液$|\w+·\w{2,5}"
    pattern_4 = "[\w·]+[^\W这名美好饮酿烈本酒购]酒王?$"
    pattern_5 = "\w*[^\W这名美好饮酿烈本酒购]酒"

    pattern_0 = "产?品名称?\W?([^称\W]+)"
    pattern_pre = "产?品名称?\W*$"
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if "品名" in k or k in ["名","名称"] or len(re.compile("^\w名$").findall(k)) > 0:
                    if len(kv[k]) > 1 and len(re.compile(pattern_text).findall(kv[k])) ==0 and len(re.compile("[Nn]ame").findall(kv[k])) == 0:
                        result_list.append(kv[k])

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_0)
            if len(p_res) > 0 and p_res[0] not in result_list and len(p_res[0]) > 1 and len(re.compile(pattern_text).findall(p_res[0])) ==0 and len(re.compile("[Nn]ame").findall(p_res[0])) == 0:
                result_list.append(p_res[0])


    for texts in texts_list:
        for index, text in enumerate(texts):
            p_res_pre = get_info_by_pattern(text, pattern_pre)
            total_len = len(texts)
            if len(p_res_pre) > 0:
                for i in [1,]:
                    if index + i >= 0 and index + i < total_len:
                        p_res = re.compile("酒|老窖|原浆|特贡").findall(texts[index + i])
                        if len(p_res) > 0 and len(re.compile(pattern_text).findall(texts[index + i])) ==0 and "香型" not in texts[index + i]:
                            result_list.append(texts[index + i])

    for texts in texts_list:
        for text in texts:
            if text in Wine_name_1:
                if "酒" in text:
                    result_list.append(text)
                else:
                    result_list.append(text + "酒")

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                p_res = p_res[0]
                if "的" not in p_res[0] and "饮酒" not in p_res[0] and len(re.compile(pattern_text).findall(text)) ==0 and len(re.compile(pattern_taste).findall(p_res[0])) ==0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                p_res = p_res[0]
                if "的" not in p_res[0] and "饮酒" not in p_res[0] and len(re.compile(pattern_text).findall(text)) ==0 and len(re.compile(pattern_taste).findall(p_res[0])) ==0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "饮酒" not in p_res[0] and len(re.compile(pattern_text).findall(text)) ==0 and len(re.compile(pattern_taste).findall(p_res[0])) ==0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    # tmp_name = getMostCommon(texts_list)
    # if tmp_name != "不分":
    #     return tmp_name

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "饮酒" not in p_res[0] and len(re.compile(pattern_text).findall(text)) ==0 and len(re.compile(pattern_taste).findall(p_res[0])) ==0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_5)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "饮酒" not in p_res[0] and len(re.compile(pattern_text).findall(text)) ==0 and len(re.compile(pattern_taste).findall(p_res[0])) ==0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if int(count[0][1]) > 1:
            return count[0][0]

    bwOBJ = BigWordUtil()
    bwresult= bwOBJ.process(texts_original)
    if len(re.compile(pattern_taste).findall(bwresult)) == 0 and len(re.compile(pattern_text).findall(bwresult)) == 0:
        if len(re.compile("股份|长期").findall(bwresult)) > 0:
            return "不分"
        if bwresult != "不分" and len(re.compile("[酒曲]$").findall(bwresult)) == 0:
            bwresult += "酒"
        return bwresult
    else:
        return "不分"


def TextFormat(texts_list):
    full_text = []
    for texts in texts_list:
        tmp_str = ""
        l = len(texts)
        for index, txt in enumerate(texts):
            if len(re.compile("^[a-zA-Z0-9\W]+$").findall(txt)) > 0 and len(re.compile("^[0-9]+$").findall(txt)) == 0:
                continue
            if len(re.compile("[0-9]{5,}").findall(txt)) > 0:
                continue
            if txt in tmp_str:
                continue
            if txt in ["酒酒"]:
                continue
            if len(txt) > 2 or (index > l/2 + 1 and l > 10 ):
                split_flag = "&"
                if tmp_str != "" and tmp_str[-1] != "&":
                    tmp_str += "&"
            else:
                split_flag = ""
                if txt != "":
                    if "酒" in txt or txt[-1] in ["酿","曲","窖"]:
                        if tmp_str != "" and tmp_str[-1] == "&" and len(re.compile("[\da-zA-Z]&$").findall(tmp_str)) == 0:
                            tmp_str = tmp_str[:-1]
            tmp_str += txt
            if index != l - 1:
                tmp_str += split_flag
        full_text.append(tmp_str.split("&"))
    return full_text

def getMostCommon(texts_list):
    pattern = "^[\u4e00-\u9fa5]{2,5}$"
    pattern_taste = "^[浓清酱兼董荷]?香?型|^\w{0,2}香型|^风味\w*酒|^\w白酒$|^[小]酒|^\w{0,2}香风?味|[固周]态法|[低中高]温|[前中尾]段|有害|酿造[浓清酱兼董荷]香型"
    result_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "的" not in p_res[0] and "饮酒" not in p_res[0] and "酒精" not in text and len(re.compile(pattern_taste).findall(text)) == 0:
                    result_list.append(text)

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if count[0][1] > 1:
            return count[0][0]
    return "不分"


def category_rule_299(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    type = "不分"
    taste = "不分"
    degree = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    brand_1 = get_keyValue(dataprocessed, ["商标","品牌"])
    if len(brand_1) > 6:
        brand_1 = "不分"
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,[],["亳州","如意","逍遥","阿尔山","国酱","东泰","太平","桂花","迎宾","平坝","贵寳","貴賓","有缘","见面礼","杏花村","本草纲目","经典名著","中国人","隋唐","云台山"],[],3)
    if brand_1 == "不分":
        brand_1 = get_info_by_texts_list(datasorted,["贵州茅台镇","贵宾","MAOTAI","贵州茅台","贵州茅台酒"])
    if brand_1 == "不分":
        brand_1 = get_brand(dataprocessed)

    brand_1 = re.sub("陕西凤牌", "凤牌", brand_1)
    brand_1 = re.sub("安北坊", "安兆坊", brand_1)
    brand_1 = re.sub("吃匠", "屹匠", brand_1)
    brand_1 = re.sub("桃儿河", "洮儿河", brand_1)
    brand_1 = re.sub("贵[寳賓]", "贵宾", brand_1)
    brand_1 = re.sub("年栏山", "牛栏山", brand_1)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "[Cc][Mm][lL]|ml|毫升|mL|L|升|ML", "瓶", 1)
    capcity_1 = re.sub("[Cc][Mm][Ll]", "0毫升", capcity_1)
    capcity_2 = re.sub("[Cc][Mm][Ll]", "0毫升", capcity_2)

    datasorted = TextFormat(datasorted)
    product_name_wine = get_productName_voting(dataprocessed,datasorted,dataoriginal)
    # bwOBJ = BigWordUtil()
    # bwresult = bwOBJ.process(dataoriginal)

    product_name_wine = re.sub("\W?[浓清酱兼董荷米]+香型\w*", "", product_name_wine)
    product_name_wine = re.sub("\W?[浓清酱兼董荷米]+香风\w\W+$", "", product_name_wine)
    product_name_wine = re.sub("\W?香型.*","",product_name_wine)
    product_name_wine = re.sub("\W?原料.*", "", product_name_wine)
    product_name_wine = re.sub(".*饮", "", product_name_wine)
    product_name_wine = re.sub("高[梁柴]", "高粱", product_name_wine)
    product_name_wine = re.sub("^[锅鍋][头頭]", "二锅头", product_name_wine)
    product_name_wine = re.sub("双江", "双沟", product_name_wine)
    product_name_wine = re.sub("红燥", "红耀", product_name_wine)
    product_name_wine = re.sub("三锅头", "二锅头", product_name_wine)
    product_name_wine = re.sub("^京二锅头", "北京二锅头", product_name_wine)
    product_name_wine = re.sub("工子", "王子", product_name_wine)
    product_name_wine = re.sub("老白[千子]", "老白干", product_name_wine)
    product_name_wine = re.sub("[马岛鸟]河", "乌河", product_name_wine)
    product_name_wine = re.sub("唯台", "雌台", product_name_wine)
    product_name_wine = re.sub("黄州王子", "贵州王子", product_name_wine)
    product_name_wine = re.sub("漏窖", "湄窖", product_name_wine)
    product_name_wine = re.sub("菜台镇", "茅台镇", product_name_wine)
    product_name_wine = re.sub("杜庆", "杜康", product_name_wine)
    product_name_wine = re.sub("绵桑", "绵柔", product_name_wine)
    product_name_wine = re.sub("測阳河", "浏阳河", product_name_wine)
    product_name_wine = re.sub("脚酒", "御酒", product_name_wine)
    product_name_wine = re.sub("天津大直活", "天津大直沽", product_name_wine)
    product_name_wine = re.sub("全粮川", "金粮川", product_name_wine)
    product_name_wine = re.sub("金泌古", "金沙古", product_name_wine)

    product_name_wine = re.sub("^\w+认准", "", product_name_wine)

    product_name_wine = re.sub("^\d+[mM][lL]", "", product_name_wine)
    product_name_wine = re.sub("^\w?\W+", "", product_name_wine)
    product_name_wine = re.sub("[^\)\w]$", "", product_name_wine)
    product_name_wine_split = re.split(":", product_name_wine)

    if len(product_name_wine_split[0]) > 2:
        product_name_wine = product_name_wine_split[0]
    if len(product_name_wine) <= 1:
        product_name_wine = "不分"
    if product_name_wine != "不分" and len(re.compile("[酒曲]").findall(product_name_wine)) == 0 :
        product_name_wine += "酒"

    if taste != "不分" and product_name_wine != "不分":
        product_name = product_name_wine + "，" + taste
    elif taste == "不分":
        product_name = product_name_wine
    elif product_name_wine == "不分":
        product_name = taste + "白酒"

    taste = get_taste_type(datasorted)
    taste = re.sub("·", "", taste)
    type = get_type([[product_name,],])
    degree = get_degree(dataprocessed, datasorted)

    result_dict['info1'] = degree
    result_dict['info2'] = type
    result_dict['info3'] = taste
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    real_use_num = 3
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = ""
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_2\149-速冻食品'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3039104"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_299(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)